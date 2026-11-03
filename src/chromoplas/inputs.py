"""Safely stage one or more assembled genomes by their existing FASTA filenames."""
import re
from pathlib import Path

SUFFIXES = (".fasta.gz", ".fna.gz", ".fa.gz", ".fasta", ".fna", ".fa")


def is_fasta(path):
    return str(path).lower().endswith(SUFFIXES)


def discover(inputs):
    files = []
    for entry in inputs:
        path = Path(entry).expanduser().resolve()
        if path.is_file() and is_fasta(path):
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(p.resolve() for p in path.iterdir() if p.is_file() and is_fasta(p)))
        else:
            raise ValueError(f"Invalid or missing input FASTA: {entry}")
    unique = list(dict.fromkeys(files))
    if not unique:
        raise ValueError("No FASTA assemblies found")
    samples = {}
    names = set()
    for path in unique:
        if path.name.casefold() in names:
            raise ValueError(f"Duplicate input filename: {path.name}")
        names.add(path.name.casefold())
        stem = path.name
        for suffix in SUFFIXES:
            if stem.lower().endswith(suffix):
                stem = stem[:-len(suffix)]
                break
        sample = re.sub(r"[^A-Za-z0-9_-]", "_", stem)
        if not sample or sample in samples:
            raise ValueError(f"Invalid or duplicated sample name after normalization: {sample}")
        samples[sample] = str(path)
    return samples
