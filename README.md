# PuzzleKit

PuzzleKit solves logic puzzles from links. Give it a puzz.link URL and get the cspuz solver's result, a pzpr FileIO solution, or a link you can open in
[pzpr-trace](https://pzpr-trace.net/).

The current development version uses the Rust
[cspuz_core](https://github.com/semiexp/cspuz_core) solver. It is being prepared
for the v0.4.0 release and its API differs from earlier versions.

## Installation

Once v0.4.0 is released, install it with:

```sh
pip install puzzlekit
```

Until then, `pip install puzzlekit` installs the latest published version,
which may have a different API. To try this development version, clone this
repository and run `python -m pip install .` from its root. Building from
source requires Rust, a C/C++ compiler, Git, and network access for the pinned
dependencies. Published wheels will not require Rust at runtime.

## Solve a puzzle

```python
import puzzlekit

result = puzzlekit.solve("https://puzz.link/p?nurikabe/2/2/1i")

print(result.status)          # unique
print(result.to_pzpr())       # puzzle and answer in pzpr FileIO format
print(result.to_trace_url())  # open the answer in pzpr-trace
```

`result.board` contains the original cspuz board as a Python dictionary;
`result.board_json` provides the same board as a JSON string. The board uses
cspuz's rendering format. `result.to_state()` returns the compressed state
used in the trace URL.

The result status is `unique`, `multiple`, `no_solution`, or `unknown`. For
the verified adapters below, a multiple-solution result contains only facts
that the solver establishes across solutions, leaving the other marks empty. FileIO and state export are
available for `unique` and `multiple` results; they raise `ValueError` for
`no_solution` or `unknown`.

## Puzzle support

See the [adapter compatibility guide](docs/ADAPTERS.md) for supported
puzzles, aliases and input limits. Other URLs can return a cspuz board when
the pinned backend supports them. The list returned by
`puzzlekit.supported_puzzles()` describes that upstream coverage.

## Development and licensing

Install with `python -m pip install -e '.[dev]'` and run
`python -m pytest -q`. See the [contributor guide](docs/CONTRIBUTING.md)
for adapter development and the [roadmap](docs/ROADMAP.md) for candidates.

PuzzleKit is MIT licensed. The bundled cspuz components have their own terms
in [LICENSE-cspuz](LICENSE-cspuz).
