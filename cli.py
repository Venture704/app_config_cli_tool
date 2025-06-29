import sys
import os
import shlex
try:
    # Try absolute imports for package/module execution
    from app_config_service.storage import FileStorage
    from app_config_service.config_manager import ConfigManager
except ImportError:
    # Fallback to relative imports for direct script execution
    from storage import FileStorage
    from config_manager import ConfigManager
import typer
import json
from typing import Optional
# from app_config_service.storage import InMemoryStorage

app = typer.Typer()
# storage = InMemoryStorage()
storage = FileStorage("config/config_data.json")  # Now saves in config folder
manager = ConfigManager(storage)

def interactive_cli():
    print("Welcome to config CLI!")
    print("Type 'help' to see available commands. Type 'exit' to quit.")
    while True:
        try:
            cmd = input("config> ").strip()
            if not cmd:
                continue
            if cmd.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            if cmd.lower() == "help":
                print("Available commands:")
                print("  add-service <service_name>")
                print("  set-base <service_name> <json_config>")
                print("  set-env <service_name> <environment> <json_config>")
                print("  get-config <service_name> <environment>")
                print("  describe-service <service_name>")
                print("  delete-service <service_name>")
                print("  print-service-json <service_name>   # Export a service's config to a JSON file")
                print("  list-services")
                print("  clear")
                print("  exit")
                continue
            if cmd.lower() == "clear":
                # Clear the terminal screen (Windows: cls, others: clear)
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            # Use shlex.split to handle quoted arguments
            parts = shlex.split(cmd)
            # To debug command parsing, uncomment the next line:
            # print(f"[DEBUG] Parsed parts: {parts}")  # Uncomment for troubleshooting
            if not parts:
                continue
            command = parts[0]
            if command == "add-service" and len(parts) == 2:
                add_service(parts[1])
            elif command == "set-base" and len(parts) >= 3:
                # Join all after the service name as JSON
                set_base(parts[1], ' '.join(parts[2:]))
            elif command == "set-env" and len(parts) >= 4:
                # Join all after the environment as JSON
                set_env(parts[1], parts[2], ' '.join(parts[3:]))
            elif command == "get-config" and len(parts) == 3:
                get_config(parts[1], parts[2])
            elif command == "describe-service" and len(parts) == 2:
                describe_service(parts[1])
            elif command == "delete-service" and len(parts) == 2:
                delete_service(parts[1])
            elif command == "print-service-json" and len(parts) == 2:
                print_service_json(parts[1])
            elif command == "list-services" and len(parts) == 1:
                list_services()
            elif command == "list-services":
                print("'list-services' does not take any arguments. Type 'help' for usage.")
            else:
                print("Unknown or malformed command. Type 'help' for usage.")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

@app.command()
def add_service(service_name: str):
    """Add a new service."""
    try:
        manager.set_base_config(service_name, {})
        typer.echo(f"Service '{service_name}' added.")
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def set_base(service_name: str, config_json: str):
    """Set or update base configuration for a service. config_json should be a JSON string."""
    try:
        config_data = json.loads(config_json)
        manager.set_base_config(service_name, config_data)
        typer.echo(f"Base configuration for '{service_name}' set/updated.")
    except json.JSONDecodeError:
        typer.secho("Invalid JSON format for config_json.", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def set_env(service_name: str, environment: str, config_json: str):
    """Set or update environment-specific configuration. config_json should be a JSON string."""
    try:
        config_data = json.loads(config_json)
        manager.set_env_config(service_name, environment, config_data)
        typer.echo(f"Configuration for '{service_name}' in '{environment}' set/updated.")
    except json.JSONDecodeError:
        typer.secho("Invalid JSON format for config_json.", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def get_config(service_name: str, environment: str):
    """Get configuration for a service in a specific environment."""
    try:
        entry = manager.get_config(service_name, environment)
        if entry:
            typer.echo(json.dumps(entry.config_data, indent=2))
        else:
            typer.secho("No configuration found.", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def list_services():
    """List all services."""
    try:
        services = storage.list_services()
        typer.echo("\n".join(services) if services else "No services found.")
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def describe_service(service_name: str):
    """Show the full configuration (all environments) for a service."""
    try:
        service = storage.get_service(service_name)
        if not service:
            typer.secho(f"Service '{service_name}' not found.", fg=typer.colors.YELLOW)
            return
        typer.echo(json.dumps({env: entry.config_data for env, entry in service.configurations.items()}, indent=2))
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

@app.command()
def delete_service(service_name: str):
    """Delete a service and all its configurations."""
    try:
        if hasattr(storage, 'services') and service_name in storage.services:
            del storage.services[service_name]
            if hasattr(storage, 'save'):
                storage.save()
            typer.echo(f"Service '{service_name}' deleted.")
        else:
            typer.secho(f"Service '{service_name}' not found.", fg=typer.colors.YELLOW)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)

def print_service_json(service_name: str):
    """Export a service's config to a JSON file in the config folder and print a confirmation message."""
    try:
        service = storage.get_service(service_name)
        if not service:
            print(f"Service '{service_name}' not found.")
            return
        config_dir = os.path.join(os.path.dirname(__file__), "config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        out_file = os.path.join(config_dir, f"{service_name}.json")
        with open(out_file, "w") as f:
            json.dump({
                "service_name": service_name,
                "configurations": {env: entry.config_data for env, entry in service.configurations.items()}
            }, f, indent=2)
        print(f"A new JSON file '{out_file}' has been created for this service.")
    except Exception as e:
        print(f"Error exporting service: {e}")

# Entry point for the CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        interactive_cli()
    else:
        app()
