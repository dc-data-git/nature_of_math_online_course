# Review flags

## Coverage model (updated)

Every textbook exercise now has **3 bank items** (intro / practice / challenge), each tagged with the exact exercise number. Coverage gaps in the dashboard should be empty when the build succeeds.

## Still needs adjunct review

- **Stems synthesized from PDF families** — calculation exercises (especially 5+) often have math stripped from PDFs; stems are parameterized templates, not verbatim book wording.
- **Answer key** — used where extracted; many sections have sparse AK text in PDF extraction.
- **Figure / Venn items** — inline SVG templates; verify against textbook diagrams.
- **Section 1.1 pilot pool** — 154 extra deep variants appended (pattern-tagged); may overlap exercise families.
- **Exercise counts from chapter PDFs** — bleed between sections is filtered heuristically; spot-check edge sections (e.g. 1.2, 3.3).

## Canvas

- `manual_rebuild` — diagram-heavy items
- `requires_conversion` — short answer with multiple acceptable forms
