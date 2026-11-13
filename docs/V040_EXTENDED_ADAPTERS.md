# v0.4 puzzle adapters: scope and acceptance

This iteration adds ten adapters to the five documented in
[V040_SHADING_ADAPTERS.md](V040_SHADING_ADAPTERS.md). All use the pinned cspuz
Rust backend and export the original board, semantic facts, native pzpr FileIO,
compressed pzpr-trace state, and a trace link. The output is a snapshot of
irrefutable facts, not a solving trace. `multiple` results preserve unknowns;
`no_solution` and `unknown` cannot be exported as answer states.

| Family | Types | Answer facts | Native FileIO |
| --- | --- | --- | --- |
| Cell shading | Nurikabe, Hitori, Kuromasu, Cave, Nurimisaki, Kurotto | black / white / unknown cells | `pzprv3` |
| Vertex loop | Slitherlink | outer and internal line / no-line / unknown edges | `pzprv3.1` |
| Cell loop | Masyu | internal line / no-line / unknown edges | `pzprv3` |
| Bulbs | Akari | bulb / no bulb / unknown cells | `pzprv3` |
| Partition | Shikaku | boundary / no boundary / unknown edges | `pzprv3` |
| Room shading | Heyawake, Aqre, LITS, Norinori | room boundaries plus black / white / unknown cells | `pzprv3.1` |
| Mixed loop and shading | Yajilin | black / white / unknown cells and internal edges | `pzprv3` |

`vertical` edge rows are left-to-right borders, and `horizontal` edge rows are
top-to-bottom borders; `true` means a line/boundary, `false` means no
line/boundary, and `null` means unknown. Slitherlink's vertical matrix has
`height × (width + 1)` entries and horizontal has `(height + 1) × width`;
other loop/partition types use `height × (width - 1)` and `(height - 1) × width`.
Yajilin's backend omits edges touching a clue or a determined black cell; the
adapter marks them absent because those edges cannot be on the loop. Room
numbers are indexed by room but the native pzpr cell carrying a clue is the
leftmost, then topmost, cell in that room. Region IDs in the semantic result
are strings in row-major component discovery order.

The supported URL sources, aliases, clue limits, variant handling, minimum
sizes and conservative empty-loop guards are in the [README](../README.md).
In particular, cspuz's loop primitive permits an empty loop; the guard is an
explicit limitation, not proof that all rejected puzzles have no solution.
Yajilin display flag `b` is preserved. Full-loop, outside and other unverified
rule variants are rejected. Extra unused Yajilin body data is rejected rather
than silently discarded. Unsupported legal clue magnitudes can be decoded and
re-encoded, but are rejected by `solve` where the backend cannot represent them.

## Verification

[`test_v040_extended.py`](../tests/test_v040_extended.py) contains at least two
small real crawler records for each of the ten new types, plus an irregular
Aqre room regression. It also tests a multiple and an unsatisfiable example for
each new type, variants, URL forms, the empty-loop guard and backend clue
limits. [`test_v040_shading.py`](../tests/test_v040_shading.py) covers the
original five. The integration checks use the custom pzprjs `state.target`,
`state.changes` and `state.apply` against the input puzzle, compare FileIO and
all available answer marks, and call pzpr's answer checker for complete
boards. This includes non-square grids and both cell- and edge-based answers.
Node 24+ and the custom pzprjs checkout are required for those checks; they are
not Python package runtime dependencies.

A separate read-only audit selected the 12 smallest CSV records per type with
both dimensions between 2 and 7 (only 10 Kurotto records met the filter). With
an individual four-second subprocess limit, it considered 178 records:
172 unique, two multiple, four explicitly rejected, zero timeouts. All 174
resulting states were imported by the custom pzprjs, compared with the source
puzzle and checked when complete. The rejections were Hitori `hitori0256`
(out-of-range cspuz clues), Masyu `masyu2066` (no pearl, so cspuz may count an
empty loop), Yajilin `yajilin11075` (its clue layout does not rule out an empty
loop), and Yajilin `yajilin2790` (extra unused URL body data). These are
limitations, not no-solution results. Another read-only comparison decoded and
re-encoded 50 crawler URLs per type, 750 in total, and compared their initial
native pzpr boards without mismatches. The source corpus is not deduplicated
against the dataset's JSON files.

Repeat the bounded solve/state audit with:

```sh
PATH=/path/to/node24/bin:$PATH python scripts/audit_v040_adapters.py --per-type 12
```

The audit reports individual errors and timeouts. Its pzprjs check fails the
command on a state mismatch; inspect the reported solve rejections separately.
The automated regression suite is:

```sh
python -m pytest -c tests/native-pytest.ini tests/test_nurikabe.py tests/test_v040_shading.py tests/test_v040_extended.py tests/formats -q
```

Generated links for visual inspection:

- [Slitherlink](https://pzpr-trace.net/p?state=K6gqKCoz1jPkKs7JLMlILeIy4jLm0lPQUzBU4DICUsYKXAYKIAijDIEyumDEBWMgMbnAXEOIMiAFAA&slither/3/2/h12g3)
- [Masyu](https://pzpr-trace.net/p?state=K6gqKCoz5spNLM4o5TIGQj0FQwU9BSAFYsB4hiC2rqECEEHYYCYSDQA&mashu/3/3/313)
- [Akari](https://pzpr-trace.net/p?state=K6gqKCoz5srJTM8oKS3gMgZCIwVlBW0FLhABpECEsgIXAA&lightup/3/3/2n)
- [Shikaku](https://pzpr-trace.net/p?state=K6gqKCoz5irOyMxOzC7lMuIy4TJUMFTQA0IuPQUjBRMQAySia6jApQtjQGkQEwA&shikaku/4/2/11i24g)
- [Aqre with irregular rooms](https://pzpr-trace.net/p?state=K6gqKCoz1jPkSiwsSuUyBUJDBQgEMgyAEMgwAPMNcIkYIsQgGCqNrsBQQQ_I0IOo1YNCLghlgGCCRc2hYkCmsoKygrYCiOSCUCAukKkNZmijiCKpBQA&aqre/5/5/v5kmlael1g010070)
- [Yajilin](https://pzpr-trace.net/p?state=K6gqKCoz5qpMzMrMyczjMgZCPQUQ5DLRMYAwoHxlBW0gBPLAFJSna6hgCCZ1DZE4KDQA&yajilin/3/3/c40e)

Slitherlink, Aqre and Yajilin were also opened on pzpr-trace.net and displayed
completed boards; the remaining links above were checked with the custom
pzprjs state importer and answer checker locally.
