# Contributing adapters

Install the development package from the repository root:

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
```

## Add a puzzle

1. Check the puzzle's rules and URL tokens against the cspuz revision in
   `rust/Cargo.lock` and the custom pzprjs variety. Compare the rules,
   accepted clue ranges and native FileIO before choosing aliases.
2. Add a puzzle entry in `src/puzzlekit/puzzles/` and register it in
   `src/puzzlekit/registry.py`. Reuse the codecs and FileIO logic in
   `src/puzzlekit/_adapters/` where behavior matches. Map cspuz answer
   items to pzpr marks for the specific puzzle.
3. Add a fixture file at `tests/fixtures/adapters/<puzzle_name>.json` and
   record verified coverage in [adapter compatibility](ADAPTERS.md).

## Verify the adapter

The test runner discovers each fixture file. Each case has a bare `path`
and expected `status`. Exportable cases include exact native `fileio`
text, including spaces and newlines. Use `record` for a sourced crawler ID.
Start with a small real puzzle from the sibling dataset's
`puzzlink_crawlers/logs/merged_puzzles.csv`. Add cases for distinct behavior
such as a meaningful alias, irregular rooms or partial answers.

Use Node 24+ and a built custom pzprjs checkout for the integration test.
It defaults to the sibling `pzprjs/` directory. Set `PUZZLEKIT_PZPRJS`
to select a different checkout. The test compares the source and normalized
puzzles, imports the generated state, compares its FileIO to the fixture
and checks complete answers with pzprjs. Pytest reports a skip when the
integration dependencies are missing.

From a Git checkout, run a bounded corpus audit for the original adapter set with
`python scripts/audit_v040_adapters.py --per-type 12` with Node 24+ on
`PATH`. The read-only audit samples the crawler CSV, reports solve failures
and timeouts by record, and checks the resulting states through pzprjs.
