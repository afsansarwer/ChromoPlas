# ChromoPlas command guide

ChromoPlas analyzes one assembled bacterial FASTA or several assembled genomes independently.

~~~bash
chromoplas genome.fna -o results/ -t 4
chromoplas genomes/ -o batch_results/ -t 8
chromoplas genome.fna -o results/ --dry-run
chromoplas genome.fna -o results/ --config custom.yaml
chromoplas doctor
chromoplas --help
~~~

## Advanced mode

~~~bash
chromoplas init project
cp genome.fna project/genomes/
cd project
chromoplas qc --config config.yaml
chromoplas run --config config.yaml --cores 4
~~~

## Output files

- 02_quality/quality_summary.tsv: genome QC with PASS/FAIL reasons
- 04_abricate/: ResFinder ARGs, VFDB virulence hits, PlasmidFinder replicon hits
- 05_plasmids/: MOB-suite contig report, reconstructed plasmid predictions, MGE report
- 07_localization/SAMPLE/contig_summary.tsv: original contig IDs and predicted compartments
- 07_localization/SAMPLE/feature_localization.tsv: feature coordinates on original FASTA contigs
- 07_localization/SAMPLE/gene_localization_summary.tsv: chromosome, plasmid, both and unresolved categories
- 07_localization/SAMPLE/architecture.svg: contig-level gene map
- 07_reports/report.html: isolate QC and visualization index

The default workflow omits Prokka annotation to reduce runtime. Enable Prokka with annotation.enabled: true in a YAML config and install Prokka separately. For available options and configuration, see the linked guides.

A QC failure is excluded from screening but remains visible in the final report. Ambiguous contigs are retained as unresolved so the results remain interpretable.

Install: [Installation overview](INSTALL.md) · [Omarchy/Arch Bash fix](docs/install-omarchy.md) · [Debian/Ubuntu](docs/install-debian.md) · [macOS](docs/install-macos.md) · [Windows/WSL2](docs/install-windows-powershell.md).

Maintenance: [Update tools/databases](docs/updating.md) · [Troubleshooting](docs/troubleshooting.md) · [Workflow architecture](docs/architecture.md).
