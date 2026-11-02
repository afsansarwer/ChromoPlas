import csv
import html
from pathlib import Path
from .qc import write_tsv


def read_tsv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def build_report(out, samples, databases):
    out = Path(out)
    qc = {r["sample"]: r for r in read_tsv(out / "02_quality" / "quality_summary.tsv")}
    rows = []
    hits = []
    for sample in samples:
        rec = dict(qc[sample])
        rec["sample"] = sample
        for compartment, sub in [("genome", "04_abricate"), ("plasmid", "06_plasmid_abricate")]:
            for db in databases:
                found = read_tsv(out / sub / db / f"{sample}.tsv")
                genes = sorted({r.get("GENE", "") for r in found if r.get("GENE")})
                rec[f"{compartment}_{db}_genes"] = ";".join(genes)
                for hit in found:
                    hits.append(dict(sample=sample, compartment=compartment, database=db, **hit))
        rows.append(rec)
    columns = list(rows[0]) if rows else ["sample"]
    reportdir = out / "07_reports"
    write_tsv(reportdir / "master_summary.tsv", rows, columns)
    write_tsv(reportdir / "all_abricate_hits.tsv", hits, list(dict.fromkeys(k for r in hits for k in r)) or ["sample", "compartment", "database"])
    head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(r.get(c, '')))}</td>" for c in columns) + "</tr>" for r in rows)
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>GenomeFlow report</title>
<style>body{{font:14px system-ui;margin:2rem;color:#1b2936}} table{{border-collapse:collapse;display:block;overflow-x:auto}} th,td{{border:1px solid #ddd;padding:7px}} th{{background:#e8eff6}} tr:nth-child(even){{background:#f7f9fb}}</style></head>
<body><h1>GenomeFlow v0.2</h1><p>Samples: {len(rows)}; HQ: {sum(r.get('status') == 'PASS' for r in rows)}</p>
<p>Predicted plasmid-associated sequences are not experimentally confirmed plasmids.</p><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></body></html>"""
    (reportdir / "report.html").write_text(page)
