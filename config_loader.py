import os
import yaml
from typing import Dict, Any, Optional
import logging

class ConfigLoader:
    def __init__(self, config_path: str = "agent_config.yaml"):
        """Initialize the configuration loader.
        
        Args:
            config_path (str): Path to the main configuration file
        """
        self.config_path = config_path
        self.main_config: Dict[str, Any] = {}
        self.character_config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
    def load_main_config(self) -> bool:
        """Load the main configuration file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.main_config = yaml.safe_load(f) or {}
            return True
        except Exception as e:
            self.logger.error(f"Error loading main config: {e}")
            return False
            
    def load_character_config(self, character_name: str) -> bool:
        """Load a character-specific configuration file.
        
        Args:
            character_name (str): Name of the character to load config for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_dir = self.main_config.get('directories', {}).get('character_configs', 'character_configs')
            # Try different possible filenames
            possible_filenames = [
                f"{character_name}.yaml",
                f"{character_name}_config.yaml",
                f"{character_name}__config.yaml"
            ]
            
            for filename in possible_filenames:
                config_path = os.path.join(config_dir, filename)
                if os.path.exists(config_path):
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self.character_config = yaml.safe_load(f)
                    return True
                    
            self.logger.error(f"No configuration file found for character: {character_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error loading character config for {character_name}: {e}")
            return False
            
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value, checking character config first, then main config.
        
        Args:
            key (str): Configuration key to retrieve
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value or default
        """
        # Split key by dots for nested access
        keys = key.split('.')
        
        # Try character config first
        value = self.character_config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
                
        if value is not None:
            return value
            
        # Try main config if not found in character config
        value = self.main_config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def get_available_characters(self) -> list:
        """Get list of available characters based on config files.
        
        Returns:
            list: List of character names
        """
        try:
            config_dir = self.main_config.get('directories', {}).get('character_configs', 'character_configs')
            if not os.path.exists(config_dir):
                return []
                
            characters = []
            for file in os.listdir(config_dir):
                if file.endswith('.yaml'):
                    # Remove all possible suffixes to get the base character name
                    character_name = file.replace('_config.yaml', '').replace('__config.yaml', '').replace('.yaml', '')
                    if character_name not in characters:
                        characters.append(character_name)
            return characters
        except Exception as e:
            self.logger.error(f"Error getting available characters: {e}")
            return []
            
    def validate_config(self) -> bool:
        """Validate the loaded configurations.
        
        Returns:
            bool: True if valid, False otherwise
        """
        required_main_keys = ['llm', 'retrieval', 'directories']
        required_character_keys = ['name', 'persona_file']
        
        # Check main config
        for key in required_main_keys:
            if key not in self.main_config:
                self.logger.error(f"Missing required main config key: {key}")
                return False
                
        # Check character config if loaded
        if self.character_config:
            for key in required_character_keys:
                if key not in self.character_config:
                    self.logger.error(f"Missing required character config key: {key}")
                    return False
                    
        return True 