"""FASTA assembly metrics and a transparent, configurable QC gate."""
import csv
import gzip
from pathlib import Path


def fasta_records(path):
    """Yield (first-word contig ID, sequence), retaining original contig names."""
    opener = gzip.open if str(path).lower().endswith(".gz") else open
    seen = set()
    identifier = None
    seq = []
    with opener(path, "rt") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if identifier is not None:
                    if not seq:
                        raise ValueError(f"Empty sequence for {identifier} in {path}")
                    yield identifier, "".join(seq).upper()
                identifier = line[1:].split(maxsplit=1)[0] if line[1:].strip() else ""
                if not identifier or identifier in seen:
                    raise ValueError(f"Empty or duplicated FASTA contig ID: {identifier}")
                seen.add(identifier)
                seq = []
            else:
                if identifier is None:
                    raise ValueError(f"Sequence before FASTA header: {path}")
                seq.append(line)
        if identifier is not None:
            if not seq:
                raise ValueError(f"Empty sequence for {identifier} in {path}")
            yield identifier, "".join(seq).upper()


def contig_lengths(path):
    return {contig_id: len(seq) for contig_id, seq in fasta_records(path)}


def metrics(path):
    sizes = []
    gc = atgc = 0
    for _, seq in fasta_records(path):
        sizes.append(len(seq))
        gc += seq.count("G") + seq.count("C")
        atgc += sum(seq.count(x) for x in "ATGC")
    if not sizes:
        raise ValueError(f"No FASTA records found: {path}")
    total = sum(sizes)
    cumulative = 0
    n50 = 0
    for length in sorted(sizes, reverse=True):
        cumulative += length
        if cumulative >= total / 2:
            n50 = length
            break
    return {"genome_size": total, "contigs": len(sizes), "n50": n50,
            "gc": round(100 * gc / atgc, 3) if atgc else 0}


def assess(m, q):
    checks = [
        ("genome_size_low", m["genome_size"] >= q["min_genome_size"]),
        ("genome_size_high", m["genome_size"] <= q["max_genome_size"]),
        ("contigs_high", m["contigs"] <= q["max_contigs"]),
        ("n50_low", m["n50"] >= q["min_n50"]),
        ("gc_low", m["gc"] >= q["min_gc"]),
        ("gc_high", m["gc"] <= q["max_gc"]),
    ]
    reasons = [key for key, ok in checks if not ok]
    return ("FAIL" if reasons else "PASS", ";".join(reasons))


def write_tsv(path, rows, columns):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_tsv(path):
    path = Path(path)
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))
