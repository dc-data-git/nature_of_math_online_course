# Nature of Math Online Course

Problem bank and dashboard for *OpenStax Contemporary Mathematics*, built for an online course with parameterized exercise variants.

## Live dashboard (GitHub Pages)

After Pages is enabled: **https://dc-data-git.github.io/nature_of_math_online_course/**

## Local development

```bash
pip install -r requirements.txt
python scripts/build_bank.py
python scripts/build_dashboard.py
python -m http.server 8080
```

Open http://localhost:8080/dashboard.html

## Structure

| Path | Purpose |
|---|---|
| `bank.json` | Canonical problem bank (all sections) |
| `dashboard_data.json` | Precomputed view data for the dashboard |
| `dashboard.html` | Human-readable bank browser |
| `schema/problem.schema.json` | Item JSON schema |
| `scripts/generators/` | Per-section and auto generators |
| `classification/review_flags.md` | Items needing human review |

## Rebuild after changes

```bash
python scripts/build_bank.py && python scripts/build_dashboard.py
```

## License

Textbook content © OpenStax, CC BY 4.0. See item-level `license` fields in `bank.json`.
