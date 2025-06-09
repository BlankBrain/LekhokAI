import numpy as np
from typing import List, Dict, Any, Optional
import logging
from sentence_transformers import CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
import torch

class RetrievalModule:
    def __init__(self, config_loader):
        """Initialize the retrieval module.
        
        Args:
            config_loader: Instance of ConfigLoader for accessing configuration
        """
        self.config_loader = config_loader
        self.logger = logging.getLogger(__name__)
        self.reranker_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_reranker()
        
    def _initialize_reranker(self) -> bool:
        """Initialize the cross-encoder model for reranking.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            model_name = self.config_loader.get_config('retrieval.reranker_model')
            if not model_name:
                self.logger.info("No reranker model specified; reranking will be skipped.")
                self.reranker_model = None
                return True
            self.reranker_model = CrossEncoder(model_name, device=self.device)
            return True
        except Exception as e:
            self.logger.error(f"Error initializing reranker model: {e}")
            return False
            
    def _get_retrieval_params(self, query_type: str) -> Dict[str, Any]:
        """Get retrieval parameters for a specific query type.
        
        Args:
            query_type (str): Type of query (topic, style, timeline)
            
        Returns:
            Dict[str, Any]: Dictionary of retrieval parameters
        """
        params = self.config_loader.get_config(f'retrieval_params.{query_type}', {})
        return {
            'initial_retrieval': params.get('initial_retrieval', 7),
            'final_retrieval': params.get('final_retrieval', 3),
            'similarity_threshold': params.get('similarity_threshold', 0.20)
        }
        
    def find_relevant_chunks(
        self,
        query_embedding: np.ndarray,
        doc_chunk_embeddings: List[np.ndarray],
        doc_chunks_text: List[str],
        query_type: str = "topic"
    ) -> List[Dict[str, Any]]:
        """Find relevant chunks using initial retrieval and reranking.
        
        Args:
            query_embedding (np.ndarray): Query embedding
            doc_chunk_embeddings (List[np.ndarray]): Document chunk embeddings
            doc_chunks_text (List[str]): Document chunk texts
            query_type (str): Type of query for parameter selection
            
        Returns:
            List[Dict[str, Any]]: List of relevant chunks with scores
        """
        if query_embedding is None or len(query_embedding) == 0 or len(doc_chunk_embeddings) == 0 or len(doc_chunks_text) == 0:
            return []
            
        params = self._get_retrieval_params(query_type)
        
        # Initial retrieval using cosine similarity
        initial_scores = []
        for i, chunk_emb in enumerate(doc_chunk_embeddings):
            if chunk_emb is not None and chunk_emb.any():
                try:
                    sim = cosine_similarity(
                        query_embedding.reshape(1, -1),
                        chunk_emb.reshape(1, -1)
                    )[0][0]
                    if sim >= params['similarity_threshold']:
                        initial_scores.append({
                            'text': doc_chunks_text[i],
                            'initial_score': sim
                        })
                except Exception as e:
                    self.logger.warning(f"Error calculating similarity for chunk {i}: {e}")
                    
        # Sort by initial score and take top N
        initial_scores.sort(key=lambda x: x['initial_score'], reverse=True)
        top_chunks = initial_scores[:params['initial_retrieval']]
        
        if not top_chunks or not self.reranker_model:
            return top_chunks
            
        # Rerank using cross-encoder
        try:
            # Create pairs of query text and chunk text for reranking
            sentence_pairs = [[query_type, chunk['text']] for chunk in top_chunks]
            rerank_scores = self.reranker_model.predict(sentence_pairs, show_progress_bar=False)
            
            # Add rerank scores
            for i, chunk in enumerate(top_chunks):
                chunk['rerank_score'] = float(rerank_scores[i])
                
            # Sort by rerank score and take top N
            top_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
            return top_chunks[:params['final_retrieval']]
            
        except Exception as e:
            self.logger.error(f"Error during reranking: {e}")
            return top_chunks[:params['final_retrieval']]
            
    def get_relevant_context(
        self,
        query_text: str,
        query_embedding: np.ndarray,
        doc_chunk_embeddings: List[np.ndarray],
        doc_chunks_text: List[str],
        query_types: List[str] = ["topic", "style", "timeline"]
    ) -> Dict[str, List[str]]:
        """Get relevant context for different query types.
        
        Args:
            query_text (str): Original query text
            query_embedding (np.ndarray): Query embedding
            doc_chunk_embeddings (List[np.ndarray]): Document chunk embeddings
            doc_chunks_text (List[str]): Document chunk texts
            query_types (List[str]): Types of queries to process
            
        Returns:
            Dict[str, List[str]]: Dictionary of relevant chunks by query type
        """
        context = {}
        
        for query_type in query_types:
            chunks = self.find_relevant_chunks(
                query_embedding,
                doc_chunk_embeddings,
                doc_chunks_text,
                query_type
            )
            context[query_type] = [chunk['text'] for chunk in chunks]
            
        return context
        
    def format_context_for_llm(self, context: Dict[str, List[str]]) -> str:
        """Format context for LLM input.
        
        Args:
            context (Dict[str, List[str]]): Context dictionary by query type
            
        Returns:
            str: Formatted context string
        """
        sections = []
        
        if 'topic' in context and context['topic']:
            sections.append("Topic-Relevant Information:")
            sections.extend(context['topic'])
            
        if 'style' in context and context['style']:
            sections.append("\nStyle Guidelines:")
            sections.extend(context['style'])
            
        if 'timeline' in context and context['timeline']:
            sections.append("\nTimeline Information:")
            sections.extend(context['timeline'])
            
        return "\n\n".join(sections) 