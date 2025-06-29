# Project Explanation: Application Configuration Service

This document explains the purpose and code of each file in the project, and describes the overall flow of the application.

---

## Directory Structure (as of latest update)

The project is now organized for multi-language support. The Python implementation is located at:

```
app_config_cli_tool/
└── python/                      # All Python-related code and docs
    ├── app_config_service/      # Main Python package (modular, testable)
    │   ├── cli.py               # Typer-based CLI entry point
    │   ├── config_manager.py    # Core config logic
    │   ├── storage.py           # File-based storage logic
    │   ├── validation.py        # Type checking/validation
    │   ├── models.py            # Data models
    │   ├── __init__.py          # Package initializer
    │   └── tests/               # Unit tests for the package
    ├── python_standalone_code/  # Standalone scripts/utilities
    │   └── Set_Config.py        # Standalone CLI script
    ├── PROJECT_EXPLANATION.md   # Project documentation/explanation
    └── requirements.txt         # Python dependencies for this language
... (future: rust/, golang/, etc.) # Other language implementations
```

---

## 1. app_config_service/cli.py
**Purpose:** Entry point for the command-line interface (CLI).
**Code:**
- Uses the `typer` library to define CLI commands for adding services, setting configurations, retrieving configurations, and listing services.
- Instantiates the file-based storage and configuration manager.
- Each CLI command calls methods on the `ConfigManager` to perform actions.
**Flow:**
- User runs a CLI command (e.g., `add-service`, `set-base`, `set-env`, `get-config`, `list-services`).
- The command is parsed and the corresponding function is called.
- The function interacts with the configuration manager and storage to perform the requested operation.

---

## 2. app_config_service/models.py
**Purpose:** Defines the core data models for configuration entries and services.
**Code:**
- `ConfigurationEntry`: Represents a configuration for a service in a specific environment, including config data and timestamps.
- `Service`: Represents a service with configurations for multiple environments.
**Flow:**
- When a configuration is added or updated, a `ConfigurationEntry` is created or modified.
- Each service manages its own configurations for different environments.

---

## 3. app_config_service/storage.py
**Purpose:** Provides file-based storage abstraction for services and their configurations.
**Code:**
- `FileStorage`: Manages persistent storage of services and their configurations in a JSON file.
**Flow:**
- The storage is used by the configuration manager to persist and retrieve service objects and their configurations.

---

## 4. app_config_service/config_manager.py
**Purpose:** Implements the core logic for managing configurations, enforcing rules and atomicity.
**Code:**
- `ConfigManager`: Provides methods to set base and environment-specific configurations, remove keys, and retrieve configurations.
- Enforces that all keys must be defined in the base configuration first, and propagates/removes keys as required.
- Integrates type validation and atomic updates.
**Flow:**
- Called by the CLI to perform configuration operations.
- Uses storage to persist changes and validation to enforce type safety.

---

## 5. app_config_service/validation.py
**Purpose:** Provides type checking and validation logic for configuration data.
**Code:**
- `validate_config_types`: Ensures that the types of values in new configuration data match those in the base configuration.
**Flow:**
- Called by the configuration manager before updating configurations to ensure type safety.

---

## 6. app_config_service/tests/test_config_manager.py
**Purpose:** Contains unit tests for the configuration manager logic.
**Code:**
- Uses Python's `unittest` framework to test adding services, setting configurations, type validation, key removal, persistence, and edge cases.
**Flow:**
- Run with `python -m unittest discover -s python/app_config_service/tests` to verify the correctness of the core logic.

---

## 7. PythonCode/Set_Config.py
**Purpose:** Standalone, simplified CLI tool for managing service configurations (alternative to the main Typer CLI).
**Code:**
- Implements a basic command loop for adding, updating, showing, and exporting service configs.
- Uses a separate `services.json` file for persistence.
**Flow:**
- Run with `python PythonCode/Set_Config.py` from the `python` folder.

---

## Visual Flow Diagram (Python Implementation)

```
+-------------------+
|      User         |
| (CLI Command)     |
+--------+----------+
         |
         v
+--------+----------+
|    cli.py         |
| (Typer CLI)       |
+--------+----------+
         |
         v
+--------+----------+
|  ConfigManager    |
| (config_manager)  |
+--------+----------+
         |
         v
+--------+----------+
| FileStorage       |
|   (storage)       |
+--------+----------+
         |
         v
+--------+----------+
|   Service &       |
| ConfigurationEntry|
|   (models)        |
+--------+----------+
         ^
         |
+--------+----------+
|  Validation       |
| (validation.py)   |
+-------------------+
```

- The user interacts with the CLI (`cli.py` or `Set_Config.py`).
- CLI commands call methods on `ConfigManager`.
- `ConfigManager` uses `FileStorage` to persist/retrieve services and configurations.
- Data is structured using models (`Service`, `ConfigurationEntry`).
- Type validation is performed before updates.

---

This structure ensures modularity, testability, and clear separation of concerns in the application. The repo is now ready for multi-language support and easy future expansion.
