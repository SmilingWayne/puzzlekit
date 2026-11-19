# PuzzleKit

Build a Python library that solves puzzle URLs with the pinned Rust cspuz
backend and exports verified answers as native pzpr FileIO and pzpr-trace
state.

- Keep the public API centered on puzzle URLs and `PuzzleResult`. Preserve the
  cspuz board and keep dataset-text conversion outside the solver.
- Register each verified puzzle in `src/puzzlekit/registry.py`. Share
  codecs where rules and encodings agree. Upstream dispatch alone establishes
  board support. FileIO support requires verification against custom pzprjs.
- Preserve clues, rules and unknown marks across formats. Add only cases that
  exercise distinct behavior in `tests/fixtures/adapters/<puzzle_name>.json`.
- Run `python -m pytest -q` on the current extension after changes. Use
  Node 24+ and the custom pzprjs checkout to verify state export. Report
  skipped checks.
- Update the [compatibility guide](docs/ADAPTERS.md) when support changes.
  Follow the [contributor guide](docs/CONTRIBUTING.md) for the adapter workflow.
- `docs/PUZZLES.md` and the README summary are generated: after changing adapters
  run `python scripts/puzzle_table.py render --write` (CI checks it). Dataset
  columns come from `docs/puzzle_table.json`, refreshed with `... collect`.
