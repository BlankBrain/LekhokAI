import os
import numpy as np
from typing import List, Tuple, Optional
import logging
from sentence_transformers import SentenceTransformer
import torch
import json
from pathlib import Path
import gc

class PersonaProcessor:
    def __init__(self, config_loader):
        """Initialize the persona processor.
        
        Args:
            config_loader: Instance of ConfigLoader for accessing configuration
        """
        self.config_loader = config_loader
        self.logger = logging.getLogger(__name__)
        self.embedding_model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.cache_dir = self.config_loader.get_config('directories.cache', 'cache')
        self._initialize_embedding_model()
        
    def _initialize_embedding_model(self) -> bool:
        """Initialize the sentence transformer model for embeddings.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            model_name = self.config_loader.get_config('retrieval.embedding_model')
            self.embedding_model = SentenceTransformer(model_name, device=self.device)
            return True
        except Exception as e:
            self.logger.error(f"Error initializing embedding model: {e}")
            return False
            
    def _get_cache_path(self, persona_file: str) -> str:
        """Get the cache file path for a persona's embeddings.
        
        Args:
            persona_file (str): Path to the persona file
            
        Returns:
            str: Path to the cache file
        """
        cache_dir = Path(self.cache_dir)
        cache_dir.mkdir(exist_ok=True)
        return str(cache_dir / f"{Path(persona_file).stem}_embeddings.json")
        
    def _load_from_cache(self, cache_path: str) -> Optional[Tuple[List[str], List[np.ndarray]]]:
        """Load embeddings from cache if available.
        
        Args:
            cache_path (str): Path to the cache file
            
        Returns:
            Optional[Tuple[List[str], List[np.ndarray]]]: Tuple of (chunks, embeddings) if found, None otherwise
        """
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chunks = data['chunks']
                    embeddings = [np.array(emb) for emb in data['embeddings']]
                    return chunks, embeddings
        except Exception as e:
            self.logger.warning(f"Error loading from cache: {e}")
        return None
        
    def _save_to_cache(self, cache_path: str, chunks: List[str], embeddings: List[np.ndarray]) -> bool:
        """Save embeddings to cache.
        
        Args:
            cache_path (str): Path to the cache file
            chunks (List[str]): List of text chunks
            embeddings (List[np.ndarray]): List of embeddings
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            data = {
                'chunks': chunks,
                'embeddings': [emb.tolist() for emb in embeddings]
            }
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            self.logger.warning(f"Error saving to cache: {e}")
            return False
            
    def chunk_text(self, text: str, chunk_size: int = 700, overlap: int = 120) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text (str): Text to chunk
            chunk_size (int): Size of each chunk
            overlap (int): Number of characters to overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= len(text):
                break
            start += (chunk_size - overlap)
            
        return chunks
        
    def process_persona(self, persona_file: str) -> Optional[Tuple[List[str], List[np.ndarray]]]:
        """Process a persona document, creating chunks and embeddings.
        
        Args:
            persona_file (str): Path to the persona document
            
        Returns:
            Optional[Tuple[List[str], List[np.ndarray]]]: Tuple of (chunks, embeddings) if successful, None otherwise
        """
        try:
            # Always resolve persona_file to the correct absolute path in personas directory
            personas_dir = self.config_loader.get_config('directories.personas', 'personas')
            # If persona_file is not an absolute path and does not already include the directory, prepend it
            if not os.path.isabs(persona_file) and not persona_file.startswith(personas_dir):
                persona_file = os.path.join(personas_dir, persona_file)

            # Check cache first
            cache_path = self._get_cache_path(persona_file)
            cached_data = self._load_from_cache(cache_path)
            if cached_data:
                return cached_data
                
            # Load and process file
            with open(persona_file, 'r', encoding='utf-8') as f:
                text = f.read()
                
            chunks = self.chunk_text(text)
            if not chunks:
                self.logger.error("No chunks created from persona file")
                return None
                
            # Create embeddings
            if not self.embedding_model:
                self.logger.error("Embedding model not initialized")
                return None
                
            embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
            
            # Cache results if enabled
            if self.config_loader.get_config('app.cache_embeddings', True):
                self._save_to_cache(cache_path, chunks, embeddings)
                
            return chunks, embeddings
            
        except Exception as e:
            self.logger.error(f"Error processing persona file: {e}")
            return None
            
    def get_embeddings(self, texts: List[str]) -> Optional[List[np.ndarray]]:
        """Get embeddings for a list of texts.
        
        Args:
            texts (List[str]): List of texts to embed
            
        Returns:
            Optional[List[np.ndarray]]: List of embeddings if successful, None otherwise
        """
        try:
            if not self.embedding_model:
                self.logger.error("Embedding model not initialized")
                return None
                
            return self.embedding_model.encode(texts, show_progress_bar=False)
        except Exception as e:
            self.logger.error(f"Error creating embeddings: {e}")
            return None

    def cleanup(self):
        """Clean up resources to prevent memory leaks"""
        try:
            if self.embedding_model is not None:
                # Move model to CPU to free GPU memory
                if hasattr(self.embedding_model, 'to'):
                    self.embedding_model = self.embedding_model.to('cpu')
                
                # Clear the model reference
                del self.embedding_model
                self.embedding_model = None
                
                # Force garbage collection
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                gc.collect()
                
                self.logger.info("PersonaProcessor cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during PersonaProcessor cleanup: {e}") 