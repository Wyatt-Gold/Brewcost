# Brewcost — TODO

Tracks planned work and future improvements for Brewcost. Each bullet below is meant to be
tackled as its own commit/work session.

## Ingredients Tab

- Add a `brand` field for ingredients, and restrict `category` to a predefined list instead of
  free text (for now: Syrups, Add-ons, Extras). Both change what's stored for an ingredient, so
  they touch the same schema/repository/form code.
- Tighten up the add/update form: block null/empty required fields, cap free-text fields at
  100 characters, restrict numeric fields (e.g. cost per unit) to numbers only, give live
  red/green feedback on each field as it becomes valid/invalid, and only allow submitting once
  all required fields are filled in.
- Add a "bulk import" button that accepts a CSV of ingredients. Validate that all required
  columns are present (and no extra ones); if a row is missing data, skip it and tell the user
  which row/columns were the problem instead of silently failing.
- Add a filter feature for Brand and Category, plus a fuzzy search box for ingredient name. Each
  filter should only list values that actually exist in the database (and ideally show how many
  entries match each one). Do this after the `brand` field above exists, since filtering by brand
  depends on it.

## Calculator Screen

- Give each drink size its own fixed box in the calculator (no adding/removing sizes, instead default
  to 3: 12oz, 16oz, and 20oz), and make sure adding an ingredient row applies it to every size at
  once rather than just one.
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

- Add a `pytest` test suite for the database/repository layer (`ingredient_repository` and
  friends), since it's pure Python/SQL and doesn't need a Qt display to test — e.g. add an
  ingredient, confirm it round-trips through `get_all_ingredients`, update it, delete it, using a
  temporary SQLite file (or `:memory:`) instead of the real `brewcost.db`. Add `pytest` (and any
  test-only tools) to `requirements.txt`, or split into a `requirements-dev.txt`.
- Add a `.github/workflows/ci.yml` GitHub Actions workflow that runs that test suite on every
  push and pull request, optionally with a linter/formatter step (e.g. `ruff`) alongside it. Then,
  in the GitHub repo settings, turn on branch protection for `main` requiring that workflow to
  pass before a pull request can merge. The workflow alone only reports pass/fail, branch
  protection is what actually blocks broken code.
- (Optional, later) Once the app is packaged with PyInstaller, add a release workflow that builds
  the `.app` automatically on tags/releases.
