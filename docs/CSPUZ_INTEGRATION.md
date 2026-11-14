# cspuz integration

`solve_url()` is an alias for `solve()`. The Python extension in
`rust/src/lib.rs` calls the pinned `cspuz_solver_backend::decode_and_solve`.
Registered adapters normalize puzzle links before solving. Other inputs
follow upstream dispatch, which includes puzz.link, Kudamono and specially
prefixed Penpa inputs. `supported_puzzles()` reports the upstream solve list.
Verified FileIO and state coverage is listed in [adapter compatibility](ADAPTERS.md).

`PuzzleResult.board` retains cspuz's rendering data and `board_json` exposes
it as JSON. The board's coordinates and item types follow the solver's
rendering conventions. For example, cell centers use coordinates
`(y=2*r+1, x=2*c+1)` on Nurikabe's doubled grid.

| Status | Meaning |
| --- | --- |
| `unique` | The model has a unique assignment of its answer variables. |
| `multiple` | The model has multiple assignments. Verified adapters export the facts common to all solutions and leave unknown marks blank. |
| `no_solution` | The model is unsatisfiable. The board can still contain clues. |
| `unknown` | The backend reports that uniqueness information is unavailable. |

`has_solution` and `unique` are booleans when known and `None` when
undetermined. `is_solved` is true for a unique result.

Invalid or unsupported inputs raise `ValueError`. Backend panics surface as
`RuntimeError`.

For `unique` and `multiple` results with a verified adapter, `to_pzpr()`
maps the board into native FileIO containing clues and player marks.
`to_state()` encodes its UTF-8 bytes with raw DEFLATE and unpadded URL-safe
Base64. `to_trace_url()` adds that state to the normalized puzzle path.
These exports raise `ValueError` when the adapter or an exportable result
is unavailable.
