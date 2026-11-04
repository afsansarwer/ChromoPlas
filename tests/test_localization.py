from pathlib import Path
import pytest

from chromoplas.qc import metrics, assess, contig_lengths, read_tsv
from chromoplas.inputs import discover
from chromoplas.localization import classify_contigs, read_abricate_features, summarize, localize
from chromoplas.visualization import architecture_svg
from chromoplas.report import generate_report


@pytest.fixture
def assembly(tmp_path):
    file = tmp_path / "sample.fna"
    file.write_text(">chr1 annotation\n" + "A" * 500 + "\n"
                    ">pl1\n" + "G" * 300 + "\n"
                    ">un1\n" + "C" * 100 + "\n")
    return file


@pytest.fixture
def reports(tmp_path, assembly):
    mob = tmp_path / "mob"
    mob.mkdir()
    (mob / "contig_report.txt").write_text(
        "sample_id\tcontig_id\tmolecule_type\tprimary_cluster_id\trep_type(s)\tpredicted_mobility\n"
        "sample\tchr1\tchromosome\t-\t-\t-\n"
        "sample\tpl1\tplasmid\tAD582\tIncF\tmobilizable\n"
    )
    (mob / "mge.report.txt").write_text(
        "contig_id\tcontig_start\tcontig_end\tmge_id\tmge_type\n"
        "pl1\t40\t75\tIS26\tIS\n"
    )
    ab = tmp_path / "abricate" / "resfinder"
    ab.mkdir(parents=True)
    (ab / "sample.tsv").write_text(
        "#FILE\tSEQUENCE\tSTART\tEND\tSTRAND\tGENE\t%IDENTITY\t%COVERAGE\n"
        "sample.fna\tchr1\t20\t60\t+\ttet(M)\t100\t100\n"
        "sample.fna\tpl1\t10\t30\t-\ttet(M)\t99\t95\n"
        "sample.fna\tun1\t1\t15\t+\term(B)\t98\t94\n"
    )
    return assembly, mob, ab.parent


def test_basic_qc(assembly):
    m = metrics(assembly)
    assert m["genome_size"] == 900
    assert m["contigs"] == 3
    assert m["n50"] == 500
    assert round(m["gc"]) == 44
    assert assess(m, {"min_genome_size": 100, "max_genome_size": 1000, "max_contigs": 10,
                      "min_n50": 500, "min_gc": 0, "max_gc": 100}) == ("PASS", "")
    assert assess(m, {"min_genome_size": 1000, "max_genome_size": 10000, "max_contigs": 10,
                      "min_n50": 500, "min_gc": 0, "max_gc": 100})[0] == "FAIL"


def test_no_duplicate_normalized_sample_name(tmp_path):
    for name in ("sample.fa", "sample.fna"):
        (tmp_path / name).write_text(">contig\nA\n")
    with pytest.raises(ValueError, match="duplicat"):
        discover([tmp_path])


def test_duplicate_contig_id_rejected(tmp_path):
    assembly = tmp_path / "broken.fna"
    assembly.write_text(">ctg\nAA\n>ctg\nTT\n")
    with pytest.raises(ValueError, match="duplicated FASTA contig ID"):
        contig_lengths(assembly)


def test_classification_not_forced_to_chromosome(reports):
    assembly, mob, _ = reports
    ctg = classify_contigs("sample", assembly, mob / "contig_report.txt")
    assert ctg["chr1"]["location"] == "chromosome"
    assert ctg["pl1"]["location"] == "plasmid"
    assert ctg["pl1"]["plasmid_group"] == "AD582"
    assert ctg["un1"]["location"] == "unresolved"


def test_both_and_unresolved_gene_localization(reports):
    assembly, mob, ab = reports
    contigs = classify_contigs("sample", assembly, mob / "contig_report.txt")
    features = read_abricate_features("sample", contigs, ab, {"resfinder": "ARG"})
    rows = {r["feature_name"]: r for r in summarize("sample", features)}
    assert rows["tet(M)"]["localization"] == "both"
    assert rows["tet(M)"]["chromosome_hits"] == 1
    assert rows["tet(M)"]["plasmid_hits"] == 1
    assert rows["erm(B)"]["localization"] == "unresolved"


def test_localize_writes_tables_and_mge(reports, tmp_path):
    assembly, mob, ab = reports
    output = tmp_path / "local"
    contigs, features, summaries = localize(
        "sample", assembly, ab, mob, output, {"resfinder": "ARG"})
    assert len(read_tsv(output / "contig_summary.tsv")) == 3
    assert len(read_tsv(output / "feature_localization.tsv")) == 4
    assert any(f["feature_class"] == "MGE" for f in features)
    svg = architecture_svg("sample", contigs, features, output / "architecture.svg")
    text = svg.read_text()
    assert "<svg" in text and "CHROMOSOME" in text
    assert "tet(M)" in text


def test_abricate_unknown_contig_is_error(reports):
    assembly, mob, ab = reports
    with (ab / "resfinder" / "sample.tsv").open("a") as handle:
        handle.write("sample.fna\tinvalid\t1\t10\t+\tbadGene\t100\t100\n")
    ctg = classify_contigs("sample", assembly, mob / "contig_report.txt")
    with pytest.raises(ValueError, match="cannot localize"):
        read_abricate_features("sample", ctg, ab, {"resfinder": "ARG"})


def test_qc_exclusion_explicit_in_report(tmp_path):
    from chromoplas.qc import write_tsv
    root = tmp_path / "results"
    write_tsv(root / "02_quality/quality_summary.tsv", [
        {"sample": "low_quality", "status": "FAIL", "reasons": "genome_size_low",
         "genome_size": 12, "contigs": 3, "n50": 7, "gc": 42},
    ], ["sample", "status", "reasons", "genome_size", "contigs", "n50", "gc"])
    generate_report(root, ["low_quality"])
    page = (root / "07_reports/report.html").read_text()
    assert "Excluded from downstream screening" in page
    assert "Not a biological absence call" in page
    assert read_tsv(root / "07_reports/master_summary.tsv")[0]["qc_status"] == "FAIL"


def test_localization_output_serial_and_report_links(tmp_path):
    """Keep generated report links aligned with 06_localization / 07_reports."""
    from chromoplas.qc import write_tsv
    root = tmp_path / "results"
    write_tsv(root / "02_quality/quality_summary.tsv", [
        {"sample": "demo", "status": "PASS", "reasons": "",
         "genome_size": 2000, "contigs": 1, "n50": 2000, "gc": 40},
    ], ["sample", "status", "reasons", "genome_size", "contigs", "n50", "gc"])
    out = root / "06_localization" / "demo"
    out.mkdir(parents=True)
    (out / "architecture.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    generate_report(root, ["demo"])
    html = (root / "07_reports/report.html").read_text()
    assert "../06_localization/demo/architecture.svg" in html
    assert "../07_localization/" not in html
    from importlib.resources import files
    snakefile = files("chromoplas").joinpath("workflow/Snakefile").read_text()
    assert '06_localization/{sample}/.done' in snakefile
    assert "07_localization/" not in snakefile


def test_architecture_svg_explains_all_marker_and_track_colors(tmp_path):
    """Feature legend must include dark-grey replicons and distinguish tracks."""
    import xml.etree.ElementTree as ET
    from chromoplas.visualization import PALETTE

    contigs = {
        "chr": {"contig_id": "chr", "location": "chromosome", "length_bp": 1000, "plasmid_group": ""},
        "pl": {"contig_id": "pl", "location": "plasmid", "length_bp": 500, "plasmid_group": "AA452"},
        "und": {"contig_id": "und", "location": "unresolved", "length_bp": 200, "plasmid_group": ""},
    }
    features = [
        {"contig_id": "pl", "start": 100, "end": 130,
         "feature_class": "Replicon", "feature_name": "repA"},
    ]
    figure = architecture_svg("legend_demo", contigs, features, tmp_path / "architecture.svg")
    tree = ET.parse(figure)
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    labels = [elem.text for elem in root.findall(".//svg:text", ns) if elem.text]
    for required in (
        "Feature markers", "Resistance gene (ARG)", "Virulence factor (VF)",
        "Mobile element (MGE)", "Plasmid replicon", "Contig tracks",
        "Chromosome-associated", "Plasmid-associated", "Unresolved",
    ):
        assert required in labels
    rect_colors = {el.get("fill") for el in root.findall(".//svg:rect", ns)}
    for category in ("ARG", "VF", "MGE", "Replicon", "chromosome", "plasmid", "unresolved"):
        assert PALETTE[category] in rect_colors
    assert PALETTE["Replicon"] != PALETTE["unresolved"]
    assert "repA" in figure.read_text()


def test_architecture_svg_legend_clear_when_no_contigs(tmp_path):
    """Even an empty architecture retains its full descriptive legend."""
    import xml.etree.ElementTree as ET

    output = architecture_svg("empty_demo", {}, [], tmp_path / "empty.svg")
    ET.parse(output)
    text = output.read_text()
    assert "Plasmid replicon" in text
    assert "Unresolved" in text
