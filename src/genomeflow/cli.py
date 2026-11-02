import csv
import json
import re
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path
import typer
import yaml
from .config import DEFAULT, load_config
from .qc import metrics, assess, write_tsv
from .report import build_report

app = typer.Typer(help="Bacterial assembly analysis with Snakemake", no_args_is_help=True)
SUFFIXES = (".fasta", ".fa", ".fna", ".fasta.gz", ".fa.gz", ".fna.gz")

def discover(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError(f"Input folder does not exist: {folder}")
    found = {}
    for path in sorted(folder.iterdir()):
        if not path.is_file() or not path.name.lower().endswith(SUFFIXES):
            continue
        stem = path.name
        for suffix in SUFFIXES:
            if stem.lower().endswith(suffix):
                stem = stem[:-len(suffix)]
                break
        sample = re.sub(r"[^A-Za-z0-9_-]", "_", stem)
        if not sample or sample in found:
            raise ValueError(f"Invalid or duplicate sample name: {sample}")
        found[sample] = str(path.resolve())
    if not found:
        raise ValueError("No FASTA files found")
    return found

@app.command()
def init(directory: Path = typer.Argument(Path("."), help="Project directory")):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "config.yaml"
    if target.exists():
        raise typer.BadParameter(f"Already exists: {target}")
    target.write_text(DEFAULT.read_text())
    (directory / "genomes").mkdir(exist_ok=True)
    typer.echo(f"Created {target} and genomes/")

@app.command()
def qc(config: Path = typer.Option(..., "--config", "-c")):
    cfg = load_config(config)
    samples = discover(cfg["input"]["genomes"])
    rows = []
    for sample, path in samples.items():
        m = metrics(path)
        status, reasons = assess(m, cfg["quality"])
        rows.append(dict(sample=sample, input_fasta=path, **m, status=status, reasons=reasons))
    dest = Path(cfg["project"]["output"]) / "02_quality" / "quality_summary.tsv"
    write_tsv(dest, rows, list(rows[0]))
    typer.echo(f"Saved {dest}; passing {sum(x['status']=='PASS' for x in rows)}/{len(rows)}")

@app.command()
def doctor(config: Path = typer.Option(..., "--config", "-c")):
    cfg = load_config(config)
    for binary in ["snakemake", cfg["annotation"]["tool"], "abricate", "mob_recon"]:
        typer.echo(f"{binary}: {shutil.which(binary) or 'MISSING'}")
    try:
        typer.echo(f"FASTA files: {len(discover(cfg['input']['genomes']))}")
    except ValueError as exc:
        typer.echo(f"WARNING: {exc}")
    if cfg["annotation"]["tool"] == "bakta" and not cfg["annotation"].get("bakta_db"):
        typer.echo("WARNING: configure annotation.bakta_db or BAKTA_DB")

@app.command()
def run(config: Path = typer.Option(..., "--config", "-c"),
        cores: int = typer.Option(2, min=1), dry_run: bool = typer.Option(False, "--dry-run"),
        keep_going: bool = typer.Option(False, "--keep-going")):
    cfg = load_config(config)
    samples = discover(cfg["input"]["genomes"])
    out = Path(cfg["project"]["output"])
    out.mkdir(parents=True, exist_ok=True)
    runtime = out / "00_metadata"
    runtime.mkdir(exist_ok=True)
    manifest = runtime / "samples.json"
    manifest.write_text(json.dumps(samples, indent=2))
    effective = runtime / "resolved_config.yaml"
    cfg["_manifest"] = str(manifest)
    effective.write_text(yaml.safe_dump(cfg, sort_keys=False))
    snakefile = files("genomeflow").joinpath("workflow/Snakefile")
    cmd = ["snakemake", "--snakefile", str(snakefile), "--configfile", str(effective),
           "--directory", str(out), "--cores", str(cores), "--printshellcmds", "07_reports/report.html"]
    if dry_run: cmd.append("--dry-run")
    if keep_going: cmd.append("--keep-going")
    typer.echo("Executing: " + " ".join(cmd))
    try:
        code = subprocess.call(cmd)
    except FileNotFoundError:
        typer.echo("Snakemake missing. Install package dependencies.", err=True)
        raise typer.Exit(127)
    raise typer.Exit(code)


@app.command("analyze")
def analyze(
    inputs: list[Path] = typer.Argument(..., help="One or more FASTA files or directories"),
    output: Path = typer.Option(..., "--output", "-o", help="Results directory"),
    threads: int = typer.Option(4, "--threads", "-t", min=1),
    config: Path | None = typer.Option(None, "--config", "-c", help="Optional custom YAML configuration"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    keep_going: bool = typer.Option(False, "--keep-going"),
):
    """Run the full pipeline directly from FASTA input(s)."""
    from tempfile import TemporaryDirectory
    from .config import DEFAULT
    from .config import load_config as _load
    paths = []
    for entry in inputs:
        entry = entry.expanduser().resolve()
        if entry.is_file() and entry.name.lower().endswith(SUFFIXES):
            paths.append(entry)
        elif entry.is_dir():
            paths.extend(p.resolve() for p in sorted(entry.iterdir()) if p.is_file() and p.name.lower().endswith(SUFFIXES))
        else:
            typer.echo(f"Invalid FASTA input: {entry}", err=True)
            raise typer.Exit(2)
    paths = list(dict.fromkeys(paths))
    if not paths:
        typer.echo("No FASTA files found", err=True)
        raise typer.Exit(2)
    out = output.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    if any(p == out or out in p.parents for p in paths):
        typer.echo("Input FASTA must not be inside the output directory", err=True)
        raise typer.Exit(2)
    with TemporaryDirectory(prefix="genomeflow-config-") as temp:
        staged = out / "00_metadata" / "input_links"
        staged.mkdir(parents=True, exist_ok=True)
        expected_names = {p.name for p in paths}
        for stale in staged.iterdir():
            if stale.is_symlink() and stale.name not in expected_names:
                stale.unlink()
        for p in paths:
            link = staged / p.name
            if link.is_symlink() and link.resolve() == p:
                continue
            if link.exists() or link.is_symlink():
                typer.echo(f"Duplicate FASTA filename: {p.name}", err=True)
                raise typer.Exit(2)
            link.symlink_to(p)
        # Write a standalone config with absolute paths, preserving custom settings.
        from copy import deepcopy
        if config:
            cfg = _load(config)
        else:
            cfg = yaml.safe_load(DEFAULT.read_text())
        cfg["input"]["genomes"] = str(staged)
        cfg["project"]["output"] = str(out)
        cfg["resources"]["threads_per_job"] = min(threads, cfg["resources"].get("threads_per_job", 2))
        # Persistent links support resumable runs and stable manifests.
        temp_config = Path(temp) / "config.yaml"
        temp_config.write_text(yaml.safe_dump(cfg))
        run(config=temp_config, cores=threads, dry_run=dry_run, keep_going=keep_going)


def main():
    """Allow `genomeflow sample.fasta -o results` while retaining subcommands."""
    if len(sys.argv) > 1:
        first = sys.argv[1]
        known = {"analyze", "run", "init", "qc", "doctor"}
        if first not in known and not first.startswith("-"):
            sys.argv.insert(1, "analyze")
    app()

if __name__ == "__main__":
    main()
