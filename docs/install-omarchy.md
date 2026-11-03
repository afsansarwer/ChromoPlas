# Omarchy (Arch Linux): fix Conda/Mamba activation

On Omarchy, Bash may report **bash: hash: hashing disabled** when you run **conda activate chromoplas**. The environment exists; Bash command hashing is disabled by Omarchy's mise shell setup (set +h), while Conda calls hash -r during activation.

## One-time permanent fix (Bash)

1. **Confirm that your current shell is Bash:**

   ~~~bash
   ps -p $$ -o comm=
   ~~~

   If it says bash, follow these steps. Do not use a Zsh hook inside Bash.

2. **Back up and edit your personal Bash configuration:**

   ~~~bash
   cp -p ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d-%H%M%S)
   nano ~/.bashrc
   ~~~

3. Find the line that sources Omarchy's defaults, commonly:

   ~~~bash
   source ~/.local/share/omarchy/default/bash/rc
   ~~~

   Immediately **after** Omarchy initialization, and **before** any Conda/Mamba/NVM initialization, add:

   ~~~bash
   # Conda requires Bash command hashing (Omarchy disables it for mise).
   set -h

   # Initialize Miniforge in this Bash session.
   if [ -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
       source "$HOME/miniforge3/etc/profile.d/conda.sh"
   fi
   ~~~

   **Already have a Conda initialization block?** Add only set -h **before** that existing block; do not duplicate Conda setup. If Omarchy's defaults are sourced from another location, place set -h after the setting that disables hashing.

4. Save, open a new terminal (or run **exec bash**), and verify:

   ~~~bash
   set -o | grep '^hashall'      # expected: hashall on
   type conda                   # expected: conda is a shell function
   conda activate chromoplas
   echo "$CONDA_DEFAULT_ENV"     # expected: chromoplas
   command -v chromoplas
   chromoplas --help
   ~~~

## Quick fix for the current terminal

~~~bash
set -h
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate chromoplas
~~~

## If the environment activates but chromoplas is not found

Your Conda environment and Python package are separate installations. From the **repository root**, with ChromoPlas activated:

~~~bash
python -m pip install --no-deps -e .
chromoplas --help
chromoplas doctor
~~~

Run git pull --ff-only in the repository first if the local source is outdated.

## Activation-free fallback

~~~bash
"$HOME/miniforge3/bin/conda" run -n chromoplas chromoplas --help
~~~

This helps diagnose shell issues without modifying your Bash startup files.

## Still seeing the error?

Look for a later set +h, or Conda/NVM initialized before set -h:

~~~bash
grep -nE 'set \+h|set -h|omarchy|conda|mamba|nvm' ~/.bashrc
~~~

Reorder your **personal** .bashrc rather than editing Omarchy-managed startup scripts. Enabling hashing overrides Omarchy's default; if you use mise to switch tool versions and a command resolves to a stale executable, use hash -r or open a fresh terminal.

**References:** [Omarchy issue #2178](https://github.com/omacom/omarchy/issues/2178) · [Omarchy dotfiles](https://omarchy.org/manual/dotfiles/) · [Conda issue #7995](https://github.com/conda/conda/issues/7995).

[Install ChromoPlas](../INSTALL.md) · [Troubleshooting](troubleshooting.md)
