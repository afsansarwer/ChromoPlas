"""Build a deterministic, self-contained analysis source payload on any platform."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parent.parent


def prepare(root=ROOT):
    target = root / "desktop/assets"
    target.mkdir(parents=True, exist_ok=True)
    paths = [root / p for p in ("pyproject.toml", "README.md", "LICENSE", "INSTALL.sh",
                                "scripts/check-install.sh", "examples/genomes/test_isolate.fna",
                                "desktop/linux/worker.py")]
    paths += [p for p in (root / "src/chromoplas").rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    archive = target / "source.tar.gz"
    with archive.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tar:
            for path in sorted(paths):
                data = path.read_bytes().replace(b"\r\n", b"\n")
                info = tarfile.TarInfo(path.relative_to(root).as_posix())
                info.size = len(data)
                info.mode = 0o755 if path.suffix == ".sh" else 0o644
                info.mtime = 0
                tar.addfile(info, io.BytesIO(data))
    (target / "bootstrap.sh").write_bytes((root / "desktop/linux/bootstrap.sh").read_bytes().replace(b"\r\n", b"\n"))
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True,
                                capture_output=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "source-bundle"
    metadata = {"schema": 1, "desktop_version": "0.1.0", "source_commit": commit,
                "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
    (target / "payload.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
