"""Windows orchestration. No GUI dependency; subprocesses never use shell=True."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import uuid

DISTRO = "ChromoPlas-Desktop-v1"
OWNER = "chromoplas-desktop-v1"
ENGINE_PYTHON = "/home/chromoplas/miniforge3/envs/chromoplas/bin/python"
WORKER = "/opt/chromoplas/current/desktop/linux/worker.py"
ROOTFS_URL = ("https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/"
              "ubuntu-base-24.04.5-base-amd64.tar.gz")
ROOTFS_SHA256 = "e77b6f10c2590cef872b33ee9f635a0e3fd1f57fb074c0e52b5c7f56147a0c86"
FASTA_SUFFIXES = (".fasta.gz", ".fna.gz", ".fa.gz", ".fasta", ".fna", ".fa")
EVENT_PREFIX = "CHROMOPLAS_EVENT "


class DesktopError(RuntimeError):
    pass


class RestartRequired(DesktopError):
    pass


def decode_output(data: bytes) -> str:
    # WSL's management commands use UTF-16LE on some Windows versions.
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="replace")
    if b"\x00" in data:
        return data.decode("utf-16-le", errors="replace").lstrip("\ufeff")
    return data.decode("utf-8", errors="replace")


def windows_to_linux(value: str | Path) -> str:
    """Dedicated distro uses the standard /mnt/<drive> automount configuration."""
    raw = str(value)
    path = PureWindowsPath(raw)
    if (not path.is_absolute() or not re.fullmatch(r"[A-Za-z]:", path.drive)
            or raw.startswith(("\\\\", "//")) or any(c in raw for c in "\x00\r\n")):
        raise DesktopError("Choose a local drive path such as C:\\Genomes; network/UNC paths are unsupported.")
    if any(part in (".", "..") or ":" in part for part in path.parts[1:]):
        raise DesktopError("Choose a normal local path without parent traversal or alternate data streams.")
    return "/mnt/" + path.drive[0].lower() + "/" + "/".join(path.parts[1:])


def validate_inputs(paths: list[str]) -> list[Path]:
    if not paths:
        raise DesktopError("Select at least one assembled FASTA file.")
    result, sample_names, file_names = [], set(), set()
    for value in dict.fromkeys(paths):
        path = Path(value).resolve()
        suffix = next((s for s in FASTA_SUFFIXES if path.name.lower().endswith(s)), None)
        if not path.is_file() or suffix is None:
            raise DesktopError(f"Not an assembled FASTA file: {path.name}")
        sample = re.sub(r"[^A-Za-z0-9_-]", "_", path.name[:-len(suffix)])
        if not sample or sample in sample_names or path.name.casefold() in file_names:
            raise DesktopError(f"Ambiguous sample name: {path.name}. Rename files so sample names are unique.")
        sample_names.add(sample)
        file_names.add(path.name.casefold())
        result.append(path)
    return result


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_verified(url: str, path: Path, expected: str, log=print) -> None:
    if not url.startswith("https://") or not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise DesktopError("Invalid download specification.")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and sha256_file(path) == expected:
        log("Using verified cached Linux image.")
        return
    temporary = path.with_suffix(path.suffix + ".part")
    last_error = None
    for attempt in range(3):
        try:
            log(f"Downloading Linux image (attempt {attempt + 1}/3)...")
            request = urllib.request.Request(url, headers={"User-Agent": "ChromoPlas-Desktop/0.1"})
            with urllib.request.urlopen(request, timeout=30) as source, temporary.open("wb") as target:
                if not source.geturl().startswith("https://"):
                    raise DesktopError("The download redirected to an insecure address.")
                count, announced = 0, 0
                while block := source.read(1024 * 1024):
                    target.write(block)
                    count += len(block)
                    if count - announced >= 8 * 1024 * 1024:
                        log(f"Linux image: {count // (1024 * 1024)} MiB downloaded")
                        announced = count
            if sha256_file(temporary) != expected:
                raise DesktopError("Linux image checksum mismatch. Import was blocked.")
            temporary.replace(path)
            return
        except (OSError, DesktopError) as exc:
            last_error = exc
            temporary.unlink(missing_ok=True)
            if attempt < 2:
                time.sleep(attempt + 1)
    raise DesktopError(f"Download failed after three attempts: {last_error}")


class Backend:
    def __init__(self, log=print, event=None, data_dir: Path | None = None,
                 assets_dir: Path | None = None):
        self.log = log
        self.event = event or (lambda item: None)
        self.data = data_dir or Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "ChromoPlas"
        self.data.mkdir(parents=True, exist_ok=True)
        self.assets = assets_dir or (Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
                                    / "desktop" / "assets")
        self.distro_dir = self.data / "engine"
        self.wsl = str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "wsl.exe")
        self.stopping = False

    def _host(self, args: list[str], timeout=30, check=True) -> str:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    timeout=timeout, creationflags=flags, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise DesktopError(f"Command could not finish: {exc}") from exc
        output = decode_output(result.stdout)
        if check and result.returncode:
            raise DesktopError(f"Command exited with code {result.returncode}:\n{output.strip()}")
        return output

    def _stream(self, args: list[str], data: bytes = b"") -> str:
        """Drain output continuously; WSL exec commands emit Linux UTF-8."""
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, creationflags=flags)
        except OSError as exc:
            raise DesktopError(str(exc)) from exc
        try:
            proc.stdin.write(data)
            proc.stdin.close()
            tail = []
            for raw in proc.stdout:
                line = raw.decode("utf-8", errors="replace").rstrip()
                self.log(line)
                tail = (tail + [line])[-40:]
                if line.startswith(EVENT_PREFIX):
                    try:
                        self.event(json.loads(line[len(EVENT_PREFIX):]))
                    except ValueError:
                        pass
            code = proc.wait()
        except BaseException:
            proc.kill()
            proc.wait()
            raise
        finally:
            proc.stdout.close()
        if code:
            if self.stopping:
                raise DesktopError("Analysis stopped. The log and partial Linux working files were kept.")
            raise DesktopError(f"Analysis environment command failed ({code}).\n" + "\n".join(tail[-12:]))
        return "\n".join(tail)

    def _linux(self, args: list[str], user="root") -> list[str]:
        return [self.wsl, "--distribution", DISTRO, "--user", user, "--exec", *args]

    def _check_platform(self):
        if sys.platform != "win32" or platform.machine().lower() not in ("amd64", "x86_64"):
            raise DesktopError("This installer supports Windows x64 on Intel/AMD processors. Windows ARM is unsupported.")
        if sys.getwindowsversion().build < 19045:
            raise DesktopError("Windows 11 or Windows 10 22H2 (build 19045+) is required.")

    def _ensure_wsl(self):
        try:
            self._host([self.wsl, "--status"])
            return
        except DesktopError:
            self.log("Enabling WSL2. Windows will request administrator approval.")
        # Elevate only system-feature installation, never per-user distro import.
        command = ("$ErrorActionPreference='Stop'; "
                   "$p=Start-Process -FilePath ($env:SystemRoot+'\\System32\\wsl.exe') "
                   "-ArgumentList '--install','--no-distribution','--web-download' "
                   "-Verb RunAs -Wait -PassThru; exit $p.ExitCode")
        try:
            self._host(["powershell.exe", "-NoProfile", "-Command", command], timeout=1800)
        except DesktopError as exc:
            # WSL may return a reboot-required status rather than zero.
            self.log(str(exc))
        raise RestartRequired(
            "WSL2 setup was requested. If Windows reported success, restart Windows, reopen ChromoPlas "
            "and click Set up engine again. If approval was declined or installation failed, check the log. "
            "Virtualization must be enabled in BIOS/UEFI; managed PCs may require your administrator.")

    def _registered_path(self) -> Path | None:
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Lxss") as root:
                for index in range(winreg.QueryInfoKey(root)[0]):
                    with winreg.OpenKey(root, winreg.EnumKey(root, index)) as key:
                        if winreg.QueryValueEx(key, "DistributionName")[0] == DISTRO:
                            raw = winreg.QueryValueEx(key, "BasePath")[0]
                            if raw.startswith("\\\\?\\"):
                                raw = raw[4:]
                            return Path(raw).resolve()
        except FileNotFoundError:
            return None
        return None

    def _assert_owned(self):
        if self._registered_path() != self.distro_dir.resolve():
            raise DesktopError(f"{DISTRO} is missing or registered elsewhere. Refusing to modify an unrelated environment.")
        marker = self._host(self._linux(["cat", "/etc/chromoplas-desktop-owner"]))
        if marker.strip() != OWNER:
            raise DesktopError("The engine ownership check failed. No repair or removal was attempted.")

    def setup(self):
        self._check_platform()
        if not (self.assets / "payload.json").is_file():
            raise DesktopError("Build payload missing. Run python desktop/prepare_payload.py before starting from source.")
        manifest = json.loads((self.assets / "payload.json").read_text(encoding="utf-8"))
        archive = self.assets / "source.tar.gz"
        if sha256_file(archive) != manifest["sha256"]:
            raise DesktopError("Bundled analysis source failed its integrity check.")
        self._ensure_wsl()
        registered = self._registered_path()
        if registered is None:
            # A planning allowance, not a measured peak requirement.
            if shutil.disk_usage(self.data).free < 25 * 1024**3:
                raise DesktopError("Keep at least 25 GiB free on the installation drive for setup, databases and temporary files.")
            rootfs = self.data / "downloads" / "ubuntu-base-24.04.5-amd64.tar.gz"
            download_verified(ROOTFS_URL, rootfs, ROOTFS_SHA256, self.log)
            self.distro_dir.mkdir(parents=True, exist_ok=True)
            self.log("Creating ChromoPlas's dedicated WSL2 environment...")
            self._host([self.wsl, "--import", DISTRO, str(self.distro_dir), str(rootfs), "--version", "2"], timeout=600)
            # Registry location is checked before even the ownership marker is written.
            if self._registered_path() != self.distro_dir.resolve():
                raise DesktopError("Imported environment has an unexpected location; setup stopped.")
            self._stream(self._linux(["bash", "-s"]),
                         f"printf '%s\\n' '{OWNER}' > /etc/chromoplas-desktop-owner\n".encode())
        self._assert_owned()
        self.log("Installing analysis tools and reference databases. This can take a long time on first setup.")
        encoded = base64.b64encode(windows_to_linux(archive).encode()).decode()
        self._stream(self._linux(["bash", "-s", "--", encoded, manifest["sha256"]]),
                     (self.assets / "bootstrap.sh").read_bytes())
        self.probe()
        self.log("Analysis engine is ready.")

    def probe(self):
        self._assert_owned()
        manifest = json.loads((self.assets / "payload.json").read_text(encoding="utf-8"))
        self._stream(self._linux([ENGINE_PYTHON, WORKER], user="chromoplas"),
                     json.dumps({"action": "probe", "payload_sha256": manifest["sha256"]}).encode())

    def analyze(self, values: list[str], parent: str, threads: int):
        self.stopping = False
        inputs = validate_inputs(values)
        if not 1 <= threads <= 256:
            raise DesktopError("CPU threads must be between 1 and 256.")
        destination_parent = Path(parent).resolve()
        destination_parent.mkdir(parents=True, exist_ok=True)
        run_id = uuid.uuid4().hex
        destination = destination_parent / (time.strftime("ChromoPlas-%Y%m%d-%H%M%S-") + run_id[:8])
        request = {"action": "analyze", "inputs": [windows_to_linux(p) for p in inputs],
                   "destination": windows_to_linux(destination), "threads": threads, "run_id": run_id}
        self.log(f"Results for this run: {destination}")
        self.probe()
        if self.stopping:
            raise DesktopError("Analysis stopped before launch.")
        self._stream(self._linux([ENGINE_PYTHON, WORKER], user="chromoplas"), json.dumps(request).encode())
        return destination

    def stop(self):
        self._assert_owned()
        self.stopping = True
        # Only this application's dedicated distro; never wsl --shutdown.
        self._host([self.wsl, "--terminate", DISTRO])
