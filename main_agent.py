import os
import logging
from typing import Optional, Tuple
import torch
from config_loader import ConfigLoader
from persona_processor import PersonaProcessor
from retrieval_module import RetrievalModule
from llm_handler import LLMHandler

class CharacterBasedAgent:
    def __init__(self):
        """Initialize the character-based agent."""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.config_loader = ConfigLoader()
        if not self.config_loader.load_main_config():
            raise RuntimeError("Failed to load main configuration")
            
        self.persona_processor = PersonaProcessor(self.config_loader)
        self.retrieval_module = RetrievalModule(self.config_loader)
        self.llm_handler = LLMHandler(self.config_loader)
        
        # State
        self.current_character = None
        self.current_persona_chunks = []
        self.current_persona_embeddings = []
        
    def cleanup(self):
        """Clean up all components to prevent memory leaks"""
        try:
            if hasattr(self.persona_processor, 'cleanup'):
                self.persona_processor.cleanup()
            
            if hasattr(self.llm_handler, 'cleanup'):
                self.llm_handler.cleanup()
            
            # Clear state
            self.current_character = None
            self.current_persona_chunks = []
            self.current_persona_embeddings = []
            
            self.logger.info("CharacterBasedAgent cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during CharacterBasedAgent cleanup: {e}")
        
    def list_available_characters(self) -> list:
        """Get list of available characters.
        
        Returns:
            list: List of character names
        """
        return self.config_loader.get_available_characters()
        
    def load_character(self, character_name: str) -> bool:
        """Load a character's configuration and persona.
        
        Args:
            character_name (str): Name of the character to load
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load character config
            if not self.config_loader.load_character_config(character_name):
                self.logger.error(f"Failed to load config for character: {character_name}")
                return False
                
            # Get persona file path
            persona_file = self.config_loader.get_config('persona_file')
            if not persona_file:
                self.logger.error(f"No persona file specified for character: {character_name}")
                return False
                
            # Process persona document
            result = self.persona_processor.process_persona(persona_file)
            if not result:
                self.logger.error(f"Failed to process persona for character: {character_name}")
                return False
                
            self.current_character = character_name
            self.current_persona_chunks, self.current_persona_embeddings = result
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading character {character_name}: {e}")
            return False
            
    def reinitialize_llm_handler(self) -> bool:
        """Reinitialize the LLM handler with updated configuration/API key.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.llm_handler.reinitialize_with_new_api_key()
        except Exception as e:
            self.logger.error(f"Error reinitializing LLM handler: {e}")
            return False
            
    def generate_story_and_image(
        self,
        story_prompt: str
    ) -> Tuple[str, str, str, int, int]:
        """Generate a story and image prompt based on user input.
        
        Args:
            story_prompt (str): User's story idea
            
        Returns:
            Tuple[str, str, str, int, int]: Generated story, image prompt, model name, input tokens, output tokens
        """
        if not self.current_character or len(self.current_persona_chunks) == 0 or len(self.current_persona_embeddings) == 0:
            return "Error: No character loaded", "Error: No character loaded", "unknown", 0, 0
            
        try:
            # Get query embedding
            query_embedding = self.persona_processor.get_embeddings([story_prompt])[0]
            if query_embedding is None:
                return "Error: Failed to create query embedding", "Error: Failed to create query embedding", "unknown", 0, 0
                
            # Get relevant context
            context = self.retrieval_module.get_relevant_context(
                story_prompt,
                query_embedding,
                self.current_persona_embeddings,
                self.current_persona_chunks
            )
            
            # Format context for LLM
            persona_context = self.retrieval_module.format_context_for_llm(context)
            
            # Get image prompt guidelines
            image_guidelines = "\n".join(context.get('style', []))
            
            # Generate story and image prompt
            result = self.llm_handler.generate_story_and_image_prompt(
                story_prompt,
                persona_context,
                image_guidelines,
                self.current_character
            )
            
            return result.story, result.image_prompt, result.model_name, result.input_tokens, result.output_tokens
            
        except Exception as e:
            error_msg = f"Error generating content: {str(e)}"
            self.logger.error(error_msg)
            return error_msg, error_msg, "unknown", 0, 0

    def generate_image(self, image_prompt: str, quality: str = "high", size: str = "1024x1024") -> str:
        """Generate an image from the given prompt using Gemini's image generation capabilities.
        
        Args:
            image_prompt (str): The prompt for image generation
            quality (str): Quality setting (standard, high, ultra)
            size (str): Image size (512x512, 1024x1024, 1024x1792)
            
        Returns:
            str: Base64 encoded image data or error message
        """
        try:
            # Use LLM handler to generate image
            result = self.llm_handler.generate_image(image_prompt, quality=quality, size=size)
            
            if result and hasattr(result, 'image_data'):
                return result.image_data
            else:
                raise Exception("No image data received from LLM handler")
                
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

def main():
    """Main entry point for the character-based agent."""
    print(f"\n{'='*30}\n   Character-Based Story & Image Prompt Agent   \n{'='*30}")
    
    # Check for CUDA
    if not torch.cuda.is_available():
        print("WARNING: CUDA (GPU) not available. CPU will be used.")
    else:
        print(f"CUDA available. PyTorch using GPU: {torch.cuda.get_device_name(0)}")
        
    try:
        # Initialize agent
        agent = CharacterBasedAgent()
        
        # List available characters
        characters = agent.list_available_characters()
        if not characters:
            print("No characters found. Please add character configurations.")
            return
            
        print("\nAvailable characters:")
        for i, char in enumerate(characters, 1):
            print(f"{i}. {char}")
            
        # Select character
        while True:
            try:
                choice = int(input("\nSelect a character (number): "))
                if 1 <= choice <= len(characters):
                    selected_character = characters[choice - 1]
                    break
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
                
        # Load character
        print(f"\nLoading character: {selected_character}")
        if not agent.load_character(selected_character):
            print("Failed to load character. Exiting.")
            return
            
        print("\nCharacter loaded successfully!")
        print("\nEnter your story idea (or 'exit' to quit):")
        
        # Main interaction loop
        while True:
            story_prompt = input("\nYou: ").strip()
            if story_prompt.lower() == 'exit':
                break
                
            if not story_prompt:
                continue
                
            print("\nGenerating story and image prompt...")
            story, image_prompt, model_name, input_tokens, output_tokens = agent.generate_story_and_image(story_prompt)
            
            print("\nGenerated Story:")
            print("-" * 20)
            print(story)
            print("-" * 20)
            
            if image_prompt and not image_prompt.startswith("Error"):
                print("\nImage Generation Prompt:")
                print("-" * 20)
                print(image_prompt)
                print("-" * 20)
                
    except Exception as e:
        print(f"An error occurred: {e}")
        
    print("\nGoodbye!")
    
if __name__ == "__main__":
    main() 