# PuzzleKit

PuzzleKit is a Python package for solving logic puzzles from links. The
v0.4.0 development branch uses the Rust [cspuz_core](https://github.com/semiexp/cspuz_core)
solver backend through a bundled Python extension. This is an in-progress,
breaking migration from the earlier OR-Tools solvers; v0.4.0 has not yet been
released.

## Install

Once v0.4.0 is published, install a release with either:

```sh
pip install puzzlekit
# or
uv pip install puzzlekit
```

These commands currently install the latest available release, which may be
an older version with a different API. The planned release provides prebuilt
wheels for supported CPython and platform combinations; availability is
subject to successful release builds. A compatible wheel needs no Rust
installation at runtime. Building from source requires Rust, a C/C++ compiler,
Git and network access to fetch the pinned cspuz source and Rust dependencies.

For the development checkout (Python 3.10 or newer):

```sh
python -m venv .venv
# Activate the environment, then use either pip or uv:
python -m pip install -e '.[dev]'
# uv pip install -e '.[dev]'
python -m pytest -c tests/native-pytest.ini tests/test_nurikabe.py
```

## Solve a link

```python
import puzzlekit

result = puzzlekit.solve("https://puzz.link/p?nurikabe/2/2/1i")
print(result.status)  # unique
print(result.board)   # cspuz's JSON board, decoded as a Python dict
```

`solve_url` is an alias for `solve`. When the backend returns a board, `status` is
`unique`, `multiple`, `no_solution`, or `unknown` when the backend does not
report uniqueness. `result.unique` and `result.has_solution` are `True`,
`False`, or `None` when the answer is not known. `result.is_solved` means the
backend reports a unique assignment of its answer variables. An invalid or
unsupported URL raises `ValueError`; an internal backend failure raises
`RuntimeError`. Other backend errors can also surface as `ValueError`.

The board uses cspuz's rendering schema. For Nurikabe, it contains facts
common to all solutions, not an arbitrary complete solution. Clue items are
black; determined non-clue
cells are green `block` (black) or `dot` (white), and undetermined cells have
no answer item. Cell coordinates use cspuz's doubled grid: row `r`, column `c`
is `(y=2*r+1, x=2*c+1)`. In particular, a board for an unsatisfiable puzzle
is not a solution. Other genres can use different board items and conventions.

## Scope and migration

Nurikabe puzz.link URLs are the initial integration and test target. The
backend can dispatch more URLs, and `puzzlekit.supported_puzzles()` lists its
upstream puzzle names; this list is **not** a claim that PuzzleKit has tested
all those genres, variants or link formats. Dataset text to URL conversion is
a separate capability and is not part of `solve`; a converted link can use the
same entry point. Existing `decode`, `encode` and `convert` format utilities
remain separate and have their own format coverage.

The old dataset-text `solve(..., puzzle_type=...)`, per-puzzle solver API,
OR-Tools options and result shape are not supported by the new entry point.
Legacy modules remain in the repository during migration and are not covered
by the new installation or tests. Their old documentation and benchmark
numbers describe previous releases, not the current backend.

The cspuz board is an upstream rendering representation, not a pzprjs
`state` string. Mapping each puzzle's answer items into pzprjs player marks,
including partial and unsatisfiable boards, and encoding a share link are
future work. See [the integration notes](docs/CSPUZ_INTEGRATION.md).

## Development and licensing

The Rust dependency is pinned in [rust/Cargo.toml](rust/Cargo.toml) and
[rust/Cargo.lock](rust/Cargo.lock). CI builds and tests wheels separately from
the source distribution; the target matrix is documented in the workflow.
PuzzleKit is MIT licensed; the bundled cspuz components have their own license
terms in [LICENSE-cspuz](LICENSE-cspuz).
