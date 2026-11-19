# PuzzleKit

[![PyPI](https://img.shields.io/pypi/v/puzzlekit)](https://pypi.org/project/puzzlekit/)
[![Python](https://img.shields.io/pypi/pyversions/puzzlekit)](https://pypi.org/project/puzzlekit/)
[![License](https://img.shields.io/pypi/l/puzzlekit)](https://github.com/SmilingWayne/puzzlekit/blob/main/LICENSE)
[![CI](https://github.com/SmilingWayne/puzzlekit/actions/workflows/ci_pr.yml/badge.svg)](https://github.com/SmilingWayne/puzzlekit/actions/workflows/ci_pr.yml)

**Solve logic puzzles from a [puzz.link](https://puzz.link/) URL, and open the answer in [pzpr-trace](https://pzpr-trace.net/).**

PuzzleKit is a thin Python layer over the Rust [cspuz_core](https://github.com/semiexp/cspuz_core)
constraint solver. Give it a puzzle link and it returns the solution status,
the solver's board, the answer in [pzpr](https://github.com/robx/pzprjs)
FileIO format, and a pzpr-trace link that restores the puzzle with the answer
filled in.

- **Link in, answer out.** Works with the puzzle links you already have, in the
  pzpr format used by puzz.link and pzpr-trace.
- **Native pzpr output.** The exported answer is the same text pzpr saves, so
  any pzpr-based tool can load it.
- **Tells you about uniqueness.** Results are `unique`, `multiple`,
  `no_solution` or `unknown`; for multiple solutions you get the marks that
  hold in all of them.
- **Install and go.** Prebuilt wheels for Linux, macOS and Windows. No Rust
  toolchain and no other Python dependencies.

## Installation

```sh
pip install puzzlekit
# or
uv add puzzlekit          # in a uv project
uv pip install puzzlekit  # in any virtual environment
```

Requires Python 3.10 or newer. Wheels are published for Linux (x86-64 and
ARM64, glibc), macOS (Apple silicon and Intel) and Windows (x86-64). One wheel
per platform serves every supported Python version. On other
platforms pip builds from source, which needs Rust, a C/C++ compiler, Git and
network access for the pinned dependencies.

## Quick start

```python
import puzzlekit

result = puzzlekit.solve("https://puzz.link/p?slither/3/2/h17d")

print(result.status)          # unique
print(result.to_pzpr())       # puzzle and answer in pzpr FileIO format
print(result.to_trace_url())  # open the answer in pzpr-trace
```

```text
pzprv3.1
slither
2
3
. . 1 
2 . 3 
0 0 0 
0 0 0 
1 1 -1 -1 
1 -1 -1 1 
1 -1 -1 
-1 1 1 
1 1 1 
```

```text
https://pzpr-trace.net/p?state=K6gqKCoz1jPkKs7JLMlILeIy4jLm0lPQUzBU4DICUsYKXAYKIAijDIEyumDEBWMgMbnAXEOIMiAFAA&slither/3/2/h12g3
```

The trace link opens the puzzle in [pzpr-trace](https://pzpr-trace.net/) with
the solution already drawn.

### Input

`solve()` takes a single string. All of these are equivalent:

```python
puzzlekit.solve("https://puzz.link/p?slither/3/2/h17d")   # puzz.link URL
puzzlekit.solve("?slither/3/2/h17d")                      # query only
puzzlekit.solve("slither/3/2/h17d")                       # bare path
puzzlekit.solve("https://pzpr-trace.net/p?slither/3/2/h17d")  # trace link
```

The host is ignored; only the puzzle path (`type/columns/rows/data`) matters.
A `state=` parameter in a trace link is skipped. The path starts with the
puzzle's URL token, such as `slither`, `nurikabe` or `yajilin`. The tokens
and aliases for each puzzle are in the [adapter guide](https://github.com/SmilingWayne/puzzlekit/blob/main/docs/ADAPTERS.md).

Dataset text, a puzzle type argument and legacy solver options (as in
PuzzleKit 0.3) are not accepted; `solve()` raises `ValueError` for them.

### Output

`solve()` returns a `PuzzleResult`:

| Member | Description |
| --- | --- |
| `status` | `unique`, `multiple`, `no_solution` or `unknown` (see below). |
| `has_solution` | `True`, `False`, or `None` when undetermined. |
| `unique` | `True` for one solution, `False` for several, `None` if unknown. |
| `is_solved` | `True` when the status is `unique`. |
| `board` | The cspuz board as a Python `dict` (cspuz's rendering format). |
| `board_json` | The same board as a JSON string. |
| `normalized_url` | The puzzle link after PuzzleKit's normalization. |
| `to_pzpr()` | Puzzle and answer in pzpr FileIO text. |
| `to_state()` | The compressed state used by pzpr-trace. |
| `to_trace_url()` | A pzpr-trace link that restores puzzle and answer. |

| Status | Meaning |
| --- | --- |
| `unique` | Exactly one solution. |
| `multiple` | Several solutions. Exports contain only the marks shared by all of them; the rest stay empty. |
| `no_solution` | The puzzle has no solution. |
| `unknown` | The solver could not determine uniqueness. |

`to_pzpr()`, `to_state()` and `to_trace_url()` work for `unique` and
`multiple` results of the supported puzzles below. For `no_solution` and
`unknown` they raise `ValueError`, as they do for puzzles without a verified
adapter. Unreadable or unsupported input raises `ValueError`; an internal
solver failure raises `RuntimeError`.

`board` is available for every puzzle the pinned backend can solve, even when
there is no pzpr export. `puzzlekit.supported_puzzles()` lists the backend's
coverage; this is wider than the verified list below.

## Supported puzzles

<!-- puzzle-summary:start -->
PuzzleKit currently supports **137** of the **346** puzzle types registered in pzpr. [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset) holds 39,405 problems (33,692 with answers) for 77 of them.
<!-- puzzle-summary:end -->

The [puzzle table](https://github.com/SmilingWayne/puzzlekit/blob/main/docs/PUZZLES.md) lists every pzpr puzzle with its support
status, dataset size and largest board. The names are pzpr IDs, so they can be
pasted straight into pzpr-trace.
The [adapter guide](https://github.com/SmilingWayne/puzzlekit/blob/main/docs/ADAPTERS.md) gives each puzzle's URL tokens, answer
marks and known limits.

"Supported" means a verified adapter: URL solving, native pzpr FileIO and
pzpr-trace state, checked against real puzzles and the custom
[pzprjs](https://github.com/SmilingWayne/pzprjs-trace) used by pzpr-trace.

## Upgrading from 0.3

0.4 is a rewrite. The OR-Tools solvers and the dataset-text interface were
removed in favor of the cspuz backend and puzzle URLs. `solve()` now takes a
URL and returns a `PuzzleResult`. Pin `puzzlekit<0.4` if you depend on the
old API.

## Related projects

- [puzz.link](https://puzz.link/) and [pzprjs](https://github.com/robx/pzprjs) — the puzzle player and the
  pzpr format PuzzleKit reads and writes.
- [pzpr-trace](https://pzpr-trace.net/) — view and replay puzzle states; the target of `to_trace_url()`.
- [cspuz_core](https://github.com/semiexp/cspuz_core) — the Rust constraint solver and puzzle models PuzzleKit
  builds on, and [cspuz-solver2](https://github.com/semiexp/cspuz-solver2), a web solver built on it.
- [Penpa+](https://github.com/swaroopg92/penpa-edit) — a general puzzle editor and solver-checker.
- [puzzlekit-dataset](https://github.com/SmilingWayne/puzzlekit-dataset) — about 40,000 puzzle instances used to test PuzzleKit.
- [puzzlekit-web](https://github.com/SmilingWayne/puzzlekit-web) — a step-by-step, explainable solver in the browser.

## Development

```sh
git clone https://github.com/SmilingWayne/puzzlekit
cd puzzlekit
python -m pip install -e '.[dev]'
python -m pytest -q
```

Building needs Rust, a C/C++ compiler and Git. The [contributor guide](https://github.com/SmilingWayne/puzzlekit/blob/main/docs/CONTRIBUTING.md)
covers adding a puzzle, and [cspuz integration](https://github.com/SmilingWayne/puzzlekit/blob/main/docs/CSPUZ_INTEGRATION.md)
describes the backend bridge. [Releasing](https://github.com/SmilingWayne/puzzlekit/blob/main/docs/RELEASING.md) lists the release checklist.

## License

PuzzleKit is released under the [MIT license](https://github.com/SmilingWayne/puzzlekit/blob/main/LICENSE). The bundled cspuz
components have their own terms in [LICENSE-cspuz](https://github.com/SmilingWayne/puzzlekit/blob/main/LICENSE-cspuz).
