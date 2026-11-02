from pathlib import Path
import yaml

DEFAULT = Path(__file__).with_name("default_config.yaml")

def load_config(path):
    path = Path(path).resolve()
    with DEFAULT.open() as f:
        defaults = yaml.safe_load(f)
    with path.open() as f:
        supplied = yaml.safe_load(f) or {}
    if not isinstance(supplied, dict):
        raise ValueError("Configuration must be a YAML mapping")
    for section, values in supplied.items():
        if isinstance(values, dict) and isinstance(defaults.get(section), dict):
            defaults[section].update(values)
        else:
            defaults[section] = values
    for section, key in [("input", "genomes"), ("project", "output")]:
        value = Path(defaults[section][key]).expanduser()
        defaults[section][key] = str((path.parent / value).resolve()) if not value.is_absolute() else str(value)
    if defaults["annotation"]["tool"] not in {"prokka", "bakta"}:
        raise ValueError("annotation.tool must be prokka or bakta")
    dbs = defaults["abricate"]["databases"]
    if not dbs or not all(isinstance(x, str) and x.isidentifier() for x in dbs):
        raise ValueError("abricate.databases must contain safe database identifiers")
    return defaults
