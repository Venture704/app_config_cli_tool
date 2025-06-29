# Simple CLI tool for managing service configurations with environments

"""
# Example commands you can try in this CLI:

# Add a new service
add myservice

# Set a config key/value for an environment
set myservice prod timeout 60
set myservice prod retries 5

# Add or replace an entire environment config (JSON)
addenv myservice prod '{"timeout": 60, "retries": 5}'

# Show all configs for a service
show myservice

# Delete a service
delete myservice

# Export a service's config to a JSON file
printjson myservice

# List all services
list

# Exit the CLI
exit

# Example that will throw an error:
addenv myservice prod '{timeout: 60, retries: 5}'  # Invalid JSON (keys must be in double quotes)

# Note:
# - For addenv, the third argument must be a valid JSON string (use single quotes around JSON, and double quotes for keys/values).
# - For set, you can set any key/value in any environment.
"""

class Config:
    def __init__(self, service_name, config=None):
        self.service_name = service_name
        # Structure: {"base": {...}, "production": {...}, ...}
        self.config = config or {"base": {}}
        print(f"{self.service_name} onboarded")

    def add_env(self, env_name, env_config):
        try:
            self.config[env_name] = env_config
            print(f"Added/updated environment '{env_name}' for {self.service_name}")
        except Exception as e:
            print(f"Error adding environment: {e}")

    def get_service(self):
        return {"service": self.service_name, "configs": self.config}

    def set_service(self, env, config_key, config_value):
        try:
            if env not in self.config:
                self.config[env] = {}
            self.config[env][config_key] = config_value
            print(f"Set {config_key}={config_value} in {env} for {self.service_name}")
        except Exception as e:
            print(f"Error setting config: {e}")

    def show(self):
        try:
            print(f"Service: {self.service_name}")
            for env, conf in self.config.items():
                print(f"  [{env}] {conf}")
        except Exception as e:
            print(f"Error showing service: {e}")


def parse_input(input_str):
    import shlex
    try:
        parts = shlex.split(input_str)
        if not parts:
            return None, []
        cmd = parts[0]
        return cmd, parts[1:]
    except Exception as e:
        print(f"Error parsing input: {e}")
        return None, []

import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICES_FILE = os.path.join(SCRIPT_DIR, "services.json")

def load_services():
    try:
        if os.path.exists(SERVICES_FILE):
            with open(SERVICES_FILE, "r") as f:
                data = json.load(f)
                return {name: Config(name, config) for name, config in data.items()}
        return {}
    except Exception as e:
        print(f"Error loading services: {e}")
        return {}

def save_services(services):
    try:
        data = {name: svc.config for name, svc in services.items()}
        with open(SERVICES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving services: {e}")


def main():
    services = load_services()
    print("Welcome to the Config CLI! Type 'help' for commands, 'exit' to quit.")
    while True:
        try:
            user_input = input("config> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                save_services(services)
                print("Goodbye!")
                break
            if user_input.lower() == "help":
                print("Commands:")
                print("  add <service_name>                 - Add a new service")
                print("  set <service> <env> <key> <value>  - Set config key/value for env")
                print("  addenv <service> <env> <json>      - Add/replace env config (JSON)")
                print("  show <service>                     - Show all configs for a service")
                print("  delete <service>                   - Delete a service")
                print("  printjson <service>                - Export a service's config to a JSON file")
                print("  list                               - List all services")
                print("  exit                               - Quit")
                continue
            cmd, args = parse_input(user_input)
            if cmd == "add" and len(args) == 1:
                name = args[0]
                if name in services:
                    print(f"Service '{name}' already exists.")
                else:
                    services[name] = Config(name)
                    save_services(services)
            elif cmd == "set" and len(args) == 4:
                name, env, key, value = args
                if name not in services:
                    print(f"Service '{name}' not found.")
                else:
                    services[name].set_service(env, key, value)
                    save_services(services)
            elif cmd == "addenv" and len(args) == 3:
                name, env, json_str = args
                if name not in services:
                    print(f"Service '{name}' not found.")
                else:
                    try:
                        env_config = json.loads(json_str)
                        services[name].add_env(env, env_config)
                        save_services(services)
                    except Exception as e:
                        print(f"Invalid JSON: {e}")
            elif cmd == "show" and len(args) == 1:
                name = args[0]
                if name not in services:
                    print(f"Service '{name}' not found.")
                else:
                    services[name].show()
            elif cmd == "delete" and len(args) == 1:
                name = args[0]
                if name not in services:
                    print(f"Service '{name}' not found.")
                else:
                    del services[name]
                    save_services(services)
                    print(f"Service '{name}' deleted.")
            elif cmd == "printjson" and len(args) == 1:
                name = args[0]
                if name not in services:
                    print(f"Service '{name}' not found.")
                else:
                    try:
                        out_file = os.path.join(SCRIPT_DIR, f"{name}.json")
                        with open(out_file, "w") as f:
                            json.dump(services[name].config, f, indent=2)
                        print(f"A new JSON file '{name}.json' has been created for this service.")
                    except Exception as e:
                        print(f"Error exporting service: {e}")
            elif cmd == "list" and not args:
                if not services:
                    print("No services found.")
                else:
                    print("Services:", ", ".join(services.keys()))
            else:
                print("Unknown or malformed command. Type 'help' for usage.")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()




