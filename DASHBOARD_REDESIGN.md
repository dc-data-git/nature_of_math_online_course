# Dashboard redesign preview

Branch: `dashboard-redesign` (does not affect `main`).

## Preview locally

```bash
git checkout dashboard-redesign
python -m http.server 8080
```

Open http://localhost:8080/dashboard.html

## What changed

- Branded header (Nature of Math / OpenStax)
- Chapter buttons + section list (replaces 104-option dropdown)
- Section stats: exercises, items, coverage
- Simplified topic cards (less badge clutter)
- Review/coverage alerts compact in sidebar
- Bloom filter under "Advanced filters"
- Item viewer: serif stem, difficulty chips, Reviewer vs Student preview toggle
- Collapsible answer key
- **Warm linen palette** (stone/cream surfaces — not apartment-white)
- Subtle **dot + grid geometry** on page background; triangles/circles in header
- Geometric **logo mark** beside title; accent bar under header
- Topic cards with faint triangle watermark; problem card on warm paper with left accent

## Merge or discard

```bash
# Keep redesign
git checkout main && git merge dashboard-redesign

# Discard
git checkout main && git branch -D dashboard-redesign
```
