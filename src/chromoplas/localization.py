"""MOB-suite and ABRicate interpretation with explicit unresolved assignments.

Original FASTA contig IDs are the coordinate system. No mappings may silently
fall back to 'chromosome' when MOB-suite has no assignment.
"""
from collections import defaultdict
from pathlib import Path
from .qc import read_tsv, contig_lengths, write_tsv

CONTIG_COLUMNS = ["sample", "contig_id", "length_bp", "location", "plasmid_group",
                  "assignment_source", "assignment_note", "replicon_types",
                  "predicted_mobility"]
FEATURE_COLUMNS = ["sample", "contig_id", "contig_length_bp", "location",
                   "plasmid_group", "feature_class", "feature_name",
                   "start", "end", "strand", "database", "identity",
                   "coverage", "evidence", "assignment_note"]
GENE_COLUMNS = ["sample", "feature_class", "feature_name", "localization",
                "chromosome_hits", "plasmid_hits", "unresolved_hits",
                "plasmid_groups"]


def _missing(value):
    return not str(value or "").strip() or str(value).strip().lower() in {"-", "na", "none", "unknown"}


def classify_contigs(sample, fasta, mob_report=None):
    """Classify each original contig; unknown/absent MOB entries stay unresolved."""
    lengths = contig_lengths(fasta)
    result = {}
    mob_rows = read_tsv(mob_report) if mob_report else []
    by_id = defaultdict(list)
    for row in mob_rows:
        identifier = str(row.get("contig_id", "")).strip()
        if identifier in lengths:
            by_id[identifier].append(row)
    for contig_id, length in lengths.items():
        matches = by_id[contig_id]
        location = "unresolved"
        group = ""
        note = "No matching MOB-suite contig assignment"
        rep = ""
        mobility = ""
        if matches:
            types = {row.get("molecule_type", "").lower().strip() for row in matches}
            groups = {row.get("primary_cluster_id", "").strip()
                      for row in matches if not _missing(row.get("primary_cluster_id"))}
            if len(types) == 1 and types == {"plasmid"} and len(groups) == 1:
                location = "plasmid"
                group = next(iter(groups))
                note = "MOB-suite plasmid prediction (not experimentally confirmed)"
            elif len(types) == 1 and types == {"chromosome"} and not groups:
                location = "chromosome"
                note = "MOB-suite chromosome prediction (not experimentally confirmed)"
            else:
                note = "Ambiguous/incomplete or inconsistent MOB-suite assignment"
            rep = ";".join(sorted({row.get("rep_type(s)", "") for row in matches
                                    if not _missing(row.get("rep_type(s)"))}))
            mobility = ";".join(sorted({row.get("predicted_mobility", "") for row in matches
                                         if not _missing(row.get("predicted_mobility"))}))
        result[contig_id] = {
            "sample": sample, "contig_id": contig_id, "length_bp": length,
            "location": location, "plasmid_group": group,
            "assignment_source": "MOB-suite" if matches else "none",
            "assignment_note": note, "replicon_types": rep,
            "predicted_mobility": mobility,
        }
    return result


def _number(value, default=None):
    try:
        return float(str(value).replace("%", "").strip())
    except (TypeError, ValueError):
        return default


def _coordinates(row):
    try:
        a = int(row.get("START", row.get("start", "")))
        b = int(row.get("END", row.get("end", "")))
        return min(a, b), max(a, b)
    except (TypeError, ValueError):
        return None


def read_abricate_features(sample, contigs, report_dir, db_classes):
    """Parse matches on the ORIGINAL assembled FASTA, preserving coordinates."""
    features = []
    for db, feature_class in db_classes.items():
        for row in read_tsv(Path(report_dir) / db / f"{sample}.tsv"):
            identifier = (row.get("SEQUENCE") or row.get("sequence") or "").strip()
            if identifier not in contigs:
                raise ValueError(
                    f"ABRicate contig {identifier!r} not in FASTA for {sample}; cannot localize reliably."
                )
            coords = _coordinates(row)
            if not coords:
                raise ValueError(f"Missing coordinates in ABRicate results: {sample}/{db}")
            start, end = coords
            info = contigs[identifier]
            if not (1 <= start <= end <= info["length_bp"]):
                raise ValueError(f"Out-of-bounds ABRicate coordinates: {sample}/{identifier}: {start}-{end}")
            features.append({
                "sample": sample, "contig_id": identifier,
                "contig_length_bp": info["length_bp"],
                "location": info["location"], "plasmid_group": info["plasmid_group"],
                "feature_class": feature_class,
                "feature_name": row.get("GENE", row.get("gene", "")),
                "start": start, "end": end,
                "strand": row.get("STRAND", row.get("strand", "")),
                "database": db,
                "identity": row.get("%IDENTITY", row.get("IDENTITY", "")),
                "coverage": row.get("%COVERAGE", row.get("COVERAGE", "")),
                "evidence": "ABRicate hit",
                "assignment_note": info["assignment_note"],
            })
    return features


def read_mob_mges(sample, contigs, mob_dir):
    """Use only coordinate-resolved MOB-suite MGE hits.

    MOB-suite columns vary across versions; MGE rows without documented,
    unambiguous contig IDs and coordinates are preserved in MOB's raw report
    but excluded from a coordinate map.
    """
    result = []
    path = Path(mob_dir) / "mge.report.txt"
    for row in read_tsv(path):
        identifier = (row.get("contig_id") or "").strip()
        if identifier not in contigs:
            continue
        try:
            start = int(row.get("contig_start", ""))
            end = int(row.get("contig_end", ""))
        except ValueError:
            continue
        start, end = min(start, end), max(start, end)
        info = contigs[identifier]
        if not (1 <= start <= end <= info["length_bp"]):
            continue
        result.append({
            "sample": sample, "contig_id": identifier,
            "contig_length_bp": info["length_bp"],
            "location": info["location"], "plasmid_group": info["plasmid_group"],
            "feature_class": "MGE",
            "feature_name": row.get("mge_id") or row.get("mge_type") or "MGE",
            "start": start, "end": end, "strand": row.get("sstrand", ""),
            "database": "mob-suite", "identity": "", "coverage": "",
            "evidence": "MOB-suite MGE hit", "assignment_note": info["assignment_note"],
        })
    return result


def summarize(sample, features):
    """One row per unique feature name; 'both' only if BOTH locations evidenced."""
    by_gene = defaultdict(list)
    for feature in features:
        name = feature["feature_name"]
        if name:
            by_gene[(feature["feature_class"], name)].append(feature)
    summary = []
    for (kind, name), matches in sorted(by_gene.items()):
        chrom = sum(f["location"] == "chromosome" for f in matches)
        plas = sum(f["location"] == "plasmid" for f in matches)
        unknown = sum(f["location"] == "unresolved" for f in matches)
        location = ("both" if chrom and plas else
                    "chromosome_only" if chrom and not plas else
                    "plasmid_only" if plas and not chrom else "unresolved")
        summary.append({
            "sample": sample, "feature_class": kind, "feature_name": name,
            "localization": location, "chromosome_hits": chrom,
            "plasmid_hits": plas, "unresolved_hits": unknown,
            "plasmid_groups": ";".join(sorted({f["plasmid_group"] for f in matches
                                             if f["location"] == "plasmid" and f["plasmid_group"]})),
        })
    return summary


def localize(sample, fasta, abricate_dir, mob_dir, output_dir, db_classes, plasmids_enabled=True):
    contigs = classify_contigs(sample, fasta, Path(mob_dir) / "contig_report.txt" if plasmids_enabled else None)
    features = read_abricate_features(sample, contigs, abricate_dir, db_classes)
    if plasmids_enabled:
        features += read_mob_mges(sample, contigs, mob_dir)
    gene_summary = summarize(sample, features)
    out = Path(output_dir)
    write_tsv(out / "contig_summary.tsv", list(contigs.values()), CONTIG_COLUMNS)
    write_tsv(out / "feature_localization.tsv", features, FEATURE_COLUMNS)
    write_tsv(out / "gene_localization_summary.tsv", gene_summary, GENE_COLUMNS)
    return contigs, features, gene_summary
