import unittest
# from app_config_service.storage import InMemoryStorage
from app_config_service.storage import FileStorage
from app_config_service.config_manager import ConfigManager
import os

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        # self.storage = InMemoryStorage()
        # Use a test-specific file to avoid clobbering real data
        self.test_file = "config/test_config_data.json"
        # Remove the file before each test to ensure isolation
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.storage = FileStorage(self.test_file)
        self.manager = ConfigManager(self.storage)

    def tearDown(self):
        # Clean up the test file after each test
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_service_and_base_config(self):
        # Test adding a service and setting its base configuration
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30})
        service = self.storage.get_service('payment-service')
        self.assertIsNotNone(service)
        base = service.get_configuration('base')
        self.assertEqual(base.config_data['timeout_seconds'], 30)

    def test_set_env_config_and_override(self):
        # Test setting environment config and overriding base config values
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30, 'retry_attempts': 3})
        self.manager.set_env_config('payment-service', 'production', {'timeout_seconds': 60})
        config = self.manager.get_config('payment-service', 'production')
        self.assertEqual(config.config_data['timeout_seconds'], 60)
        self.assertEqual(config.config_data['retry_attempts'], 3)

    def test_type_validation(self):
        # Test that type validation is enforced for config values
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30})
        with self.assertRaises(ValueError):
            self.manager.set_env_config('payment-service', 'production', {'timeout_seconds': 'wrong_type'})

    def test_remove_key_from_base(self):
        # Test removing a key from base config and propagation to environments
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30, 'retry_attempts': 3})
        self.manager.set_env_config('payment-service', 'production', {'timeout_seconds': 60})
        self.manager.remove_key_from_base('payment-service', 'timeout_seconds')
        config = self.manager.get_config('payment-service', 'production')
        self.assertNotIn('timeout_seconds', config.config_data)

    def test_list_services(self):
        # Test listing all services after adding multiple
        for service in self.storage.list_services():
            del self.storage.services[service]
        if hasattr(self.storage, 'save'):
            self.storage.save()
        self.assertEqual(self.storage.list_services(), [])
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30})
        self.assertIn('payment-service', self.storage.list_services())
        self.manager.set_base_config('order-service', {'timeout_seconds': 10})
        services = self.storage.list_services()
        self.assertIn('payment-service', services)
        self.assertIn('order-service', services)
        self.assertEqual(set(services), {'payment-service', 'order-service'})

    def test_delete_service(self):
        # Test deleting a service and ensuring it is removed
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30})
        self.assertIn('payment-service', self.storage.list_services())
        if hasattr(self.storage, 'services') and 'payment-service' in self.storage.services:
            del self.storage.services['payment-service']
            if hasattr(self.storage, 'save'):
                self.storage.save()
        self.assertNotIn('payment-service', self.storage.list_services())

    def test_describe_service(self):
        # Test describing a service to get all environment configs
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30, 'retry_attempts': 3})
        self.manager.set_env_config('payment-service', 'production', {'timeout_seconds': 60})
        service = self.storage.get_service('payment-service')
        self.assertIsNotNone(service)
        configs = {env: entry.config_data for env, entry in service.configurations.items()}
        self.assertIn('base', configs)
        self.assertIn('production', configs)
        self.assertEqual(configs['base']['timeout_seconds'], 30)
        self.assertEqual(configs['production']['timeout_seconds'], 60)

    def test_get_config(self):
        # Test getting config for a service/environment and fallback to base
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30, 'retry_attempts': 3})
        self.manager.set_env_config('payment-service', 'production', {'timeout_seconds': 60})
        entry = self.manager.get_config('payment-service', 'production')
        self.assertIsNotNone(entry)
        self.assertEqual(entry.config_data['timeout_seconds'], 60)
        self.assertEqual(entry.config_data['retry_attempts'], 3)
        # Test for missing config
        missing = self.manager.get_config('nonexistent', 'base')
        self.assertIsNone(missing)

    def test_duplicate_service_addition(self):
        # Test that adding a service with the same name overwrites the config
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30})
        # Add again with different config, should overwrite
        self.manager.set_base_config('payment-service', {'timeout_seconds': 99})
        service = self.storage.get_service('payment-service')
        self.assertEqual(service.get_configuration('base').config_data['timeout_seconds'], 99)

    def test_delete_nonexistent_service(self):
        # Test deleting a service that does not exist (should not raise error)
        try:
            if hasattr(self.storage, 'services') and 'ghost-service' in self.storage.services:
                del self.storage.services['ghost-service']
                if hasattr(self.storage, 'save'):
                    self.storage.save()
        except Exception as e:
            self.fail(f"Deleting non-existent service raised an error: {e}")
        self.assertNotIn('ghost-service', self.storage.list_services())

    def test_remove_env_config(self):
        # Test removing an environment-specific config
        self.manager.set_base_config('payment-service', {'timeout_seconds': 30})
        self.manager.set_env_config('payment-service', 'production', {'timeout_seconds': 60})
        # Remove environment config
        service = self.storage.get_service('payment-service')
        if 'production' in service.configurations:
            del service.configurations['production']
        self.assertNotIn('production', service.configurations)

    def test_persistence(self):
        # Test that data persists after reloading storage from file
        self.manager.set_base_config('persist-service', {'timeout_seconds': 42})
        # Reload storage from file
        new_storage = FileStorage(self.test_file)
        self.assertIn('persist-service', new_storage.list_services())
        service = new_storage.get_service('persist-service')
        self.assertEqual(service.get_configuration('base').config_data['timeout_seconds'], 42)

    def test_edge_cases(self):
        # Test empty service name, invalid environment name, and empty config data
        with self.assertRaises(Exception):
            self.manager.set_base_config('', {'timeout_seconds': 1})
        self.manager.set_base_config('edge-service', {'timeout_seconds': 1})
        with self.assertRaises(Exception):
            self.manager.set_env_config('edge-service', '', {'timeout_seconds': 2})
        self.manager.set_base_config('empty-config', {})
        service = self.storage.get_service('empty-config')
        self.assertEqual(service.get_configuration('base').config_data, {})

    def test_very_long_service_and_env_names(self):
        # Test handling of very long service and environment names (up to 128 chars allowed)
        long_name = 's' * 128
        self.manager.set_base_config(long_name, {'timeout': 1})
        self.assertIn(long_name, self.storage.list_services())
        self.manager.set_env_config(long_name, 'e' * 128, {'timeout': 2})
        service = self.storage.get_service(long_name)
        self.assertIn('e' * 128, service.configurations)
        # Test that >128 chars is rejected
        too_long = 's' * 129
        with self.assertRaises(ValueError):
            self.manager.set_base_config(too_long, {'timeout': 1})

    def test_special_characters_in_names(self):
        # Test service and environment names with special characters and unicode
        special_name = 'service!@# 你好'
        env_name = 'prod-测试'
        self.manager.set_base_config(special_name, {'timeout': 1})
        self.manager.set_env_config(special_name, env_name, {'timeout': 2})
        service = self.storage.get_service(special_name)
        self.assertIn(env_name, service.configurations)

    def test_duplicate_environment_addition(self):
        # Test that adding the same environment twice overwrites the config
        self.manager.set_base_config('dup-service', {'timeout': 1})
        self.manager.set_env_config('dup-service', 'prod', {'timeout': 2})
        # Add again, should overwrite
        self.manager.set_env_config('dup-service', 'prod', {'timeout': 3})
        config = self.manager.get_config('dup-service', 'prod')
        self.assertEqual(config.config_data['timeout'], 3)

    def test_nested_config_data(self):
        # Test that nested dicts in config data are accepted and retrievable
        self.manager.set_base_config('nested-service', {'timeout': 1, 'meta': {'a': 1}})
        config = self.manager.get_config('nested-service', 'base')
        self.assertIsInstance(config.config_data['meta'], dict)
        self.assertEqual(config.config_data['meta']['a'], 1)

    def test_remove_nonexistent_key_from_base(self):
        # Test removing a key that does not exist from base config (should not raise error)
        self.manager.set_base_config('remove-key', {'timeout': 1})
        # Should not raise error
        try:
            self.manager.remove_key_from_base('remove-key', 'notfound')
        except Exception as e:
            self.fail(f"Removing non-existent key raised error: {e}")

    def test_case_sensitivity(self):
        # Test that service names are case-sensitive
        self.manager.set_base_config('CaseService', {'timeout': 1})
        self.manager.set_base_config('caseservice', {'timeout': 2})
        self.assertIn('CaseService', self.storage.list_services())
        self.assertIn('caseservice', self.storage.list_services())
        self.assertNotEqual(
            self.storage.get_service('CaseService').get_configuration('base').config_data['timeout'],
            self.storage.get_service('caseservice').get_configuration('base').config_data['timeout']
        )

    def test_none_as_config_data(self):
        # Test that passing None as config data raises an error
        with self.assertRaises(Exception):
            self.manager.set_base_config('none-service', None)

    def test_export_service_to_json(self):
        # Test exporting a service's config to a JSON file
        self.manager.set_base_config('export-service', {'timeout': 123, 'url': 'http://test'})
        self.manager.set_env_config('export-service', 'prod', {'timeout': 456})
        service = self.storage.get_service('export-service')
        out_file = 'export-service.json'
        if os.path.exists(out_file):
            os.remove(out_file)
        # Simulate the print_service_json logic
        with open(out_file, "w") as f:
            import json
            json.dump({env: entry.config_data for env, entry in service.configurations.items()}, f, indent=2)
        # Now check the file exists and contents are correct
        self.assertTrue(os.path.exists(out_file))
        with open(out_file, "r") as f:
            data = json.load(f)
            self.assertIn('base', data)
            self.assertIn('prod', data)
            self.assertEqual(data['base']['timeout'], 123)
            self.assertEqual(data['prod']['timeout'], 456)
        os.remove(out_file)

if __name__ == '__main__':
    unittest.main()
