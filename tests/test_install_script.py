"""Installer smoke tests using mocked Conda: no network or real environment writes."""
import os
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("mode,expected_success", [("ok", True), ("create_fail", False)])
def test_conda_installer_stays_out_of_base(tmp_path, mode, expected_success):
    base = tmp_path / "fake_conda_base"
    base.mkdir()
    fake = tmp_path / "conda"
    log = tmp_path / "calls.txt"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$MOCK_LOG\"\n"
        "if [[ \"$1 $2\" == 'info --base' ]]; then echo \"$MOCK_BASE\"; exit 0; fi\n"
        "if [[ \"$1 $2\" == 'env list' ]]; then echo '# conda environments:'; exit 0; fi\n"
        "if [[ \"$1\" == 'create' && \"$MOCK_MODE\" == 'create_fail' ]]; then exit 23; fi\n"
        "if [[ \"$1\" == 'run' && \" $* \" == *' abricate --list '* ]]; then\n"
        "  printf 'DATABASE SEQUENCES\\nresfinder 100\\nvfdb 100\\nplasmidfinder 100\\n'; exit 0\n"
        "fi\n"
        "exit 0\n"
    )
    fake.chmod(0o755)
    env = {
        **os.environ,
        "CONDA_EXE": str(fake),
        "MOCK_BASE": str(base),
        "MOCK_LOG": str(log),
        "MOCK_MODE": mode,
    }
    result = subprocess.run(
        ["bash", str(ROOT / "INSTALL.sh")],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    calls = log.read_text()
    assert ("Installation finished successfully!" in result.stdout) == expected_success
    assert (result.returncode == 0) == expected_success
    assert "create -y -n chromoplas" in calls
    assert "mamba " not in calls.lower()
    if expected_success:
        assert "run --no-capture-output -n chromoplas python -m pip install --no-deps -e" in calls
        assert "run --no-capture-output -n chromoplas chromoplas doctor" in calls
    else:
        assert "python -m pip install" not in calls
        assert "Installation stopped" in result.stderr


def test_install_help_has_no_side_effects():
    result = subprocess.run(
        ["bash", str(ROOT / "INSTALL.sh"), "--help"],
        cwd=ROOT, capture_output=True, text=True, check=True
    )
    assert "Usage: bash INSTALL.sh" in result.stdout
    assert "base environment" in result.stdout
