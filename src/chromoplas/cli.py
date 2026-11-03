"""ChromoPlas command-line interface."""
import json
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import typer
import yaml

from .config import default_config, load_config
from .inputs import discover
from .qc import metrics, assess, write_tsv

app = typer.Typer(help="ChromoPlas: contig-resolved chromosome/plasmid gene localization",
                  no_args_is_help=True, add_completion=False)


@app.command()
def init(directory: Path = typer.Argument(Path("."), help="Project directory")):
    directory = directory.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "config.yaml"
    if target.exists():
        raise typer.BadParameter(f"Config already exists: {target}")
    target.write_text(yaml.safe_dump(default_config(), sort_keys=False))
    (directory / "genomes").mkdir(exist_ok=True)
    typer.echo(f"Created {target} and genomes/")


@app.command()
def doctor():
    """Check executables and installed databases (no project config required)."""
    missing = []
    for name in ("snakemake", "abricate", "mob_recon"):
        found = shutil.which(name)
        typer.echo(f"{name}: {found or 'MISSING'}")
        if not found:
            missing.append(name)
    if missing:
        typer.echo("Missing required commands: " + ", ".join(missing), err=True)
        raise typer.Exit(1)
    try:
        proc = subprocess.run(["abricate", "--list"], capture_output=True, text=True,
                              check=True)
        typer.echo(proc.stdout)
        lower = proc.stdout.lower()
        for db in ("resfinder", "vfdb", "plasmidfinder"):
            if db not in lower:
                typer.echo(f"WARNING: ABRicate database {db} not listed", err=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        typer.echo(f"ABRicate database inspection failed: {exc}", err=True)
        raise typer.Exit(1)
    typer.echo("NOTE: MOB-suite database readiness must be verified during a real analysis.")


@app.command()
def qc(
    config: Path = typer.Option(..., "--config", "-c"),
):
    cfg = load_config(config)
    samples = discover([cfg["input"]["genomes"]])
    rows = []
    for sample, path in samples.items():
        data = metrics(path)
        status, reason = assess(data, cfg["quality"])
        rows.append({"sample": sample, "input_fasta": path,
                     **data, "status": status, "reasons": reason})
    destination = Path(cfg["project"]["output"]) / "02_quality/quality_summary.tsv"
    write_tsv(destination, rows,
              ["sample", "input_fasta", "genome_size", "contigs", "n50", "gc", "status", "reasons"])
    typer.echo(f"QC results: {destination}; passing {sum(x['status']=='PASS' for x in rows)}/{len(rows)}")


@app.command()
def run(
    config: Path = typer.Option(..., "--config", "-c"),
    cores: int = typer.Option(4, "--cores", min=1),
    dry_run: bool = typer.Option(False, "--dry-run"),
    keep_going: bool = typer.Option(False, "--keep-going"),
):
    cfg = load_config(config)
    samples = discover([cfg["input"]["genomes"]])
    out = Path(cfg["project"]["output"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    meta = out / "00_metadata"
    meta.mkdir(exist_ok=True)
    manifest = meta / "samples.json"
    manifest.write_text(json.dumps(samples, indent=2))
    cfg["_manifest"] = str(manifest)
    effective = meta / "resolved_config.yaml"
    effective.write_text(yaml.safe_dump(cfg, sort_keys=False))
    snakefile = files("chromoplas").joinpath("workflow/Snakefile")
    cmd = ["snakemake", "--snakefile", str(snakefile), "--configfile", str(effective),
           "--directory", str(out), "--cores", str(cores), "--printshellcmds",
           "07_reports/report.html"]
    if dry_run:
        cmd.append("--dry-run")
    if keep_going:
        cmd.append("--keep-going")
    typer.echo("Executing: " + " ".join(cmd))
    try:
        result = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        typer.echo("Snakemake not found in environment", err=True)
        raise typer.Exit(127)
    raise typer.Exit(result.returncode)


@app.command("analyze")
def analyze(
    inputs: list[Path] = typer.Argument(..., help="Assembled FASTA files or directories"),
    output: Path = typer.Option(..., "--output", "-o", help="New or existing results folder"),
    threads: int = typer.Option(4, "--threads", "-t", min=1),
    config: Path | None = typer.Option(None, "--config", "-c"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    keep_going: bool = typer.Option(False, "--keep-going"),
):
    """Analyze genomes independently; no pangenome or across-isolate comparisons."""
    from tempfile import TemporaryDirectory
    from .inputs import is_fasta
    try:
        samples = discover(inputs)
    except ValueError as exc:
        typer.echo(f"Input error: {exc}", err=True)
        raise typer.Exit(2)
    out = output.expanduser().resolve()
    for path in samples.values():
        input_path = Path(path)
        if out == input_path or out in input_path.parents:
            typer.echo("Input FASTAs must be outside the output directory", err=True)
            raise typer.Exit(2)
    out.mkdir(parents=True, exist_ok=True)
    staged = out / "00_metadata" / "input_links"
    staged.mkdir(parents=True, exist_ok=True)
    # Ensure a rerun cannot silently include previous cohort's FASTA files.
    expected = {Path(p).name for p in samples.values()}
    for entry in staged.iterdir():
        if entry.is_symlink() and entry.name not in expected:
            entry.unlink()
        elif entry.name not in expected:
            typer.echo(f"Unexpected file in staged inputs: {entry}", err=True)
            raise typer.Exit(2)
    for path in samples.values():
        source = Path(path)
        link = staged / source.name
        if link.is_symlink() and link.resolve() == source:
            continue
        if link.exists() or link.is_symlink():
            typer.echo(f"Conflicting staged filename: {link}", err=True)
            raise typer.Exit(2)
        link.symlink_to(source)
    with TemporaryDirectory(prefix="chromoplas-") as temporary:
        cfg = load_config(config) if config else default_config()
        cfg["input"]["genomes"] = str(staged)
        cfg["project"]["output"] = str(out)
        cfg["resources"]["threads_per_job"] = min(
            threads, max(1, int(cfg["resources"].get("threads_per_job", 2))))
        tmp_config = Path(temporary) / "config.yaml"
        tmp_config.write_text(yaml.safe_dump(cfg, sort_keys=False))
        run(tmp_config, threads, dry_run, keep_going)


def main():
    if len(sys.argv) > 1:
        known = {"analyze", "run", "init", "qc", "doctor"}
        if sys.argv[1] not in known and not sys.argv[1].startswith("-"):
            sys.argv.insert(1, "analyze")
    app()


if __name__ == "__main__":
    main()
