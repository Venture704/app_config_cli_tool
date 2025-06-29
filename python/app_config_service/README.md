# Application Configuration Service

## Steps Completed

### Step 1: Project Structure
- Created the project folder `app_config_service` with the following files:
  - `cli.py`: Entry point for the CLI
  - `config_manager.py`: Core logic for managing configurations
  - `storage.py`: In-memory/ FSS storage abstraction
  - `validation.py`: Type checking and validation logic
  - `models.py`: Data models (Service, Configuration, etc.)
  - `__init__.py`: Package initializer
  - `tests/`: Directory for unit tests

### Step 2: Data Models
- Defined `ConfigurationEntry` and `Service` classes in `models.py` to represent configuration data, environments, and timestamps.

### Step 3: In-Memory Storage
- Implemented `InMemoryStorage` in `storage.py` to manage services and their configurations.

### Step 4: Base Configuration Logic
- Implemented `ConfigManager` in `config_manager.py` to enforce base configuration rules, environment overrides, key propagation, and key removal logic.

### Step 5: CLI Implementation
- Implemented CLI commands in `cli.py` using Typer:
  - Add a service
  - Set/update base configuration
  - Set/update environment-specific configuration
  - Get configuration for a service/environment
  - List all services

### Step 6: Validation & Atomicity
- Added type checking for configuration updates using a validation function in `validation.py`.
- Integrated validation and atomic (all-or-nothing) updates into `ConfigManager` methods in `config_manager.py`.

### Step 7: Testing
- Added unit tests in `tests/test_config_manager.py` to verify:
  - Adding a service and base configuration
  - Setting and overriding environment-specific configuration
  - Type validation enforcement
  - Removing keys from base configuration and propagation

### Step 8: Documentation

This README will be updated as further steps are completed.

### Step 9: Error Handling Improvements
- Enhanced the CLI (`cli.py`) to gracefully handle errors and invalid input.
- All commands now catch exceptions and display user-friendly error messages instead of stack traces.
- Invalid JSON and configuration errors are clearly reported to the user.

## Usage

### Install dependencies
```
pip install typer
```

### Run the CLI
```
python -m app_config_service.cli [COMMAND] [ARGS]
```

**Important:**
- When setting environment-specific configuration with `set-env`, the keys you use must already exist in the base configuration for that service. Always set the base config first with all allowed keys using `set-base`, then set environment configs.

#### Example commands
- Add a service:
  ```
  python -m app_config_service.cli add-service payment-service
  ```
- Set base configuration (define all allowed keys first!):
  ```
  python -m app_config_service.cli set-base payment-service '{"timeout_seconds": 30, "retry_attempts": 3}'
  ```
- Set environment configuration (only use keys defined in base config):
  ```
  python -m app_config_service.cli set-env payment-service production '{"timeout_seconds": 60, "retry_attempts": 5}'
  ```
- Get configuration:
  ```
  python -m app_config_service.cli get-config payment-service production
  ```
- List all services:
  ```
  python -m app_config_service.cli list-services
  ```
- Export a service's config to a JSON file:
  ```
  python -m app_config_service.cli print-service-json payment-service
  ```

### Run tests
```
python -m unittest discover -s app_config_service/tests
```

## CLI Usage Examples

All commands should be run from the parent directory (e.g., `Downloads`) using the `-m` flag:

### PowerShell

```powershell
# Add a new service
python -m app_config_service.cli add-service myservice

# Set base configuration for a service
python -m app_config_service.cli set-base myservice '{"timeout": 30, "retries": 3}'

# Set environment-specific configuration
python -m app_config_service.cli set-env myservice production '{"timeout": 60}'

# Get configuration for a service in a specific environment
python -m app_config_service.cli get-config myservice production

# List all services
python -m app_config_service.cli list-services

# Export a service's config to a JSON file
python -m app_config_service.cli print-service-json myservice
```

### Bash (Linux/macOS/WSL)

```bash
# Add a new service
python -m app_config_service.cli add-service myservice

# Set base configuration for a service
python -m app_config_service.cli set-base myservice '{"timeout": 30, "retries": 3}'

# Set environment-specific configuration
python -m app_config_service.cli set-env myservice production '{"timeout": 60}'

# Get configuration for a service in a specific environment
python -m app_config_service.cli get-config myservice production

# List all services
python -m app_config_service.cli list-services

# Export a service's config to a JSON file
python -m app_config_service.cli print-service-json myservice
```

## Interactive CLI Mode

You can now run the CLI in interactive mode. Just run:

```
python -m app_config_service.cli
```

You'll see:
```
Welcome to config CLI!
Type 'help' to see available commands. Type 'exit' to quit.
config>
```

From there, you can type commands like:
- `add-service myservice`
- `set-base myservice {"timeout": 30, "retries": 3}`
- `set-env myservice production {"timeout": 60}`
- `get-config myservice production`
- `describe-service myservice` *(shows all configs for a service)*
- `delete-service myservice` *(removes a service and all its configs)*
- `print-service-json myservice` *(exports the service config to a JSON file)*
- `list-services`
- `help` 
- `exit`

**Notes:**
- For `set-base` and `set-env`, you can include spaces in the JSON (e.g., `set-base myservice {"timeout": 30, "retries": 3}`)
- For `get-config`, you must provide both the service name and the environment (e.g., `get-config myservice production`)
- If you get a JSON error, check your quotes: in PowerShell, use single quotes outside and double quotes inside the JSON.
- `describe-service` shows all environments and their configs for a service.
- `delete-service` removes a service and all its configurations.

**Manual Testing Note:**
- Argument validation for interactive CLI commands (such as `list-services`) is manually tested. Automated tests cover only the Typer CLI commands, not the interactive input loop.

**Advanced & Edge Case Examples:**

```bash
# Add a service with a long name (up to 128 characters)
python -m app_config_service.cli add-service $(python -c "print('s'*128)")

# Add a service with special characters and unicode
python -m app_config_service.cli add-service "service!@# 你好"

# Set base config with nested data
python -m app_config_service.cli set-base nested-service '{"timeout": 1, "meta": {"a": 1}}'

# Set environment config for a long environment name
python -m app_config_service.cli set-env myservice $(python -c "print('e'*300)") '{"timeout": 2}'

# Overwrite an environment config
python -m app_config_service.cli set-env myservice production '{"timeout": 10}'
python -m app_config_service.cli set-env myservice production '{"timeout": 20}'

# List all services (should show all added, including special/long names)
python -m app_config_service.cli list-services

# Describe a service (shows all environments and configs)
python -m app_config_service.cli describe-service myservice

# Delete a service
python -m app_config_service.cli delete-service myservice

# Try to add a service with an empty name (should error)
python -m app_config_service.cli add-service ""

# Try to set base config with None (should error)
python -m app_config_service.cli set-base myservice null

# Try to set environment config with an empty environment name (should error)
python -m app_config_service.cli set-env myservice "" '{"timeout": 1}'

# Add two services differing only by case (case sensitivity)
python -m app_config_service.cli add-service CaseService
python -m app_config_service.cli add-service caseservice
python -m app_config_service.cli list-services

# Try to add a service with a name longer than 128 characters (should error)
python -m app_config_service.cli add-service $(python -c "print('s'*129)")
```

**Limitations:**
- Service names must be non-empty and cannot exceed 128 characters. Attempts to add or use a service name longer than 128 characters will result in an error.

---

## Troubleshooting & Debugging

If you encounter issues with command parsing in the interactive CLI (for example, when using spaces or special characters), you can enable a debug print to see exactly how your input is being parsed:

1. Open `cli.py`.
2. Find the line:
   ```python
   # print(f"[DEBUG] Parsed parts: {parts}")  # Uncomment for troubleshooting
   ```
3. Uncomment this line by removing the `#` at the start:
   ```python
   print(f"[DEBUG] Parsed parts: {parts}")  # Uncomment for troubleshooting
   ```
4. Run the CLI in interactive mode. Each command you enter will show how it was parsed.
5. Comment the line again when you are done debugging.

This is useful for diagnosing issues with quoting, spaces, or special characters in your commands.

---

## Running Unit Tests

Unit tests are provided to ensure the reliability and correctness of all core features and edge cases.

### Run all tests from the command line

From the parent directory (e.g., `Downloads`), run:

```
python -m unittest discover -s app_config_service/tests
```

This will automatically discover and run all test cases in the `tests` folder.

### Run a specific test file

```
python -m unittest app_config_service.tests.test_config_manager
```

### Run tests in VS Code
- Open the `app_config_service/tests` folder in VS Code.
- Right-click on a test function or file and select **Run Test** or **Debug Test**.
- You can also use the built-in Test Explorer for a graphical interface.

### Notes
- Tests are isolated and use a separate test config file (`test_config_data.json`) to avoid affecting your real data.
- All major features, edge cases, and error conditions are covered by the tests.

---
