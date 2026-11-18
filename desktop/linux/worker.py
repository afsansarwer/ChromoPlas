"""Runs in Linux. One JSON request on stdin; structured events on stdout."""
from __future__ import annotations

import csv
import gzip
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

PREFIX = "CHROMOPLAS_EVENT "
READY = Path("/opt/chromoplas/ready.json")
JOBS = Path("/home/chromoplas/jobs")
STAGES = {"qc_sample": "Checking assembly quality", "select_hq": "Selecting assemblies that passed QC",
          "screen_genome": "Screening resistance, virulence and replicon genes",
          "reconstruct_plasmids": "Reconstructing plasmids with MOB-suite",
          "localize_sample": "Mapping genes and drawing figures", "generate_report": "Generating report"}


def event(**values):
    print(PREFIX + json.dumps(values), flush=True)


def engine_env():
    env = os.environ.copy()
    env["PATH"] = str(Path(sys.executable).parent) + ":/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
    env["PYTHONUNBUFFERED"] = "1"
    env["LC_ALL"] = "C.UTF-8"
    return env


def check_engine():
    subprocess.run([str(Path(sys.executable).with_name("chromoplas")), "doctor"],
                   env=engine_env(), check=True)
    from mob_suite.constants import default_database_dir
    directory = Path(default_database_dir)
    required = ("status.txt", "ncbi_plasmid_full_seqs.fas.msh", "ncbi_plasmid_full_seqs.fas")
    missing = [name for name in required if not (directory / name).is_file() or (directory / name).stat().st_size == 0]
    if missing:
        raise RuntimeError("MOB-suite database is incomplete: " + ", ".join(missing))
    return directory


def validate_request(request):
    run_id = request.get("run_id", "")
    if not re.fullmatch(r"[a-f0-9]{32}", run_id):
        raise ValueError("Invalid analysis identifier")
    threads = request.get("threads")
    if type(threads) is not int or not 1 <= threads <= 256:
        raise ValueError("Invalid thread count")
    inputs = [Path(p) for p in request.get("inputs", [])]
    destination = Path(request["destination"])
    for path in [*inputs, destination]:
        if not path.is_absolute() or not re.match(r"^/mnt/[a-z]/", str(path)) or ".." in path.parts:
            raise ValueError("Only local Windows drive paths are supported")
    if not inputs or destination.exists():
        raise ValueError("Inputs are empty or the result directory already exists")
    names = set()
    for path in inputs:
        if not path.is_file():
            raise ValueError(f"Input is missing: {path.name}")
        if path.name.casefold() in names:
            raise ValueError(f"Duplicate filename: {path.name}")
        names.add(path.name.casefold())
        opener = gzip.open if str(path).lower().endswith(".gz") else open
        with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
            # A quick format check; full sequence QC is still performed by ChromoPlas.
            first = next((line.strip() for line in handle if line.strip()), "")
            if not first.startswith(">"):
                raise ValueError(f"Expected an assembled FASTA header in {path.name}; FASTQ is unsupported")
    return inputs, destination


def qc_all_failed(results: Path) -> bool:
    summary = results / "02_quality/quality_summary.tsv"
    if not summary.is_file():
        return False
    with summary.open() as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return bool(rows) and all(row.get("status") != "PASS" for row in rows)


def database_inventory(directory: Path):
    # Sizes and mtimes are cheap enough for every run; don't hash multi-GB DBs repeatedly.
    files = [{"name": p.name, "size": p.stat().st_size, "mtime": p.stat().st_mtime}
             for p in sorted(directory.iterdir()) if p.is_file()]
    listing = subprocess.run(["abricate", "--list"], env=engine_env(), capture_output=True,
                             text=True, check=True).stdout
    status = (directory / "status.txt").read_text(errors="replace")
    return {"mob_suite_files": files, "mob_suite_status": status, "abricate_databases": listing}


def analyze(request):
    inputs, destination = validate_request(request)
    db_dir = check_engine()
    JOBS.mkdir(parents=True, exist_ok=True)
    job = JOBS / request["run_id"]
    job.mkdir(mode=0o700)  # exclusive creation; never reuse another run's files
    staged, results = job / "inputs", job / "results"
    staged.mkdir()
    results.mkdir()
    event(stage="Copying assemblies into the Linux workspace")
    for path in inputs:
        shutil.copy2(path, staged / path.name)
    started = time.time()
    cmd = [str(Path(sys.executable).with_name("chromoplas")), "analyze", str(staged),
           "--output", str(results), "--threads", str(request["threads"])]
    event(stage="Starting analysis")
    with (results / "analysis.log").open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace", env=engine_env())
        for line in proc.stdout:
            print(line, end="", flush=True)
            log.write(line)
            match = re.search(r"(?:local)?rule (\w+):", line)
            if match and match[1] in STAGES:
                event(stage=STAGES[match[1]])
        code = proc.wait()
    record = {"run_id": request["run_id"], "inputs": [str(p) for p in inputs],
              "threads": request["threads"], "exit_code": code, "elapsed_seconds": time.time() - started,
              "engine": json.loads(READY.read_text()), "databases": database_inventory(db_dir)}
    (results / "desktop_run.json").write_text(json.dumps(record, indent=2))
    freeze = Path("/opt/chromoplas/conda-explicit.txt")
    if freeze.is_file():
        shutil.copy2(freeze, results / "conda-explicit.txt")
    event(stage="Saving results to your selected folder")
    # Resolve pipeline-created input symlinks into files so Windows outputs are self-contained.
    # The directory is new, and symlinks are never copied as Windows symlinks.
    shutil.copytree(results, destination, symlinks=False,
                    ignore=shutil.ignore_patterns(".snakemake"))
    report = destination / "07_reports/report.html"
    if code == 0 and report.is_file():
        event(status="complete", stage="Analysis complete")
    elif code == 2 and report.is_file() and qc_all_failed(results):
        event(status="qc_failed", stage="All assemblies were excluded by QC. Open the report for reasons.")
    else:
        event(status="failed", stage="Analysis failed; partial results and logs were saved")
        raise RuntimeError(f"ChromoPlas exited with code {code}. Inspect analysis.log in the results folder.")
    # Retain failed working files for diagnosis; remove only this successful job's staging.
    shutil.rmtree(job)


def main():
    if sys.argv[1:] == ["--check"]:
        check_engine()
        return
    request = json.load(sys.stdin)
    action = request.get("action")
    if not READY.is_file():
        raise RuntimeError("Setup is incomplete. Run Set up engine again.")
    if action == "probe":
        ready = json.loads(READY.read_text())
        if ready.get("payload_sha256") != request.get("payload_sha256"):
            raise RuntimeError("Engine version differs from the desktop app. Run Set up engine to update it.")
        check_engine()
        event(status="ready", stage="Analysis engine ready")
    elif action == "analyze":
        analyze(request)
    else:
        raise ValueError("Unknown action")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        event(status="error", stage=str(exc))
        print(f"ERROR: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
