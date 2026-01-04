import json
from pathlib import Path
from crypto_auto.models.crypto import CryptoProject


class ConfigurationError(Exception):
    pass


def load_crypto_projects(config_path: str | Path = "cryptos.json") -> list[CryptoProject]:
    config_file = Path(config_path)

    if not config_file.exists():
        raise ConfigurationError(f"Configuration file not found: {config_path}")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in {config_path}: {e}")

    if "projects" not in data:
        raise ConfigurationError(
            f"Missing 'projects' key in {config_path}. "
            "Expected format: {{\"projects\": [...]}}"
        )

    try:
        projects = [CryptoProject(**project) for project in data["projects"]]
    except Exception as e:
        raise ConfigurationError(f"Failed to parse projects from {config_path}: {e}")

    if not projects:
        raise ConfigurationError(f"No projects defined in {config_path}")

    _validate_allocations(projects)

    return projects


def _validate_allocations(projects: list[CryptoProject]) -> None:
    total_allocation = sum(p.target_allocation for p in projects)

    if not (0.99 <= total_allocation <= 1.01):
        raise ConfigurationError(
            f"Total target allocation is {total_allocation:.2f}, "
            f"but should sum to 1.0 (100%)"
        )
