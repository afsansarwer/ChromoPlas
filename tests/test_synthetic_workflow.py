"""Synthetic, fully orchestrated Snakemake smoke test using stub external programs.

This checks the integration between stages without claiming validation of
ABRicate/MOB-suite algorithms or their reference databases.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from chromoplas.qc import read_tsv


def _binary(path, body):
    path.write_text("#!" + sys.executable + "\n" + body)
    path.chmod(0o755)


@pytest.mark.skipif(shutil.which("snakemake") is None, reason="Snakemake not available")
def test_full_synthetic_workflow_from_fasta_to_report(tmp_path):
    bin_dir = tmp_path / "fake-tools"
    bin_dir.mkdir()
    _binary(bin_dir / "abricate", """import sys
from pathlib import Path
db = sys.argv[sys.argv.index('--db')+1]
fasta = Path(sys.argv[-1])
id = fasta.read_text().split('\\n')[0].lstrip('>').split()[0]
print('#FILE\\tSEQUENCE\\tSTART\\tEND\\tSTRAND\\tGENE\\t%IDENTITY\\t%COVERAGE')
gene = {'resfinder':'tet(M)', 'vfdb':'fimH', 'plasmidfinder':'repA'}[db]
print(f'{fasta}\\t{id}\\t10\\t45\\t+\\t{gene}\\t99\\t97')
""")
    _binary(bin_dir / "mob_recon", """import sys
from pathlib import Path
args = sys.argv
fasta = Path(args[args.index('--infile')+1])
output = Path(args[args.index('--outdir')+1])
output.mkdir(parents=True, exist_ok=True)
id = fasta.read_text().split('\\n')[0].lstrip('>').split()[0]
(output/'contig_report.txt').write_text(
    'sample_id\\tcontig_id\\tmolecule_type\\tprimary_cluster_id\\trep_type(s)\\tpredicted_mobility\\n'
    +f'fixture\\t{id}\\tplasmid\\tAD582\\tIncF\\tmobilizable\\n')
(output/'mge.report.txt').write_text(
    'contig_id\\tcontig_start\\tcontig_end\\tmge_id\\tmge_type\\n'
    +f'{id}\\t20\\t35\\tIS26\\tIS\\n')
""")
    fasta = tmp_path / "fixture.fna"
    fasta.write_text(">contig1\n" + "ACGT" * 150 + "\n")
    output = tmp_path / "out"
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ.get("PATH",""))
    p = subprocess.run(
        [sys.executable, "-m", "chromoplas.cli", str(fasta), "-o", str(output), "-t", "2"],
        env=env, cwd=tmp_path, capture_output=True, text=True,
    )
    assert p.returncode == 0, p.stdout + "\n" + p.stderr
    assert (output/"07_reports/report.html").exists()
    assert (output/"06_localization/fixture/architecture.svg").exists()
    assert (output/"06_localization/fixture/gene_localization_matrix.svg").exists()
    assert (output/"00_metadata/provenance.json").exists()
    summary = read_tsv(output/"07_reports/master_summary.tsv")
    assert summary[0]["mge_evidence_status"] == "coordinate_report_available"
    assert summary[0]["mge_hits"] == "1"
    genes = read_tsv(output/"06_localization/fixture/gene_localization_summary.tsv")
    assert any(x["feature_name"] == "tet(M)" and x["localization"] == "plasmid_only" for x in genes)
