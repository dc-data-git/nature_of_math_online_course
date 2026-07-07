"""SVG diagram generators for parameterized figures."""

from __future__ import annotations

import html


def venn_two_set(
    labels: tuple[str, str] = ("A", "B"),
    shade: str = "A",
    width: int = 320,
    height: int = 200,
) -> str:
    """Two-circle Venn diagram. shade: A, B, A∩B, A∪B, A-B, B-A, outside, none."""
    la, lb = html.escape(labels[0]), html.escape(labels[1])
    cx1, cx2, cy, r = 120, 200, 100, 70

    def circle(cx: int, cy: int, r: int, fill: str, opacity: float = 0.35) -> str:
        return (
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="#333" stroke-width="2"/>'
        )

    fills = {
        "A": ("#2f6fed", "none"),
        "B": ("none", "#2f6fed"),
        "A∩B": ("#2f6fed", "#2f6fed"),
        "A∪B": ("#2f6fed", "#2f6fed"),
        "A-B": ("#2f6fed", "none"),
        "B-A": ("none", "#2f6fed"),
        "outside": ("none", "none"),
        "none": ("none", "none"),
    }
    fa, fb = fills.get(shade, ("none", "none"))
    union_fill = "#eaf1ff" if shade == "A∪B" else "none"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Venn diagram">
  <rect width="100%" height="100%" fill="#fff"/>
  {f'<rect x="10" y="10" width="{width-20}" height="{height-20}" fill="{union_fill}" stroke="#ccc" rx="8"/>' if shade == "A∪B" else ""}
  {circle(cx1, cy, r, fa)}
  {circle(cx2, cy, r, fb)}
  <text x="{cx1}" y="30" text-anchor="middle" font-size="16" font-family="sans-serif">{la}</text>
  <text x="{cx2}" y="30" text-anchor="middle" font-size="16" font-family="sans-serif">{lb}</text>
</svg>'''
    return svg


def media_entry(template: str, params: dict, svg: str) -> dict:
    return {
        "type": "diagram",
        "template": template,
        "params": params,
        "render": "inline_svg",
        "svg": svg,
    }
