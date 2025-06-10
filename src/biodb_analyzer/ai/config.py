from typing import Dict, Any
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OllamaConfig:
    """
    Configuration for Ollama integration
    """
    def __init__(self, config_file: str = "ollama_config.json"):
        """
        Initialize the configuration
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.default_config = {
            "model": "mistral",
            "api_url": "http://localhost:11434",
            "temperature": 0.7,
            "max_tokens": 2000,
            "system_prompt": """You are a bioinformatics database analyst. Your role is to analyze scientific databases and provide insights.
            Focus on biological and genomic data patterns, relationships, and potential research questions.
            Provide clear, structured responses with scientific context."""
        }
        
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults
        
        Returns:
            Configuration dictionary
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Validate config
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            return self.default_config
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return self.default_config

    def save_config(self) -> None:
        """
        Save current configuration to file
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration
        
        Returns:
            Configuration dictionary
        """
        return self.config

    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Set new configuration
        
        Args:
            config: New configuration dictionary
        """
        self.config = config
        self.save_config()

    def get_model(self) -> str:
        """
        Get the current model
        
        Returns:
            Model name
        """
        return self.config.get("model", "mistral")

    def get_api_url(self) -> str:
        """
        Get the API URL
        
        Returns:
            API URL
        """
        return self.config.get("api_url", "http://localhost:11434")
