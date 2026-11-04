"""Release-gate tests for reporting, missing data and source provenance."""
import json
import re
from pathlib import Path
from unittest.mock import patch
import pytest
from typer.testing import CliRunner

from chromoplas.cli import app
from chromoplas.localization import summarize
from chromoplas.matrix import gene_localization_matrix
from chromoplas.provenance import create_provenance


def test_doctor_fails_if_required_database_missing():
    from types import SimpleNamespace
    from unittest.mock import Mock
    subprocess_result = SimpleNamespace(returncode=0, stdout="DATABASE\tSEQUENCES\nresfinder\t100\nvfdb\t200\n", stderr="")
    with patch("chromoplas.cli.shutil.which", return_value="/usr/bin/tool"), patch(
        "chromoplas.cli.subprocess.run", return_value=subprocess_result
    ):
        response = CliRunner().invoke(app, ["doctor"])
    assert response.exit_code != 0
    assert "plasmidfinder" in response.output


def test_unresolved_evidence_not_labeled_exclusive():
    hits = [
        {"feature_class":"ARG", "feature_name":"tet(M)", "location":"chromosome", "plasmid_group":""},
        {"feature_class":"ARG", "feature_name":"tet(M)", "location":"unresolved", "plasmid_group":""},
    ]
    result = summarize("fixture", hits)[0]
    assert result["localization"] == "chromosome_and_unresolved"
    assert result["unresolved_hits"] == 1


def test_matrix_uses_actual_summary_and_remains_svg(tmp_path):
    rows = [{"feature_class":"ARG", "feature_name":"tet(M)",
             "chromosome_hits":1, "plasmid_hits":0, "unresolved_hits":1}]
    path = gene_localization_matrix("demo", rows, tmp_path/"matrix.svg")
    import xml.etree.ElementTree as ET
    ET.parse(path)
    assert "tet(M)" in path.read_text()
    assert "Showing 1 / 1" in path.read_text()


def test_provenance_hashes_inputs_and_captures_versions(tmp_path):
    fasta = tmp_path/"sample.fna"
    fasta.write_text(">ctg\nACGT\n")
    dest = tmp_path/"provenance.json"
    with patch("chromoplas.provenance._command", return_value={"status":"unavailable"}) as mocked:
        create_provenance(dest, {"sample":str(fasta)}, {"abricate":{"databases":["resfinder"]}})
    info = json.loads(dest.read_text())
    assert info["inputs"]["sample"]["sha256"] == __import__("hashlib").sha256(fasta.read_bytes()).hexdigest()
    assert info["chromoplas_git_commit"] is None
    assert "tools" in info


def test_missing_mge_report_is_unknown_not_zero(tmp_path):
    from chromoplas.qc import write_tsv, read_tsv
    from chromoplas.report import generate_report
    root = tmp_path / "results"
    write_tsv(root / "02_quality/quality_summary.tsv", [
        {"sample": "s1", "status": "PASS", "reasons": "",
         "genome_size": 1500, "contigs": 1, "n50": 1500, "gc": 50}
    ], ["sample", "status", "reasons", "genome_size", "contigs", "n50", "gc"])
    generate_report(root, ["s1"])
    record = read_tsv(root / "07_reports/master_summary.tsv")[0]
    assert record["mge_evidence_status"] == "not_reported"
    assert record["mge_hits"] == "NA"
    generate_report(root, ["s1"], plasmids_enabled=False)
    record = read_tsv(root / "07_reports/master_summary.tsv")[0]
    assert record["mge_evidence_status"] == "not_run"
    assert record["mge_hits"] == "NA"


def test_unmappable_mge_rows_are_not_called_zero(tmp_path):
    from chromoplas.qc import write_tsv, read_tsv
    from chromoplas.report import generate_report
    root = tmp_path / "results"
    write_tsv(root / "02_quality/quality_summary.tsv", [
        {"sample": "s1", "status": "PASS", "reasons": "",
         "genome_size": 1500, "contigs": 1, "n50": 1500, "gc": 50}
    ], ["sample", "status", "reasons", "genome_size", "contigs", "n50", "gc"])
    mge = root / "05_plasmids/s1/mge.report.txt"
    mge.parent.mkdir(parents=True)
    mge.write_text(
        "contig_id\\tcontig_start\\tcontig_end\\tmge_id\\n"
        "missing_contig\\t10\\t30\\tIS26\\n"
    )
    generate_report(root, ["s1"])
    rec = read_tsv(root / "07_reports/master_summary.tsv")[0]
    assert rec["mge_evidence_status"] == "coordinate_rows_unmapped"
    assert rec["mge_hits"] == "NA"
