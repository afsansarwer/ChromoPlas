# ChromoPlas v0.3.0 — public beta release notes

**Release type:** prerelease / research prototype (not a clinically validated product).

ChromoPlas is an open-source Python/Snakemake workflow that turns assembled bacterial FASTA genomes into contig-resolved resistance-gene, virulence-factor, replicon and available MGE screening results. It integrates ABRicate and MOB-suite predictions with SVG visualizations, TSVs and an HTML report.

## Highlights

- Simple `chromoplas assembly.fna -o results -t 4` interface, plus batch-directory input.
- Original FASTA contig IDs retained for feature-coordinate localization.
- Predicted chromosome, plasmid and unresolved compartments; conflicting or missing assignments are not silently forced into a compartment.
- Contig architecture and gene-localization matrix SVGs generated from each sample's results.
- Clear `mge_evidence_status`; unavailable MGE evidence is marked `NA`, not a biological zero.
- QC screening, configurable thresholds, optional Prokka annotation and HTML/TSV reports.
- Run provenance including input SHA-256 checksums, software/database checks and resolved settings.
- Install documentation for Debian/Ubuntu, Omarchy/Arch, macOS and Windows through WSL2.

## Verification evidence

- Automated tests succeeded on Python 3.11 and 3.12, including a **synthetic orchestration test** with simulated ABRicate/MOB-suite executables.
- A full current-version single-genome execution using the real external tools completed on Omarchy Linux on **2026-11-05**, with 9/9 Snakemake steps completed, an assembly QC PASS and an HTML report displayed.
- This verifies successful execution for that configuration. It does **not** establish independently benchmarked chromosome/plasmid assignment accuracy or complete support on macOS, Debian, WSL2 and native Windows. Native Windows execution without WSL2 is not supported.

## Input, installation and first run

Requires assembled bacterial FASTA; FASTQ preprocessing and assembly are not included.

```bash
git clone https://github.com/afsansarwer/ChromoPlas.git
cd ChromoPlas
# Install Miniforge first if necessary (see INSTALL.md).
source "$HOME/miniforge3/etc/profile.d/conda.sh"
mamba create -y -n chromoplas -c conda-forge -c bioconda \
  python=3.11 'snakemake>=8,<10' abricate mob_suite typer pyyaml pip pytest
conda activate chromoplas
python -m pip install --no-deps -e .
chromoplas doctor
chromoplas /path/to/assembled-genome.fna -o results -t 4
```

On Omarchy Bash, run `set -h` before Conda shell initialization if `hash: hashing disabled` occurs.

## Scientific limitations

ABRicate hits are database- and threshold-dependent predictions, not phenotypic resistance measurements. MOB-suite predicted plasmid-associated contigs are not experimentally verified plasmids. Available coordinate-resolved MGE matches are not a comprehensive MGE annotation. Default QC is not an estimate of contamination or completeness. This software is not intended for clinical diagnostic decisions.

**Please test using publicly sharable bacterial assemblies**, check outputs against independent evidence, and report bugs with relevant version and database details (without disclosing sensitive data).

Documentation: [Installation](../INSTALL.md) · [Validation](validation.md) · [Citations](../CITATION.md) · [Release checklist](release-checklist.md).

**Citation:** use `CITATION.cff` and cite the original ABRicate/MOB-suite/database resources used. No project DOI or methods paper is claimed.
