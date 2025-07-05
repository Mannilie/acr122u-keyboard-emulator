import json
import os

class Configuration:
    DEFAULT_CONFIG = {
      "prefix": "",
      "suffix": "\n",
      "log_level": "INFO",
      "format": "HEX"
    }
    
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG
        else:
            # Create default config
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)