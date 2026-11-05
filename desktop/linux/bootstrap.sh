#!/usr/bin/env bash
# Only executed as root inside the application's dedicated, ownership-checked distro.
set -Eeuo pipefail
trap 'printf "\nSETUP FAILED at line %s. Reopen the app and retry setup; the log contains the failing command.\n" "$LINENO" >&2' ERR
[[ "$(cat /etc/chromoplas-desktop-owner)" == "chromoplas-desktop-v1" ]]
[[ "$(uname -m)" == "x86_64" ]]
source_archive="$(printf '%s' "$1" | base64 --decode)"
payload_sha="$2"
[[ "$payload_sha" =~ ^[a-f0-9]{64}$ ]]
printf '%s  %s\n' "$payload_sha" "$source_archive" | sha256sum --check --status
export DEBIAN_FRONTEND=noninteractive
export PYTHONUNBUFFERED=1
printf '\nInstalling Ubuntu prerequisites...\n'
apt-get -o Acquire::Retries=3 update
apt-get -o Acquire::Retries=3 install -y --no-install-recommends ca-certificates curl bzip2 \
    coreutils python3 passwd util-linux locales
if ! id -u chromoplas >/dev/null 2>&1; then
    useradd --create-home --shell /bin/bash chromoplas
fi
# Keep Windows PATH entries out of the analysis environment. Only our distro is affected.
cat > /etc/wsl.conf <<'CONF'
[automount]
enabled=true
root=/mnt/
[interop]
enabled=true
appendWindowsPath=false
[user]
default=chromoplas
CONF
install -d -m 755 /opt/chromoplas
rm -f /opt/chromoplas/ready.json
source_dir="/opt/chromoplas/build-$payload_sha"
mkdir -p "$source_dir"
tar -xzf "$source_archive" --no-same-owner -C "$source_dir"
chown -R chromoplas:chromoplas "$source_dir"
printf '\nInstalling ChromoPlas and its databases as the analysis user...\n'
# If a first Miniforge download was interrupted, keep it for diagnosis and retry cleanly.
if [[ -d /home/chromoplas/miniforge3 && ! -x /home/chromoplas/miniforge3/bin/conda ]]; then
    mv /home/chromoplas/miniforge3 "/home/chromoplas/miniforge3-incomplete-$(date +%s)"
fi
runuser -u chromoplas -- bash "$source_dir/INSTALL.sh"
ln -sfn "$source_dir" /opt/chromoplas/current
engine_python=/home/chromoplas/miniforge3/envs/chromoplas/bin/python
runuser -u chromoplas -- "$engine_python" "$source_dir/desktop/linux/worker.py" --check
# Save exact resolved tool packages. Databases are inventoried separately by the worker.
runuser -u chromoplas -- /home/chromoplas/miniforge3/bin/conda list -n chromoplas --explicit \
    > /opt/chromoplas/conda-explicit.txt
printf '{"schema":1,"payload_sha256":"%s"}\n' "$payload_sha" > /opt/chromoplas/ready.json.tmp
mv /opt/chromoplas/ready.json.tmp /opt/chromoplas/ready.json
printf '\nChromoPlas setup and database checks completed.\n'
