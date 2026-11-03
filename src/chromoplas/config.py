"""Load and validate ChromoPlas YAML settings."""
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
import yaml


def default_config():
    return yaml.safe_load(files("chromoplas").joinpath("default_config.yaml").read_text())


def load_config(path):
    path = Path(path).expanduser().resolve()
    supplied = yaml.safe_load(path.read_text()) or {}
    if not isinstance(supplied, dict):
        raise ValueError("Config must be a YAML mapping")
    config = default_config()
    for section, value in supplied.items():
        if isinstance(value, dict) and isinstance(config.get(section), dict):
            config[section].update(value)
        else:
            config[section] = deepcopy(value)
    for section, key in (("project", "output"), ("input", "genomes")):
        value = Path(config[section][key]).expanduser()
        if not value.is_absolute():
            value = path.parent / value
        config[section][key] = str(value.resolve())
    databases = config["abricate"]["databases"]
    if not databases or not isinstance(databases, list):
        raise ValueError("abricate.databases must be a non-empty list")
    if not all(isinstance(db, str) and db.isidentifier() for db in databases):
        raise ValueError("Invalid ABRicate database name")
    for key in ("min_identity", "min_coverage"):
        v = float(config["abricate"][key])
        if not 0 <= v <= 100:
            raise ValueError(f"abricate.{key} must be between 0 and 100")
    for key in ("max_contigs", "max_genome_size", "min_genome_size", "min_n50"):
        if int(config["quality"][key]) < 0:
            raise ValueError(f"quality.{key} must be nonnegative")
    return config
