from genomeflow.qc import metrics, assess
from genomeflow.cli import discover


def test_metrics(tmp_path):
    (tmp_path / "a.fna").write_text(">c1\nGCGCAA\n>c2\nATAT\n")
    m = metrics(tmp_path / "a.fna")
    assert (m["genome_size"], m["contigs"], m["n50"], m["gc"]) == (10, 2, 6, 40.0)
    assert assess(m, {"min_genome_size": 5, "max_genome_size": 20,
                      "max_contigs": 5, "min_n50": 5, "min_gc": 0, "max_gc": 100}) == ("PASS", "")


def test_duplicate_detection(tmp_path):
    (tmp_path / "sample.fa").write_text(">x\nAT\n")
    (tmp_path / "sample.fna").write_text(">x\nAT\n")
    import pytest
    with pytest.raises(ValueError, match="duplicate"):
        discover(tmp_path)
