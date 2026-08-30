# Brewcost — TODO

Tracks planned work and future improvements for Brewcost. Each bullet below is meant to be
tackled as its own commit/work session.

## Ingredients Tab

- Add a filter feature for Brand and Category, plus a fuzzy search box for ingredient name. Each
  filter should only list values that actually exist in the database (and ideally show how many
  entries match each one). Do this after the `brand` field above exists, since filtering by brand
  depends on it.

## Calculator Screen

- Add two calculated values: the actual food cost, and a recommended selling price (calculated so
  food cost lands around 30% of the recommended price).

## Misc

- Let users save recipes so they can easily come back to them. A bigger, foundational feature
  (new table, new repository) on its own. Also allow this to be done by importing a CSV file
- Add calculator templates. Many drinks are just a base (e.g. latte, lemonade) plus a few
  syrups, so a saved template speeds up building similar drinks. Do this after recipe saving
  above, since templates are really just pre-filled recipes.

## CI/CD Pipeline

Goal: catch breakage automatically before it lands on `main`, instead of finding out after the
fact.

- ~~Add a `pytest` test suite for the database/repository layer~~ — done, see `tests/`. Also
  covers the ingredient form and calculator screens (headless, via `QT_QPA_PLATFORM=offscreen`).
- Add a `.github/workflows/ci.yml` GitHub Actions workflow that runs that test suite on every
  push and pull request, optionally with a linter/formatter step (e.g. `ruff`) alongside it. Then,
  in the GitHub repo settings, turn on branch protection for `main` requiring that workflow to
  pass before a pull request can merge. The workflow alone only reports pass/fail, branch
  protection is what actually blocks broken code.
- (Optional, later) Once the app is packaged with PyInstaller, add a release workflow that builds
  the `.app` automatically on tags/releases.
