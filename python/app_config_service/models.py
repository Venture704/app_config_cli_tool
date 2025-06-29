from typing import Dict, Any, Optional
from datetime import datetime, UTC

# Data models (Service, Configuration, etc.)

class ConfigurationEntry:
    def __init__(self, environment: str, config_data: Dict[str, Any], created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        self.environment = environment
        self.config_data = config_data  # flat JSON object (dict)
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    def update(self, new_data: Dict[str, Any]):
        self.config_data.update(new_data)
        self.updated_at = datetime.now(UTC)

class Service:
    def __init__(self, name: str):
        self.name = name
        self.configurations: Dict[str, ConfigurationEntry] = {}  # key: environment

    def add_configuration(self, environment: str, config_data: Dict[str, Any]):
        entry = ConfigurationEntry(environment, config_data)
        self.configurations[environment] = entry
        return entry

    def get_configuration(self, environment: str) -> Optional[ConfigurationEntry]:
        return self.configurations.get(environment)
