"""Render a self-contained, coordinate-scaled assembly diagram as SVG."""
from collections import defaultdict
from html import escape
from pathlib import Path

PALETTE = {
    "chromosome": "#527eae", "plasmid": "#db9e48", "unresolved": "#a2a9b1",
    "ARG": "#c44b54", "VF": "#33a187", "MGE": "#9463bd",
    "Replicon": "#65717f",
}


def _svg_text(value):
    return escape(str(value), quote=True)


def architecture_svg(sample, contigs, features, destination):
    """Draw every original contig grouped by prediction with coordinate ticks."""
    groups = {"chromosome": [], "plasmid": [], "unresolved": []}
    for contig in contigs.values():
        groups.get(contig["location"], groups["unresolved"]).append(contig)
    for group in groups.values():
        group.sort(key=lambda c: (c["plasmid_group"], -int(c["length_bp"]), c["contig_id"]))

    all_rows = []
    for location in ("chromosome", "plasmid", "unresolved"):
        all_rows.extend(groups[location])
    shown = all_rows
    maximum = max((int(c["length_bp"]) for c in shown), default=1)
    height = max(225, 156 + len(shown) * 32 + 38)
    width = 1200
    line_start, line_length = 250, 790
    mapped = defaultdict(list)
    for feature in features:
        mapped[feature["contig_id"]].append(feature)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Contig-resolved gene localization">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="25" y="38" font-family="Arial,sans-serif" font-weight="bold" font-size="22" fill="#202936">ChromoPlas | {_svg_text(sample)}</text>',
        '<text x="25" y="62" font-family="Arial,sans-serif" font-size="13" fill="#5d6571">Assembled contigs; length-scaled within this assembly. Positions are within each original contig.</text>',
    ]
    for x, cls, label in ((25, "ARG", "ARG"), (130, "VF", "Virulence factor"), (300, "MGE", "MGE")):
        parts.extend([f'<rect x="{x}" y="102" width="13" height="13" fill="{PALETTE[cls]}"/>',
                      f'<text x="{x+20}" y="113" font-family="Arial" font-size="12" fill="#313b47">{label}</text>'])
    previous_group = None
    for index, contig in enumerate(shown):
        y = 150 + index * 32
        location = contig["location"]
        if location != previous_group:
            parts.append(f'<text x="25" y="{y-9}" font-family="Arial" font-size="12" font-weight="bold" fill="{PALETTE[location]}">{location.upper()}</text>')
            previous_group = location
        size = int(contig["length_bp"])
        bar = max(3, line_length * size / maximum)
        label = str(contig["contig_id"])
        if len(label) > 25:
            label = label[:22] + "..."
        grouping = f' | {contig["plasmid_group"]}' if contig["plasmid_group"] else ""
        parts.append(f'<text x="25" y="{y+13}" font-family="Arial" font-size="12" fill="#243040">{_svg_text(label)}</text>')
        parts.append(f'<rect x="{line_start}" y="{y+1}" width="{bar:.2f}" height="14" rx="3" fill="{PALETTE[location]}" opacity="0.38" stroke="{PALETTE[location]}"/>')
        parts.append(f'<text x="1060" y="{y+13}" font-family="Arial" font-size="11" fill="#455363">{size:,} bp{_svg_text(grouping[:19])}</text>')
        for feature in mapped[contig["contig_id"]]:
            midpoint = (int(feature["start"]) + int(feature["end"])) / 2
            xpos = line_start + bar * midpoint / size
            color = PALETTE.get(feature["feature_class"], "#484848")
            tooltip = " | ".join([feature["feature_class"], feature["feature_name"],
                                  f'{feature["start"]}-{feature["end"]}', contig["contig_id"]])
            parts.append(
                f'<g><title>{_svg_text(tooltip)}</title>'
                f'<rect x="{xpos-3:.2f}" y="{y-4}" width="6" height="24" rx="1" fill="{color}" stroke="#ffffff" stroke-width=".5"/></g>'
            )
    foot_y = 165 + 32 * len(shown)
    parts.append(f'<text x="25" y="{foot_y}" font-family="Arial" font-size="12" fill="#5d6571">Predicted compartments; not experimentally verified. Unassigned contigs remain unresolved.</text>')
    parts.append('</svg>')
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(parts), encoding="utf-8")
    return destination
