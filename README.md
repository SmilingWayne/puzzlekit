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
python -m pytest -q
```

## Solve a link

```python
import puzzlekit

result = puzzlekit.solve("https://puzz.link/p?nurikabe/2/2/1i")
print(result.status)  # unique
print(result.board)   # cspuz board as a Python dict
print(result.board_json)  # the same board as a JSON string
print(result.to_pzpr())       # native pzpr FileIO text
print(result.to_state())      # compressed pzpr-trace state
print(result.to_trace_url())  # open in pzpr-trace
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

## Verified URL and state adapters

Fifteen standard puzzle types support cspuz solving and pzpr FileIO/state:
Nurikabe, Hitori, Kuromasu (`kurodoko`), Cave (`cave`, `bag`), Nurimisaki,
Slitherlink (`slither`), Masyu (`mashu`), Akari (`lightup`), Kurotto,
Shikaku, Heyawake, Aqre, LITS, Norinori and Yajilin. They accept puzz.link,
pzplus and pzpr-trace links, `?p=type/width/height/data`, `?type/...` and bare
paths.
Input `state` and `trace` parameters are ignored when solving: they are player
progress, not puzzle constraints. Other query options and puzzle variants are
rejected for these adapters until their rules are verified.

For these puzzles, `to_pzpr()` returns native FileIO containing clues and
confirmed player marks. On `multiple`, the exported state contains only facts
common to all solutions. On `no_solution` or `unknown`, state export raises
`ValueError`. `to_state()` compresses the native text with raw DEFLATE and
unpadded URL-safe Base64; `to_trace_url()` produces a pzpr-trace link.

The clue codec accepts native pzpr number formats, including Hitori's two-digit
base-36 clues and number16's extended values. The pinned cspuz URL decoder
cannot faithfully solve all of them: Hitori requires clues 1–35 or empty cells;
Nurikabe, Kuromasu, Cave, Nurimisaki and Shikaku require positive clues up to
4095 or `?`; Kurotto and numbered room puzzles also support 0. Yajilin's cspuz
decoder supports arrow numbers up to 255. Other values raise `ValueError` when solved. Room puzzles and Masyu/Yajilin currently require
at least two rows and columns. Rule variants are rejected except Yajilin's
display-only `b` flag, which is preserved.

The upstream loop constraint allows an empty loop, which pzpr rejects. Until
the backend enforces a nonempty loop, Slitherlink requires a positive clue,
Masyu at least one pearl, and Yajilin at least one adjacent pair of non-clue
cells. These conservative checks reject some otherwise valid inputs rather
than misreporting an empty-loop model as a pzpr solution.

The backend can dispatch other URLs, and `puzzlekit.supported_puzzles()` lists
upstream puzzle names; that list is **not** a claim of verified PuzzleKit
output support. FileIO and state outputs on other types raise
`ValueError`. Dataset problem text conversion is not part of `solve`. See
[the acceptance report](docs/V040_EXTENDED_ADAPTERS.md) for samples and scope.

The old dataset-text `solve(..., puzzle_type=...)`, per-puzzle solver API,
OR-Tools options and result shape are not supported by the new entry point.

The cspuz board is an upstream rendering representation, not a pzprjs state;
the adapters explicitly map its answer items to native player marks.
See [the integration notes](docs/CSPUZ_INTEGRATION.md).

## Development and licensing

The public entry point is `src/puzzlekit/api.py`, with result exports in
`core/result.py`. Puzzle registrations live in `src/puzzlekit/puzzles/` and
`registry.py`; shared URL and FileIO implementations live in `_adapters/`.
Their lightweight internal puzzle data stores only the clues and borders needed
for validation and export. `rust/src/lib.rs` bridges the pinned cspuz backend.
The `tests/test_v040_*.py` suites and `scripts/audit_v040_adapters.py` check
FileIO and state against the local dataset and custom pzprjs checkout.

The Rust dependency is pinned in [rust/Cargo.toml](rust/Cargo.toml) and
[rust/Cargo.lock](rust/Cargo.lock). CI builds and tests wheels separately from
the source distribution; the target matrix is documented in the workflow.
PuzzleKit is MIT licensed; the bundled cspuz components have their own license
terms in [LICENSE-cspuz](LICENSE-cspuz).
