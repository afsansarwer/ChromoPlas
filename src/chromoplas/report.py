"""Combine ChromoPlas per-isolate QC and localization into one HTML index."""
import csv
from html import escape
from pathlib import Path
from .qc import read_tsv, write_tsv


def _mge_evidence_status(results_dir, sample, plasmids_enabled, mapped_hits):
    """Do not interpret absent or incompatible MGE evidence as zero hits."""
    if not plasmids_enabled:
        return "not_run"
    path = results_dir / "05_plasmids" / sample / "mge.report.txt"
    if not path.is_file() or path.stat().st_size == 0:
        return "not_reported"
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        columns = set(reader.fieldnames or ())
        reported_rows = list(reader)
    if not {"contig_id", "contig_start", "contig_end"}.issubset(columns):
        return "coordinates_unavailable"
    if reported_rows and mapped_hits == 0:
        return "coordinate_rows_unmapped"
    if len(reported_rows) > mapped_hits:
        return "coordinate_rows_partly_mapped"
    return "coordinate_report_available"


def generate_report(results_dir, samples, plasmids_enabled=True):
    results_dir = Path(results_dir)
    qc = {row["sample"]: row for row in read_tsv(results_dir / "02_quality/quality_summary.tsv")}
    rows = []
    cards = []
    for sample in samples:
        quality = qc.get(sample, {})
        passed = quality.get("status") == "PASS"
        local = results_dir / "06_localization" / sample
        feature_rows = read_tsv(local / "feature_localization.tsv") if passed else []
        contig_rows = read_tsv(local / "contig_summary.tsv") if passed else []
        genes = read_tsv(local / "gene_localization_summary.tsv") if passed else []
        mge_count = sum(x["feature_class"] == "MGE" for x in feature_rows)
        mge_status = _mge_evidence_status(results_dir, sample, plasmids_enabled, mge_count) if passed else "qc_excluded"
        rec = {
            "sample": sample, "qc_status": quality.get("status", "UNKNOWN"),
            "qc_reasons": quality.get("reasons", ""),
            "genome_size": quality.get("genome_size", ""),
            "contigs": quality.get("contigs", ""),
            "n50": quality.get("n50", ""),
            "gc": quality.get("gc", ""),
            "chromosomal_contigs": sum(x["location"] == "chromosome" for x in contig_rows) if passed else "NA",
            "plasmid_contigs": sum(x["location"] == "plasmid" for x in contig_rows) if passed else "NA",
            "unresolved_contigs": sum(x["location"] == "unresolved" for x in contig_rows) if passed else "NA",
            "arg_hits": sum(x["feature_class"] == "ARG" for x in feature_rows) if passed else "NA",
            "vf_hits": sum(x["feature_class"] == "VF" for x in feature_rows) if passed else "NA",
            "mge_hits": mge_count if mge_status in {"coordinate_report_available", "coordinate_rows_partly_mapped"} else "NA",
            "mge_evidence_status": mge_status,
            "genes_in_both": sum(x["localization"] in {"both", "both_and_unresolved"} for x in genes) if passed else "NA",
        }
        rows.append(rec)
        name = escape(sample)
        if passed:
            svg_path = local / "architecture.svg"
            if svg_path.is_file():
                img = f'<img loading="lazy" src="../06_localization/{name}/architecture.svg" alt="Contig and feature localization of {name}">'
            else:
                img = "<p>Localization map unavailable.</p>"
            matrix_path = local / "gene_localization_matrix.svg"
            matrix = (
                f'<img loading="lazy" src="../06_localization/{name}/gene_localization_matrix.svg" '
                f'alt="Gene localization evidence matrix for {name}">'
                if matrix_path.is_file() else "<p>Gene localization matrix unavailable.</p>"
            )
            cards.append(
                f'<section><h2>{name} <small>QC PASS</small></h2>'
                f'<p>ARG hits: {rec["arg_hits"]}; VF hits: {rec["vf_hits"]}; MGE hits: {rec["mge_hits"]}. '
                f'MGE evidence status: {escape(rec["mge_evidence_status"])}. '
                f'Chromosome / plasmid / unresolved contigs: '
                f'{rec["chromosomal_contigs"]} / {rec["plasmid_contigs"]} / {rec["unresolved_contigs"]}.</p>'
                f'{img}{matrix}<p><a href="../06_localization/{name}/feature_localization.tsv">Feature table</a> · '
                f'<a href="../06_localization/{name}/contig_summary.tsv">Contig assignments</a> · '
                f'<a href="../06_localization/{name}/gene_localization_summary.tsv">Gene localization</a></p></section>'
            )
        else:
            cards.append(f'<section><h2>{name} <small>QC {escape(rec["qc_status"])}</small></h2>'
                         f'<p>Excluded from downstream screening: {escape(rec["qc_reasons"] or "quality gate")}. '
                         f'Not a biological absence call.</p></section>')
    out = results_dir / "07_reports"
    write_tsv(out / "master_summary.tsv", rows, list(rows[0]) if rows else ["sample"])
    no_pass_banner = ""
    if rows and not any(row["qc_status"] == "PASS" for row in rows):
        no_pass_banner = (
            '<section role="alert" class="warning"><h2>No genomes passed assembly QC</h2>'
            '<p>All input assemblies were excluded from ARG/VF screening, plasmid prediction '
            'and figure generation. No gene absences can be concluded from this report. '
            'Review <code>02_quality/quality_summary.tsv</code> and adjust QC thresholds '
            'only if scientifically appropriate for the input assembly.</p></section>'
        )
    qc_table = "".join(
        f'<tr><td>{escape(str(rec["sample"]))}</td><td>{escape(str(rec["qc_status"]))}</td>'
        f'<td>{escape(str(rec["qc_reasons"]))}</td>'
        f'<td>{rec["arg_hits"]}</td><td>{rec["vf_hits"]}</td><td>{rec["mge_hits"]}</td>'
        f'<td>{rec["plasmid_contigs"]}</td><td>{rec["unresolved_contigs"]}</td></tr>'
        for rec in rows)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ChromoPlas report</title><style>
body{{font:15px system-ui,sans-serif;max-width:1300px;margin:2rem auto;padding:0 1rem;color:#273444}}
h1{{color:#253e60}}section{{border:1px solid #d6dce2;border-radius:12px;padding:18px;margin:20px 0}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ced8e4;padding:8px;text-align:left}}
th{{background:#eef2f8}}img{{max-width:100%;height:auto;border:1px solid #e2e7ec}}
small{{color:#657487}}.note{{background:#f7f7f7;padding:14px;border-left:4px solid #d69c48}}
.warning{{background:#fff8ec;border:2px solid #d69c48}}
</style></head><body><h1>ChromoPlas — bacterial gene localization</h1>
<p class="note">Predicted chromosome/plasmid assignment is not experimental confirmation. Hits are dependent on databases and thresholds. Basic FASTA QC does not establish completeness or contamination. QC failures are not gene absences.</p>
{no_pass_banner}
<table><thead><tr><th>Isolate</th><th>QC</th><th>QC reasons</th><th>ARG hits</th><th>VF hits</th><th>MGE hits (NA = no usable coordinate evidence)</th><th>Plasmid contigs</th><th>Unresolved contigs</th></tr></thead>
<tbody>{qc_table}</tbody></table>
{''.join(cards)}</body></html>"""
    (out / "report.html").write_text(page, encoding="utf-8")
