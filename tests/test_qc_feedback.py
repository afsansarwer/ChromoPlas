"""QC-only runs must tell users why no figure/gene screening exists."""
from pathlib import Path

from chromoplas.cli import _qc_completion_summary
from chromoplas.qc import write_tsv, read_tsv
from chromoplas.report import generate_report


def _write_qc(root: Path, sample: str, status: str, reasons: str):
    write_tsv(root / "02_quality/quality_summary.tsv", [
        {"sample": sample, "status": status, "reasons": reasons,
         "genome_size": 3200000, "contigs": 800, "n50": 18000, "gc": 50}
    ], ["sample", "status", "reasons", "genome_size", "contigs", "n50", "gc"])


def test_qc_only_run_prints_reason_and_nonzero_exit(tmp_path, capsys):
    _write_qc(tmp_path, "fixture", "FAIL", "contigs_high")
    code = _qc_completion_summary(tmp_path)
    captured = capsys.readouterr()
    assert code == 2
    assert "0/1 PASS" in captured.out
    assert "contigs_high" in captured.err
    assert "NO GENOME ANALYZED" in captured.err
    assert "SVG figures were SKIPPED" in captured.err


def test_qc_only_report_has_no_false_zero_counts(tmp_path):
    _write_qc(tmp_path, "fixture", "FAIL", "contigs_high")
    generate_report(tmp_path, ["fixture"])
    row = read_tsv(tmp_path / "07_reports/master_summary.tsv")[0]
    assert row["qc_reasons"] == "contigs_high"
    for col in ("arg_hits", "vf_hits", "mge_hits", "plasmid_contigs",
                "chromosomal_contigs", "unresolved_contigs", "genes_in_both"):
        assert row[col] == "NA"
    html = (tmp_path / "07_reports/report.html").read_text()
    assert "No genomes passed assembly QC" in html
    assert "contigs_high" in html


def test_qc_pass_completion_returns_zero(tmp_path, capsys):
    _write_qc(tmp_path, "fixture", "PASS", "")
    assert _qc_completion_summary(tmp_path) == 0
    assert "1/1 PASS" in capsys.readouterr().out
