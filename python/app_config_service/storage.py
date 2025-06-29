# In-memory and file storage abstraction

from typing import Dict, Optional
import json
import os
from app_config_service.models import Service, ConfigurationEntry
from datetime import datetime

def service_to_dict(service: Service):
    return {
        'name': service.name,
        'configurations': {
            env: {
                'environment': entry.environment,
                'config_data': entry.config_data,
                'created_at': entry.created_at.isoformat(),
                'updated_at': entry.updated_at.isoformat(),
            } for env, entry in service.configurations.items()
        }
    }

def service_from_dict(data):
    service = Service(data['name'])
    for env, entry in data['configurations'].items():
        service.configurations[env] = ConfigurationEntry(
            entry['environment'],
            entry['config_data'],
            datetime.fromisoformat(entry['created_at']),
            datetime.fromisoformat(entry['updated_at'])
        )
    return service

# class InMemoryStorage:
#     def __init__(self):
#         self.services: Dict[str, Service] = {}
#
#     def add_service(self, service_name: str) -> Service:
#         if service_name not in self.services:
#             self.services[service_name] = Service(service_name)
#         return self.services[service_name]
#
#     def get_service(self, service_name: str) -> Optional[Service]:
#         return self.services.get(service_name)
#
#     def list_services(self):
#         return list(self.services.keys())

class FileStorage:
    def __init__(self, filename=None):
        if filename is None:
            # Always use path relative to this file's parent directory (app_config_service)
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(base_dir, 'config', 'config_data.json')
        else:
            # If a relative path is given, make it relative to this file's parent directory
            if not os.path.isabs(filename):
                base_dir = os.path.dirname(os.path.abspath(__file__))
                filename = os.path.join(base_dir, filename)
        self.filename = filename
        self.services = self.load()

    def load(self):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        if not os.path.exists(self.filename):
            with open(self.filename, "w") as f:
                json.dump({}, f)
            return {}
        with open(self.filename, "r") as f:
            data = json.load(f)
            return {name: service_from_dict(sdata) for name, sdata in data.items()}

    def save(self):
        with open(self.filename, "w") as f:
            json.dump({name: service_to_dict(service) for name, service in self.services.items()}, f, indent=2)

    def add_service(self, service_name: str) -> Service:
        if service_name not in self.services:
            self.services[service_name] = Service(service_name)
            self.save()
        return self.services[service_name]

    def get_service(self, service_name: str) -> Optional[Service]:
        return self.services.get(service_name)

    def list_services(self):
        return list(self.services.keys())
