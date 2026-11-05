"""Desktop safety and orchestration tests. These do not pretend to test live WSL."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
from types import SimpleNamespace

import pytest

from desktop import core
from desktop.linux import worker
from desktop.prepare_payload import prepare


@pytest.mark.parametrize(("value", "expected"), [
    (r"C:\Genomes\one.fna", "/mnt/c/Genomes/one.fna"),
    (r"E:\My data\Bangla বাংলা\a 'quote' $x;.fna", "/mnt/e/My data/Bangla বাংলা/a 'quote' $x;.fna"),
    ("D:/assemblies/test.fasta.gz", "/mnt/d/assemblies/test.fasta.gz"),
])
def test_local_paths_are_data(value, expected):
    assert core.windows_to_linux(value) == expected


@pytest.mark.parametrize("value", [r"\\server\share\input.fna", "relative.fna", "C:relative.fna",
                                        "C:/a/../b.fna", "C:/file:stream", "C:/a\n.fna"])
def test_unsupported_windows_paths_fail(value):
    with pytest.raises(core.DesktopError):
        core.windows_to_linux(value)


def test_wsl_utf16_management_output():
    assert core.decode_output("Ubuntu\r\n".encode("utf-16-le")) == "Ubuntu\r\n"
    assert core.decode_output("বাংলা".encode()) == "বাংলা"


def test_duplicate_normalized_sample_names_fail(tmp_path):
    first, second = tmp_path / "a b.fna", tmp_path / "a_b.fasta"
    for path in (first, second):
        path.write_text(">contig\nACGT\n")
    with pytest.raises(core.DesktopError, match="Ambiguous sample"):
        core.validate_inputs([str(first), str(second)])


def test_raw_reads_and_empty_selection_fail(tmp_path):
    reads = tmp_path / "reads.fastq"
    reads.write_text("@read\nACGT\n+\n!!!!\n")
    for paths in ([], [str(reads)]):
        with pytest.raises(core.DesktopError):
            core.validate_inputs(paths)


class Response(io.BytesIO):
    def geturl(self):
        return "https://example.org/rootfs.tar.gz"


def test_verified_download_and_cache(tmp_path, monkeypatch):
    content = b"a tiny test download"
    expected = hashlib.sha256(content).hexdigest()
    calls = []
    def urlopen(*args, **kwargs):
        calls.append(args)
        return Response(content)
    monkeypatch.setattr(core.urllib.request, "urlopen", urlopen)
    path = tmp_path / "image.tar.gz"
    core.download_verified("https://example.org/image", path, expected, lambda _: None)
    core.download_verified("https://example.org/image", path, expected, lambda _: None)
    assert path.read_bytes() == content
    assert len(calls) == 1


def test_corrupt_download_never_becomes_importable(tmp_path, monkeypatch):
    monkeypatch.setattr(core.urllib.request, "urlopen", lambda *a, **kw: Response(b"corrupt"))
    monkeypatch.setattr(core.time, "sleep", lambda _: None)
    path = tmp_path / "image.tar.gz"
    with pytest.raises(core.DesktopError, match="checksum"):
        core.download_verified("https://example.org/image", path, "0" * 64, lambda _: None)
    assert not path.exists()
    assert not path.with_suffix(".gz.part").exists()


def test_payload_is_deterministic_and_has_no_private_or_build_files():
    root = Path(__file__).resolve().parents[1]
    first = prepare(root)
    archive = (root / "desktop/assets/source.tar.gz").read_bytes()
    second = prepare(root)
    assert first["sha256"] == second["sha256"]
    assert archive == (root / "desktop/assets/source.tar.gz").read_bytes()
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        names = tar.getnames()
    assert "src/chromoplas/workflow/Snakefile" in names
    assert "desktop/linux/worker.py" in names
    assert "LICENSE" in names
    assert not any(".git/" in p or "__pycache__" in p or ".venv" in p for p in names)
    assert all(not p.startswith("/") and ".." not in Path(p).parts for p in names)


def test_corrupt_bundled_source_blocks_setup_before_wsl(tmp_path, monkeypatch):
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "payload.json").write_text(json.dumps({"sha256": "0" * 64}))
    (assets / "source.tar.gz").write_bytes(b"bad source")
    backend = core.Backend(data_dir=tmp_path / "data", assets_dir=assets)
    monkeypatch.setattr(backend, "_check_platform", lambda: None)
    monkeypatch.setattr(backend, "_ensure_wsl", lambda: pytest.fail("WSL must not be changed"))
    with pytest.raises(core.DesktopError, match="integrity"):
        backend.setup()


def test_unrelated_distro_is_not_modified(tmp_path, monkeypatch):
    backend = core.Backend(data_dir=tmp_path / "ours")
    monkeypatch.setattr(backend, "_registered_path", lambda: tmp_path / "someone-elses-engine")
    monkeypatch.setattr(backend, "_host", lambda *a, **k: pytest.fail("Must not execute commands there"))
    with pytest.raises(core.DesktopError, match="unrelated"):
        backend._assert_owned()


def test_stop_only_terminates_the_managed_distro(tmp_path, monkeypatch):
    backend = core.Backend(data_dir=tmp_path)
    calls = []
    monkeypatch.setattr(backend, "_assert_owned", lambda: None)
    monkeypatch.setattr(backend, "_host", lambda args: calls.append(args))
    backend.stop()
    assert calls == [[backend.wsl, "--terminate", core.DISTRO]]
    assert backend.stopping


def test_stream_propagates_nonzero_exit_without_shell(tmp_path, monkeypatch):
    calls = []
    class Input(io.BytesIO):
        def close(self):
            self.saved = self.getvalue()
            super().close()
    proc = SimpleNamespace(stdin=Input(), stdout=io.BytesIO(b"failure details\n"), wait=lambda: 9)
    def popen(args, **kwargs):
        calls.append((args, kwargs))
        return proc
    monkeypatch.setattr(core.subprocess, "Popen", popen)
    backend = core.Backend(data_dir=tmp_path, log=lambda _: None)
    with pytest.raises(core.DesktopError, match="failure details"):
        backend._stream(["wsl.exe", "--exec", "python"], b'{"path":"a;$x"}')
    assert not calls[0][1].get("shell", False)
    assert proc.stdin.saved == b'{"path":"a;$x"}'


@pytest.mark.parametrize("patch", [
    {"run_id": "../../other"}, {"threads": 0}, {"threads": True},
    {"destination": "/home/chromoplas/source"}, {"inputs": ["/etc/passwd"]},
])
def test_worker_rejects_unsafe_requests(patch):
    request = {"run_id": "a" * 32, "threads": 2, "inputs": ["/mnt/c/one.fna"],
               "destination": "/mnt/c/result"}
    request.update(patch)
    with pytest.raises(ValueError):
        worker.validate_request(request)


@pytest.mark.parametrize(("code", "qc_failed", "report", "expected"), [
    (0, False, True, "complete"), (2, True, True, "qc_failed"),
    (1, False, False, "failed"), (0, False, False, "failed"),
    (2, False, True, "failed"),
])
def test_worker_exports_self_contained_results_and_honest_status(
        tmp_path, monkeypatch, code, qc_failed, report, expected):
    original = tmp_path / "input.fna"
    original.write_text(">contig\nACGT\n")
    destination = tmp_path / "windows-result"
    ready = tmp_path / "ready.json"
    ready.write_text('{"schema":1}')
    jobs = tmp_path / "jobs"
    events = []
    monkeypatch.setattr(worker, "READY", ready)
    monkeypatch.setattr(worker, "JOBS", jobs)
    monkeypatch.setattr(worker, "validate_request", lambda _: ([original], destination))
    monkeypatch.setattr(worker, "check_engine", lambda: tmp_path)
    monkeypatch.setattr(worker, "database_inventory", lambda _: {"test_db": "v1"})
    monkeypatch.setattr(worker, "event", lambda **values: events.append(values))
    class Pipeline:
        def __init__(self, args, **kwargs):
            results = Path(args[args.index("--output") + 1])
            summary = results / "02_quality/quality_summary.tsv"
            summary.parent.mkdir()
            summary.write_text("sample\tstatus\ninput\t" + ("FAIL" if qc_failed else "PASS") + "\n")
            if report:
                page = results / "07_reports/report.html"
                page.parent.mkdir()
                page.write_text("<html>test report</html>")
            # Mimic ChromoPlas's Linux input symlink; the exported file must be portable.
            if os.name == "nt":
                # Local Windows builders need no symlink privilege; the Linux
                # run of this test exercises actual pipeline-style symlinks.
                shutil.copy2(original, results / "original.fna")
            else:
                (results / "original.fna").symlink_to(original)
            self.stdout = io.StringIO("localrule qc_sample:\n")
        def wait(self):
            return code
    monkeypatch.setattr(worker.subprocess, "Popen", Pipeline)
    request = {"run_id": "a" * 32, "threads": 2}
    if expected == "failed":
        with pytest.raises(RuntimeError, match="exited"):
            worker.analyze(request)
    else:
        worker.analyze(request)
    assert any(item.get("status") == expected for item in events)
    assert (destination / "analysis.log").is_file()
    exported = destination / "original.fna"
    assert not exported.is_symlink()
    assert exported.read_bytes() == original.read_bytes()
    assert (jobs / request["run_id"]).exists() == (expected == "failed")
    assert original.read_text() == ">contig\nACGT\n"
