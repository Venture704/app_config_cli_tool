# Type checking and validation logic

from typing import Dict, Any

def validate_config_types(base_config: Dict[str, Any], new_config: Dict[str, Any]):
    """
    Validates that the types of values in new_config match those in base_config.
    Raises ValueError if a type mismatch is found.
    """
    for key, value in new_config.items():
        if key in base_config:
            if not isinstance(value, type(base_config[key])):
                raise ValueError(f"Type mismatch for key '{key}': expected {type(base_config[key]).__name__}, got {type(value).__name__}")
