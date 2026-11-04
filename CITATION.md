# How to cite ChromoPlas and its dependencies

If ChromoPlas contributes to an analysis, please cite **the ChromoPlas software version/commit** and **the primary publications for external tools and reference databases actually used**. The GitHub repository has a machine-readable [CITATION.cff](CITATION.cff) file; use the **Cite this repository** button to export a software citation.

## ChromoPlas software citation

> Sarwer, A. (2026). *ChromoPlas: contig-resolved chromosome/plasmid localization of bacterial resistance, virulence and mobile-element determinants* (Version 0.3.0) [Computer software]. GitHub. https://github.com/afsansarwer/ChromoPlas

**There is currently no published ChromoPlas methods paper or DOI.** Do not invent or imply one. For reproducibility, specify the Git commit hash or an immutable tagged release used in a study. When a verified DOI is issued for a future archived release, the project can update the citation accordingly.

## Core analysis tools

1. **Snakemake** (workflow execution): Mölder, F., et al. (2021). Sustainable data analysis with Snakemake. *F1000Research, 10*, 33. [Original citation instructions](https://github.com/snakemake/snakemake/blob/main/docs/project_info/citations.rst).
2. **Prokka** (optional annotation): Seemann, T. (2014). Prokka: rapid prokaryotic genome annotation. *Bioinformatics, 30*(14), 2068–2069. https://doi.org/10.1093/bioinformatics/btu153
4. **ABRicate** (whole-genome screening): Seemann, T. *ABRicate* [Computer software]. https://github.com/tseemann/abricate. ABRicate's official instructions explicitly request citing **both ABRicate and each screened database**.
5. **MOB-suite** (plasmid reconstruction/typing):
   - Robertson, J. & Nash, J. H. E. (2018). MOB-suite: software tools for clustering, reconstruction and typing of plasmids from draft assemblies. *Microbial Genomics, 4*(8), e000206. https://doi.org/10.1099/mgen.0.000206
   - Robertson, J., Bessonov, K., Schonfeld, J., & Nash, J. H. E. (2020). Universal whole-sequence-based plasmid typing and its utility to prediction of host range and epidemiological surveillance. *Microbial Genomics, 6*(10), mgen000435. https://doi.org/10.1099/mgen.0.000435

## Default ABRicate reference databases

6. **ResFinder**: Bortolaia, V., et al. (2020). ResFinder 4.0 for predictions of phenotypes from genotypes. *Journal of Antimicrobial Chemotherapy, 75*(12), 3491–3500. https://doi.org/10.1093/jac/dkaa345
7. **VFDB**: Chen, L., et al. (2016). VFDB 2016: hierarchical and refined dataset for big data analysis—10 years on. *Nucleic Acids Research, 44*(D1), D694–D697. https://doi.org/10.1093/nar/gkv1239
8. **PlasmidFinder**: Carattoli, A., et al. (2014). In silico detection and typing of plasmids using PlasmidFinder and plasmid multilocus sequence typing. *Antimicrobial Agents and Chemotherapy, 58*(7), 3895–3903. https://doi.org/10.1128/AAC.02412-14

If users change the database list in YAML, they should cite those additional primary databases instead of citing databases that were not used. Check upstream citation guidance for updates and required references.

## Example Methods wording

> Assembled bacterial genomes were processed with ChromoPlas v0.3.0 (Git commit: **[replace with actual commit]**), a Snakemake-based workflow that estimates assembly quality metrics, selects assemblies meeting configurable thresholds, screens original assembled contigs with ABRicate, predicts contig locations using MOB-suite, and generates contig-resolved localization maps and consolidated reports. Optional Prokka annotation is disabled by default. Genomic matches were screened using the ResFinder, VFDB, and PlasmidFinder databases at thresholds documented in the study. Software versions and database release dates were recorded.

Edit this text to accurately reflect the settings and tools **actually used**, and cite the publications above. In particular, ChromoPlas's basic quality filter does **not** estimate contamination/completeness, and MOB-suite assignments do **not** experimentally verify plasmid location.

## Reproducibility checklist

Record the ChromoPlas tag/commit, operating system and architecture, tool versions, Conda environment export, databases and retrieval dates, screening identity/coverage thresholds, sample FASTA checksums, and complete configuration. Updating dependencies between analyses can make results non-comparable without reanalysis. See [update guidance](docs/updating.md) and [validation notes](docs/validation.md).
