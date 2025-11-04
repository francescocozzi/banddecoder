#!/usr/bin/env python3
"""
Configuration Loader
Loads and validates YAML configuration
"""

import yaml
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = config_path
        self.config = None
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.validate()
        return self.config
    
    def validate(self):
        """Validate configuration"""
        required_keys = ['system', 'hardware', 'radios', 'bands', 'relays']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
        
        # Validate bands
        if len(self.config['bands']) != 6:
            raise ValueError("Configuration must define exactly 6 bands")
        
        print("✓ Configuration validated successfully")
    
    def get(self, key: str, default=None):
        """Get configuration value by dot notation (e.g., 'radios.radio1.type')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def reload(self):
        """Reload configuration from file"""
        self.load()

if __name__ == "__main__":
    # Test
    config = ConfigLoader()
    print(f"System hostname: {config.get('system.hostname')}")
    print(f"Radio 1 type: {config.get('radios.radio1.type')}")
    print(f"Bands: {len(config.get('bands'))}")
