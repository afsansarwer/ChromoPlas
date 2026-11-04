"""Capture an auditable, local snapshot of inputs, environment and databases."""
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _command(args, timeout=15):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        output = (result.stdout or result.stderr).strip()
        return {"status": "ok" if result.returncode == 0 else "error",
                "exit_code": result.returncode, "output": output[:20000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "error": str(exc)}


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_revision():
    # Editable installs normally retain a Git working tree; installed wheels may not.
    root = Path(__file__).resolve().parents[2]
    result = _command(["git", "-C", str(root), "rev-parse", "HEAD"])
    return result["output"] if result["status"] == "ok" else None


def create_provenance(destination, samples, config):
    """Write metadata at the start of a run; never silently replace missing values with 'verified'."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        package_version = version("chromoplas")
    except PackageNotFoundError:
        package_version = None
    tools = {
        "snakemake": _command(["snakemake", "--version"]),
        "abricate": _command(["abricate", "--version"]),
        "mob_recon": _command(["mob_recon", "--version"]),
    }
    if config.get("annotation", {}).get("enabled", False):
        tools["prokka"] = _command(["prokka", "--version"])
    dbs = _command(["abricate", "--list"])
    record = {
        "schema_version": 1,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "chromoplas_version": package_version,
        "chromoplas_git_commit": _source_revision(),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "conda_environment": os.environ.get("CONDA_DEFAULT_ENV"),
        "tools": tools,
        "abricate_database_listing": dbs,
        "selected_abricate_databases": config.get("abricate", {}).get("databases", []),
        "inputs": {
            name: {"path": str(Path(path).resolve()), "sha256": _sha256(path),
                   "bytes": Path(path).stat().st_size}
            for name, path in sorted(samples.items())
        },
        "note": "Snapshots document tools and inputs; they do not validate scientific assignments.",
    }
    destination.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination
