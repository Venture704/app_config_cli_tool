# Core logic for managing configurations

from typing import Dict, Any, Optional
# from app_config_service.storage import InMemoryStorage
from app_config_service.storage import FileStorage
from app_config_service.models import ConfigurationEntry
from app_config_service.validation import validate_config_types

class ConfigManager:
    def __init__(self, storage):  # Accept any storage type
        self.storage = storage

    def set_base_config(self, service_name: str, config_data: Dict[str, Any]):
        if not service_name or not service_name.strip():
            raise ValueError('Service name cannot be empty.')
        if len(service_name) > 128:
            raise ValueError('Service name cannot exceed 128 characters.')
        if not isinstance(config_data, dict):
            raise ValueError('Config data must be a dictionary.')
        service = self.storage.add_service(service_name)
        base_entry = service.get_configuration('base')
        if base_entry:
            validate_config_types(base_entry.config_data, config_data)
            # Begin atomic update
            old_data = base_entry.config_data.copy()
            try:
                base_entry.update(config_data)
            except Exception as e:
                base_entry.config_data = old_data
                raise e
        else:
            service.add_configuration('base', config_data)
        # Propagate new keys to all environments
        for env, entry in service.configurations.items():
            if env == 'base':
                continue
            for key, value in config_data.items():
                if key not in entry.config_data:
                    entry.config_data[key] = value
        # Ensure changes are saved
        if hasattr(self.storage, 'save'):
            self.storage.save()

    def set_env_config(self, service_name: str, environment: str, config_data: Dict[str, Any]):
        if not service_name or not service_name.strip():
            raise ValueError('Service name cannot be empty.')
        if len(service_name) > 128:
            raise ValueError('Service name cannot exceed 128 characters.')
        if not environment or not environment.strip():
            raise ValueError('Environment name cannot be empty.')
        if not isinstance(config_data, dict):
            raise ValueError('Config data must be a dictionary.')
        service = self.storage.add_service(service_name)
        base_entry = service.get_configuration('base')
        if not base_entry:
            raise ValueError('Base configuration must be set first.')
        for key in config_data:
            if key not in base_entry.config_data:
                raise ValueError(f'Key {key} not defined in base configuration.')
        validate_config_types(base_entry.config_data, config_data)
        env_entry = service.get_configuration(environment)
        if env_entry:
            # Begin atomic update
            old_data = env_entry.config_data.copy()
            try:
                env_entry.update(config_data)
            except Exception as e:
                env_entry.config_data = old_data
                raise e
        else:
            merged = base_entry.config_data.copy()
            merged.update(config_data)
            service.add_configuration(environment, merged)
        # Ensure changes are saved
        if hasattr(self.storage, 'save'):
            self.storage.save()

    def remove_key_from_base(self, service_name: str, key: str):
        service = self.storage.get_service(service_name)
        if not service:
            return
        base_entry = service.get_configuration('base')
        if not base_entry or key not in base_entry.config_data:
            return
        del base_entry.config_data[key]
        # Remove from all environments
        for env, entry in service.configurations.items():
            if key in entry.config_data:
                del entry.config_data[key]
        # Ensure changes are saved
        if hasattr(self.storage, 'save'):
            self.storage.save()

    def get_config(self, service_name: str, environment: str) -> Optional[ConfigurationEntry]:
        service = self.storage.get_service(service_name)
        if not service:
            return None
        # Return environment config if exists, else base
        return service.get_configuration(environment) or service.get_configuration('base')
