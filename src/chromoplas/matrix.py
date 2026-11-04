"""Render an SVG matrix summarizing gene evidence by predicted compartment."""
from collections import Counter
from html import escape
from pathlib import Path


def gene_localization_matrix(sample, rows, destination, max_rows=36):
    """Use only observed hit counts; do not imply verified plasmid/chromosome identity."""
    rows = sorted(rows, key=lambda r: (
        {"ARG": 0, "VF": 1, "Replicon": 2, "MGE": 3}.get(r.get("feature_class"), 4),
        r.get("feature_name", "")
    ))
    visible = rows[:max_rows]
    total = len(rows)
    height = 172 + len(visible) * 29 + 35
    width = 900
    esc = lambda value: escape(str(value), quote=True)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Gene localization evidence matrix">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text x="22" y="32" font-family="Arial" font-size="21" font-weight="bold" fill="#243447">ChromoPlas | {esc(sample)}</text>',
        '<text x="22" y="55" font-family="Arial" font-size="12" fill="#596b79">Detected features on predicted compartments (not experimentally confirmed)</text>',
        '<text x="535" y="92" text-anchor="middle" font-family="Arial" font-size="12" fill="#243447">Chromosome</text>',
        '<text x="660" y="92" text-anchor="middle" font-family="Arial" font-size="12" fill="#243447">Plasmid</text>',
        '<text x="794" y="92" text-anchor="middle" font-family="Arial" font-size="12" fill="#243447">Unresolved</text>',
    ]
    colors = {"ARG": "#bd5261", "VF": "#329682", "Replicon": "#64758a", "MGE": "#9369b0"}
    for i, row in enumerate(visible):
        y = 112 + i * 29
        cls = row.get("feature_class", "Other")
        name = row.get("feature_name", "")
        color = colors.get(cls, "#718096")
        if i % 2 == 0:
            parts.append(f'<rect x="18" y="{y-14}" width="861" height="27" fill="#f3f6f9"/>')
        parts.append(f'<rect x="26" y="{y-8}" width="10" height="10" fill="{color}"/>')
        parts.append(f'<text x="44" y="{y+3}" font-family="Arial" font-size="12" fill="#243447">{esc((str(name)[:57] + "…") if len(str(name))>57 else name)}</text>')
        for x, key in ((535, "chromosome_hits"), (660, "plasmid_hits"), (794, "unresolved_hits")):
            try:
                count = int(row.get(key, 0))
            except (TypeError, ValueError):
                count = 0
            if count:
                parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{color}"><title>{esc(key)}: {count}</title></circle>')
            else:
                parts.append(f'<circle cx="{x}" cy="{y}" r="6" fill="none" stroke="#d0d8e0"/>')
    foot = 141 + len(visible) * 29
    parts.append(f'<text x="22" y="{foot}" font-family="Arial" font-size="12" fill="#596b79">Filled = detected; empty = no matching hit. Showing {len(visible)} / {total} features.</text>')
    parts.append(f'<text x="22" y="{foot+19}" font-family="Arial" font-size="12" fill="#596b79">Unresolved evidence is displayed separately, including when a gene also has other hits.</text>')
    parts.append("</svg>")
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(parts), encoding="utf-8")
    return destination
