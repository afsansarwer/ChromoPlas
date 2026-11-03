# ChromoPlas architecture and scientific interpretation

## Purpose

Process a bacterial assembly, preserve each original contig identifier, identify ARGs, virulence factors, replicon markers, and available mobile-element matches, and locate those signals on predicted chromosome/plasmid/unresolved contigs.

This package does NOT perform pangenome analysis, ANI, phylogeny or cross-isolate comparison.

## Computational stages

1. Validate FASTA file names and original contig identifiers; calculate FASTA genome size, contig count, N50, GC%.
2. Apply configurable FASTA-metric quality filtering. Failed assemblies remain in the report and do not enter expensive screening jobs.
3. Run ABRicate ON THE ORIGINAL ASSEMBLY, preserving contig-relative start/end coordinates.
4. Run MOB-suite mob_recon on the same FASTA, retaining contig_report.txt, plasmid bins, and any mge.report.txt.
5. Link ABRicate hits to MOB-suite assignments by ORIGINAL contig_id. A MOB-suite plasmid prediction requires a unique primary_cluster_id; chromosome requires an explicit chromosome call without a cluster. Missing, contradictory or unmatched assignments remain unresolved.
6. Map MOB-suite MGE hits using contig_start and contig_end. Its mge_start and mge_end describe MGE query positions, not genomic contig positions.
7. Summarize unique feature names as chromosome_only, plasmid_only, both, or unresolved. The both label requires evidence of at least one chromosomal and one plasmid-associated detection.
8. Plot every contig, scaled by length within the assembly, with features shown at genomic coordinates, and write HTML and TSV results.

## Main data contract

contig_summary.tsv: sample, contig_id, length_bp, location, plasmid_group, assignment_source, assignment_note, replicon_types, predicted_mobility.

feature_localization.tsv: sample, contig_id, contig_length_bp, location, plasmid_group, feature_class, feature_name, start, end, strand, database, identity, coverage, evidence, assignment_note.

gene_localization_summary.tsv: unique feature name, class, localization, chromosome_hits, plasmid_hits, unresolved_hits, plasmid_groups.

## Limits

Classification is predicted by MOB-suite and must not be treated as conclusive chromosome/plasmid localization. Complete plasmids are not guaranteed. MGE matches in MOB-suite 3.1+ are limited/repetitive-element evidence, not a comprehensive MGE screen. The FASTA quality metrics DO NOT measure contamination or completeness.

Planned but not implemented: optional CheckM2, geNomad consensus, detailed context annotation, cross-tool confidence categories, interactive high-density plotting. No draft assembly contig is forced to chromosome by default.

## Testing

Synthetic fixtures exercise both-location gene calls, unresolved assignments, MGE contig-coordinate mapping, QC failure recording and SVG generation. Real bacterial assemblies and multiple platforms require end-to-end validation before stable release.
