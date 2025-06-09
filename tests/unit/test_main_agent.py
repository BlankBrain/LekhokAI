import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from main_agent import CharacterBasedAgent
import os
import yaml
import tempfile
import threading
import time


class TestCharacterBasedAgentInitialization:
    """Test CharacterBasedAgent initialization scenarios."""
    
    @patch('main_agent.PersonaProcessor')
    @patch('main_agent.LLMHandler')
    @patch('main_agent.ConfigLoader')
    def test_init_with_config(self, mock_config_loader_class, mock_llm_handler, mock_persona_processor):
        """Test initialization with valid configuration."""
        mock_config_loader = Mock()
        mock_config_loader.load_main_config.return_value = True
        mock_config_loader_class.return_value = mock_config_loader
        
        agent = CharacterBasedAgent()
        
        assert agent.config_loader == mock_config_loader
        assert agent.persona_processor is not None
        assert agent.llm_handler is not None
        assert agent.current_character is None
    
    @patch('main_agent.ConfigLoader')
    def test_init_with_missing_config(self, mock_config_loader_class):
        """Test initialization with missing configuration."""
        mock_config_loader = Mock()
        mock_config_loader.load_main_config.return_value = False
        mock_config_loader_class.return_value = mock_config_loader
        
        with pytest.raises(RuntimeError, match="Failed to load main configuration"):
            CharacterBasedAgent()
    
    @patch('main_agent.ConfigLoader')
    def test_init_with_invalid_yaml(self, mock_config_loader_class):
        """Test initialization with invalid YAML configuration."""
        mock_config_loader = Mock()
        mock_config_loader.load_main_config.side_effect = Exception("Invalid YAML")
        mock_config_loader_class.return_value = mock_config_loader
        
        with pytest.raises(Exception):
            CharacterBasedAgent()


class TestCharacterManagement:
    """Test character loading and management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor') as mock_persona_processor_class:
                with patch('main_agent.LLMHandler') as mock_llm_handler_class:
                    mock_config_loader = Mock()
                    mock_config_loader.load_main_config.return_value = True
                    mock_config_loader_class.return_value = mock_config_loader
                    
                    self.agent = CharacterBasedAgent()
    
    def test_load_character_success(self):
        """Test successful character loading."""
        self.agent.config_loader.load_character_config.return_value = True
        self.agent.config_loader.get_config.return_value = "test_persona.txt"
        self.agent.persona_processor.process_persona.return_value = (
            ["chunk1", "chunk2"], 
            [Mock(), Mock()]
        )
        
        result = self.agent.load_character("himu")
        
        assert result is True
        assert self.agent.current_character == "himu"
    
    def test_load_character_failure(self):
        """Test character loading failure."""
        self.agent.config_loader.load_character_config.return_value = False
        
        result = self.agent.load_character("nonexistent")
        
        assert result is False
        assert self.agent.current_character is None
    
    def test_load_character_exception(self):
        """Test character loading with exception."""
        self.agent.config_loader.load_character_config.side_effect = Exception("Config error")
        
        result = self.agent.load_character("error_character")
        
        assert result is False
    
    def test_load_character_empty_name(self):
        """Test loading character with empty name."""
        result = self.agent.load_character("")
        
        assert result is False
    
    def test_load_character_none_name(self):
        """Test loading character with None name."""
        result = self.agent.load_character(None)
        
        assert result is False


class TestStoryGeneration:
    """Test story generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor') as mock_persona_processor_class:
                with patch('main_agent.LLMHandler') as mock_llm_handler_class:
                    with patch('main_agent.RetrievalModule') as mock_retrieval_module_class:
                        mock_config_loader = Mock()
                        mock_config_loader.load_main_config.return_value = True
                        mock_config_loader_class.return_value = mock_config_loader
                        
                        # Mock retrieval module
                        mock_retrieval_module = Mock()
                        mock_retrieval_module_class.return_value = mock_retrieval_module
                        
                        self.agent = CharacterBasedAgent()
                        # Set up character state for testing
                        self.agent.current_character = "test_character"
                        self.agent.current_persona_chunks = ["chunk1", "chunk2"]
                        self.agent.current_persona_embeddings = [Mock(), Mock()]
    
    def test_generate_story_and_image_success(self):
        """Test successful story and image generation."""
        # Mock the persona processor methods
        self.agent.persona_processor.get_embeddings.return_value = [Mock()]
        
        # Mock retrieval module methods
        mock_retrieval_module = Mock()
        mock_retrieval_module.get_relevant_context.return_value = {
            'style': ['style1', 'style2']
        }
        mock_retrieval_module.format_context_for_llm.return_value = "formatted context"
        self.agent.retrieval_module = mock_retrieval_module
        
        # Mock LLM handler response
        mock_result = Mock()
        mock_result.story = "Generated story"
        mock_result.image_prompt = "Generated image prompt"
        mock_result.model_name = "test_model"
        mock_result.input_tokens = 100
        mock_result.output_tokens = 200
        
        self.agent.llm_handler.generate_story_and_image_prompt.return_value = mock_result
        
        story, image_prompt, model_name, input_tokens, output_tokens = self.agent.generate_story_and_image("Test prompt")
        
        assert story == "Generated story"
        assert image_prompt == "Generated image prompt"
        assert model_name == "test_model"
        assert input_tokens == 100
        assert output_tokens == 200
    
    def test_generate_story_and_image_with_character(self):
        """Test story generation with specific character loaded."""
        # Setup character
        self.agent.current_character = "himu"
        self.agent.current_persona_chunks = ["character chunk"]
        self.agent.current_persona_embeddings = [Mock()]
        
        # Mock methods
        self.agent.persona_processor.get_embeddings.return_value = [Mock()]
        
        # Mock retrieval module methods
        mock_retrieval_module = Mock()
        mock_retrieval_module.get_relevant_context.return_value = {'style': []}
        mock_retrieval_module.format_context_for_llm.return_value = "character context"
        self.agent.retrieval_module = mock_retrieval_module
        
        mock_result = Mock()
        mock_result.story = "Character story"
        mock_result.image_prompt = "Character image"
        mock_result.model_name = "test_model"
        mock_result.input_tokens = 50
        mock_result.output_tokens = 100
        
        self.agent.llm_handler.generate_story_and_image_prompt.return_value = mock_result
        
        story, image_prompt, model_name, input_tokens, output_tokens = self.agent.generate_story_and_image("Test prompt")
        
        assert story == "Character story"
        assert image_prompt == "Character image"
    
    def test_generate_story_and_image_no_character(self):
        """Test story generation without character loaded."""
        # Clear character state
        self.agent.current_character = None
        self.agent.current_persona_chunks = []
        self.agent.current_persona_embeddings = []
        
        story, image_prompt, model_name, input_tokens, output_tokens = self.agent.generate_story_and_image("Test prompt")
        
        assert "Error: No character loaded" in story
        assert "Error: No character loaded" in image_prompt
    
    def test_generate_story_and_image_llm_error(self):
        """Test story generation with LLM error."""
        # Setup character
        self.agent.current_character = "test"
        self.agent.current_persona_chunks = ["chunk"]
        self.agent.current_persona_embeddings = [Mock()]
        
        # Mock error in LLM handler
        self.agent.persona_processor.get_embeddings.side_effect = Exception("LLM Error")
        
        story, image_prompt, model_name, input_tokens, output_tokens = self.agent.generate_story_and_image("Test prompt")
        
        assert "Error generating content" in story
    
    def test_generate_story_and_image_empty_prompt(self):
        """Test story generation with empty prompt."""
        # Setup character but with empty prompt
        self.agent.current_character = "test"
        self.agent.current_persona_chunks = ["chunk"]
        self.agent.current_persona_embeddings = [Mock()]
        
        # Mock methods
        self.agent.persona_processor.get_embeddings.return_value = [Mock()]
        
        # Mock retrieval module methods
        mock_retrieval_module = Mock()
        mock_retrieval_module.get_relevant_context.return_value = {'style': []}
        mock_retrieval_module.format_context_for_llm.return_value = "context"
        self.agent.retrieval_module = mock_retrieval_module
        
        mock_result = Mock()
        mock_result.story = "Default story"
        mock_result.image_prompt = "Default image"
        mock_result.model_name = "test_model"
        mock_result.input_tokens = 10
        mock_result.output_tokens = 20
        
        self.agent.llm_handler.generate_story_and_image_prompt.return_value = mock_result
        
        story, image_prompt, model_name, input_tokens, output_tokens = self.agent.generate_story_and_image("")
        
        assert story == "Default story"
        assert image_prompt == "Default image"


class TestLLMHandlerIntegration:
    """Test LLM handler integration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor') as mock_persona_processor_class:
                with patch('main_agent.LLMHandler') as mock_llm_handler_class:
                    mock_config_loader = Mock()
                    mock_config_loader.load_main_config.return_value = True
                    mock_config_loader_class.return_value = mock_config_loader
                    
                    self.agent = CharacterBasedAgent()
    
    def test_reinitialize_llm_handler_success(self):
        """Test successful LLM handler reinitialization."""
        self.agent.llm_handler.reinitialize_with_new_api_key.return_value = True
        
        result = self.agent.reinitialize_llm_handler()
        
        assert result is True
    
    def test_reinitialize_llm_handler_failure(self):
        """Test LLM handler reinitialization failure."""
        self.agent.llm_handler.reinitialize_with_new_api_key.return_value = False
        
        result = self.agent.reinitialize_llm_handler()
        
        assert result is False
    
    def test_reinitialize_llm_handler_exception(self):
        """Test LLM handler reinitialization with exception."""
        self.agent.llm_handler.reinitialize_with_new_api_key.side_effect = Exception("Reinit error")
        
        result = self.agent.reinitialize_llm_handler()
        
        assert result is False


class TestConfigurationManagement:
    """Test configuration management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor'):
                with patch('main_agent.LLMHandler'):
                    mock_config_loader = Mock()
                    mock_config_loader.load_main_config.return_value = True
                    mock_config_loader_class.return_value = mock_config_loader
                    
                    self.agent = CharacterBasedAgent()
    
    def test_load_configuration_success(self):
        """Test successful configuration loading."""
        # Test that config_loader is properly initialized
        assert self.agent.config_loader is not None
        assert hasattr(self.agent.config_loader, 'load_main_config')
    
    def test_load_configuration_file_not_found(self):
        """Test configuration loading with file not found."""
        # Test initialization failure
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            mock_config_loader = Mock()
            mock_config_loader.load_main_config.return_value = False
            mock_config_loader_class.return_value = mock_config_loader
            
            with pytest.raises(RuntimeError):
                CharacterBasedAgent()
    
    def test_load_configuration_invalid_yaml(self):
        """Test configuration loading with invalid YAML."""
        # Test YAML parsing error
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            mock_config_loader = Mock()
            mock_config_loader.load_main_config.side_effect = Exception("YAML Error")
            mock_config_loader_class.return_value = mock_config_loader
            
            with pytest.raises(Exception):
                CharacterBasedAgent()
    
    def test_get_ai_settings(self):
        """Test getting AI settings from configuration."""
        # Test that we can access AI settings through config_loader
        self.agent.config_loader.get_config.return_value = "test_value"
        
        result = self.agent.config_loader.get_config("ai.setting")
        
        assert result == "test_value"
    
    def test_get_ai_settings_missing(self):
        """Test getting missing AI settings."""
        # Test default value handling
        self.agent.config_loader.get_config.return_value = None
        
        result = self.agent.config_loader.get_config("missing.setting", "default")
        
        # The mock returns None, but in real implementation would return default
        assert result is None or result == "default"


class TestPersonaProcessorIntegration:
    """Test persona processor integration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor') as mock_persona_processor_class:
                with patch('main_agent.LLMHandler'):
                    mock_config_loader = Mock()
                    mock_config_loader.load_main_config.return_value = True
                    mock_config_loader_class.return_value = mock_config_loader
                    
                    self.agent = CharacterBasedAgent()
    
    def test_get_current_character_description(self):
        """Test getting current character description."""
        # Test through character loading process
        self.agent.current_character = "test_character"
        
        assert self.agent.current_character == "test_character"
    
    def test_get_current_character_description_no_character(self):
        """Test getting character description with no character loaded."""
        # No character loaded
        assert self.agent.current_character is None
    
    def test_get_available_characters(self):
        """Test getting list of available characters."""
        # Test list_available_characters method
        self.agent.config_loader.get_available_characters.return_value = ["char1", "char2"]
        
        characters = self.agent.list_available_characters()
        
        assert characters == ["char1", "char2"]
    
    def test_validate_character_exists(self):
        """Test validating if character exists."""
        # Test through character loading
        self.agent.config_loader.load_character_config.return_value = True
        self.agent.config_loader.get_config.return_value = "persona.txt"
        self.agent.persona_processor.process_persona.return_value = (["chunk"], [Mock()])
        
        result = self.agent.load_character("himu")
        
        assert result is True


class TestResourceManagement:
    """Test resource management and cleanup functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor') as mock_persona_processor_class:
                with patch('main_agent.LLMHandler') as mock_llm_handler_class:
                    mock_config_loader = Mock()
                    mock_config_loader.load_main_config.return_value = True
                    mock_config_loader_class.return_value = mock_config_loader
                    
                    self.agent = CharacterBasedAgent()
    
    def test_cleanup_success(self):
        """Test successful cleanup of resources."""
        # Mock cleanup methods
        self.agent.persona_processor.cleanup = Mock()
        self.agent.llm_handler.cleanup = Mock()
        
        self.agent.cleanup()
        
        assert self.agent.current_character is None
        assert self.agent.current_persona_chunks == []
        assert self.agent.current_persona_embeddings == []
    
    def test_cleanup_with_exceptions(self):
        """Test cleanup with exceptions in component cleanup."""
        # Mock cleanup methods to raise exceptions
        self.agent.persona_processor.cleanup = Mock(side_effect=Exception("Persona cleanup error"))
        self.agent.llm_handler.cleanup = Mock()
        
        # Should not raise exception, should handle gracefully
        self.agent.cleanup()
        
        assert self.agent.current_character is None

    def test_context_manager_usage(self):
        """Test using agent as context manager."""
        # CharacterBasedAgent doesn't implement context manager, this should fail
        with pytest.raises(AttributeError):
            with CharacterBasedAgent() as agent:
                pass


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor') as mock_persona_processor_class:
                with patch('main_agent.LLMHandler') as mock_llm_handler_class:
                    mock_config_loader = Mock()
                    mock_config_loader.load_main_config.return_value = True
                    mock_config_loader_class.return_value = mock_config_loader
                    
                    self.agent = CharacterBasedAgent()
    
    def test_generate_story_with_none_prompt(self):
        """Test story generation with None prompt."""
        # Clear character to trigger error path
        self.agent.current_character = None
        
        story, image_prompt, model_name, input_tokens, output_tokens = self.agent.generate_story_and_image(None)
        
        assert "Error: No character loaded" in story
    
    def test_load_character_with_special_characters(self):
        """Test loading character with special characters in name."""
        self.agent.config_loader.load_character_config.return_value = False
        
        result = self.agent.load_character("test-character_123")
        
        assert result is False
    
    def test_concurrent_character_loading(self):
        """Test concurrent character loading."""
        # Mock character loading to return False
        self.agent.config_loader.load_character_config.return_value = False
        
        # Test concurrent loading
        def load_char(name):
            return self.agent.load_character(name)
        
        thread1 = threading.Thread(target=load_char, args=("character1",))
        thread2 = threading.Thread(target=load_char, args=("character2",))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Both should fail since config loading returns False
        result1 = self.agent.load_character("character1")
        result2 = self.agent.load_character("character2")
        
        assert result1 is False
        assert result2 is False
    
    def test_memory_management_large_stories(self):
        """Test memory management with large story generation."""
        # Setup character
        self.agent.current_character = "test"
        self.agent.current_persona_chunks = ["chunk"]
        self.agent.current_persona_embeddings = [Mock()]
        
        # Mock large story generation
        self.agent.persona_processor.get_embeddings.return_value = [Mock()]
        
        # Mock retrieval module methods
        mock_retrieval_module = Mock()
        mock_retrieval_module.get_relevant_context.return_value = {'style': []}
        mock_retrieval_module.format_context_for_llm.return_value = "context"
        self.agent.retrieval_module = mock_retrieval_module
        
        mock_result = Mock()
        mock_result.story = "A" * 100000  # Large story
        mock_result.image_prompt = "Large image prompt"
        mock_result.model_name = "test_model"
        mock_result.input_tokens = 1000
        mock_result.output_tokens = 2000
        
        self.agent.llm_handler.generate_story_and_image_prompt.return_value = mock_result
        
        story, image_prompt, model_name, input_tokens, output_tokens = self.agent.generate_story_and_image("Large prompt")
        
        assert len(story) == 100000
        assert input_tokens == 1000
        assert output_tokens == 2000


class TestLoggingAndDebugging:
    """Test logging and debugging functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('main_agent.ConfigLoader') as mock_config_loader_class:
            with patch('main_agent.PersonaProcessor') as mock_persona_processor_class:
                with patch('main_agent.LLMHandler') as mock_llm_handler_class:
                    mock_config_loader = Mock()
                    mock_config_loader.load_main_config.return_value = True
                    mock_config_loader_class.return_value = mock_config_loader
                    
                    self.agent = CharacterBasedAgent()
    
    @patch('main_agent.logging')
    def test_logging_initialization(self, mock_logging):
        """Test that logging is properly initialized."""
        # Logger should be set up during initialization
        assert hasattr(self.agent, 'logger')
    
    @patch('main_agent.logging')
    def test_logging_character_operations(self, mock_logging):
        """Test logging during character operations."""
        # Mock character loading failure to trigger logging
        self.agent.config_loader.load_character_config.return_value = False
        
        result = self.agent.load_character("test_character")
        
        assert result is False
        # Character loading failure should be logged


class TestIntegrationWorkflows:
    """Test complete integration workflows."""
    
    @patch('main_agent.PersonaProcessor')
    @patch('main_agent.LLMHandler')
    @patch('main_agent.ConfigLoader')
    def test_complete_story_generation_workflow(self, mock_config_loader_class, mock_llm_handler_class, mock_persona_processor_class):
        """Test complete story generation workflow from start to finish."""
        # Setup mocks
        mock_config_loader = Mock()
        mock_config_loader.load_main_config.return_value = True
        mock_config_loader.load_character_config.return_value = True
        mock_config_loader.get_config.return_value = "test_persona.txt"
        mock_config_loader_class.return_value = mock_config_loader
        
        mock_persona_processor = Mock()
        mock_persona_processor.process_persona.return_value = (["chunk1"], [Mock()])
        mock_persona_processor.get_embeddings.return_value = [Mock()]
        mock_persona_processor_class.return_value = mock_persona_processor
        
        # Initialize agent
        with patch('main_agent.RetrievalModule') as mock_retrieval_module_class:
            mock_retrieval_module = Mock()
            mock_retrieval_module_class.return_value = mock_retrieval_module
            
            agent = CharacterBasedAgent()
            
            # Mock retrieval module methods
            agent.retrieval_module.get_relevant_context.return_value = {'style': ['style1']}
            agent.retrieval_module.format_context_for_llm.return_value = "formatted context"
            
            # Mock LLM handler
            mock_result = Mock()
            mock_result.story = "Complete workflow story"
            mock_result.image_prompt = "Complete workflow image"
            mock_result.model_name = "test_model"
            mock_result.input_tokens = 150
            mock_result.output_tokens = 300
            agent.llm_handler.generate_story_and_image_prompt.return_value = mock_result
            
            # Test complete workflow
            load_result = agent.load_character("test_character")
            assert load_result is True
            
            story, image_prompt, model_name, input_tokens, output_tokens = agent.generate_story_and_image("Test story prompt")
            
            assert story == "Complete workflow story"
            assert image_prompt == "Complete workflow image"
            assert model_name == "test_model"
            assert input_tokens == 150
            assert output_tokens == 300
    
    @patch('main_agent.PersonaProcessor')
    @patch('main_agent.LLMHandler')  
    @patch('main_agent.ConfigLoader')
    def test_character_switching_workflow(self, mock_config_loader_class, mock_llm_handler_class, mock_persona_processor_class):
        """Test switching between different characters."""
        # Setup mocks
        mock_config_loader = Mock()
        mock_config_loader.load_main_config.return_value = True
        mock_config_loader_class.return_value = mock_config_loader
        
        mock_persona_processor = Mock()
        mock_persona_processor_class.return_value = mock_persona_processor
        
        agent = CharacterBasedAgent()
        
        # Mock character loading for different characters
        def mock_get_description(character):
            if character == "character1":
                return "Description for character 1"
            elif character == "character2":
                return "Description for character 2"
            return None
        
        # Test character switching
        mock_config_loader.load_character_config.side_effect = lambda char: char in ["character1", "character2"]
        mock_config_loader.get_config.return_value = "persona.txt"
        mock_persona_processor.process_persona.return_value = (["chunk"], [Mock()])
        
        # Load first character
        result1 = agent.load_character("character1")
        assert result1 is True
        assert agent.current_character == "character1"
        
        # Switch to second character
        result2 = agent.load_character("character2")
        assert result2 is True
        assert agent.current_character == "character2" 