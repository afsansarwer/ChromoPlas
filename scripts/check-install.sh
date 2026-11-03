#!/usr/bin/env bash
# ChromoPlas read-only install verification. Run after activating chromoplas.
set -u
fail=0
echo "ChromoPlas installation check"
echo "Conda environment: ${CONDA_DEFAULT_ENV:-not-activated}"
for program in python chromoplas snakemake abricate mob_recon; do
  if command -v "$program" >/dev/null 2>&1; then
    printf 'OK   %s: %s\n' "$program" "$(command -v "$program")"
  else
    printf 'FAIL %s missing\n' "$program" >&2
    fail=1
  fi
done
if command -v chromoplas >/dev/null 2>&1; then
  chromoplas --help >/dev/null || { echo "FAIL ChromoPlas CLI" >&2; fail=1; }
fi
if command -v abricate >/dev/null 2>&1; then
  if dbs="$(abricate --list 2>&1)"; then
    for db in resfinder vfdb plasmidfinder; do
      if printf '%s\n' "$dbs" | awk -v db="$db" 'tolower($1)==db {seen=1} END{exit !seen}'; then
        echo "OK   ABRicate database: $db"
      else
        echo "FAIL ABRicate database missing: $db" >&2
        fail=1
      fi
    done
  else
    printf 'FAIL ABRicate database listing: %s\n' "$dbs" >&2
    fail=1
  fi
fi
if command -v mob_recon >/dev/null 2>&1; then
  mob_recon --help >/dev/null 2>&1 || { echo "FAIL mob_recon help" >&2; fail=1; }
fi
if [[ "$fail" -ne 0 ]]; then
  echo "See docs/troubleshooting.md" >&2
else
  echo "Setup checks passed. Run a real genome to verify database usability end-to-end."
fi
exit "$fail"
