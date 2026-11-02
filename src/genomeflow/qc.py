import csv
import gzip
import math
from pathlib import Path


def fasta_records(path):
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as stream:
        seq = []
        for line in stream:
            if line.startswith(">"):
                if seq:
                    yield "".join(seq).upper()
                    seq = []
            elif line.strip():
                seq.append(line.strip())
        if seq:
            yield "".join(seq).upper()


def metrics(path):
    lengths = []
    gc = 0
    atgc = 0
    for seq in fasta_records(path):
        lengths.append(len(seq))
        gc += seq.count("G") + seq.count("C")
        atgc += sum(seq.count(base) for base in "ATGC")
    if not lengths:
        raise ValueError(f"No FASTA sequence found in {path}")
    total = sum(lengths)
    running = 0
    n50 = 0
    for length in sorted(lengths, reverse=True):
        running += length
        if running >= total / 2:
            n50 = length
            break
    return dict(genome_size=total, contigs=len(lengths), n50=n50,
                gc=round(100*gc/atgc, 3) if atgc else 0)


def assess(m, q):
    checks = [("genome_size_low", m["genome_size"] >= q["min_genome_size"]),
              ("genome_size_high", m["genome_size"] <= q["max_genome_size"]),
              ("contigs_high", m["contigs"] <= q["max_contigs"]),
              ("n50_low", m["n50"] >= q["min_n50"]),
              ("gc_low", m["gc"] >= q["min_gc"]),
              ("gc_high", m["gc"] <= q["max_gc"])]
    reasons = [name for name, ok in checks if not ok]
    return "PASS" if not reasons else "FAIL", ";".join(reasons)


def write_tsv(path, rows, columns):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
