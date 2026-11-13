# v0.4 shading adapters: scope and acceptance

This first batch implements puzz.link clue decoding/encoding, cspuz solve, and
native pzpr text and compressed trace state for five standard puzzles. Their
intersection with the old PuzzleKit solvers, the custom pzprjs fork, cspuz and
the local inventory was checked against `assets/V040_PUZZLE_INVENTORY.md`.
Inventory counts are a snapshot and dataset and crawler records can overlap.

| Puzzle | pzpr PID | Dataset cases | Crawler URLs | Current adapter |
| --- | --- | ---: | ---: | --- |
| Nurikabe | `nurikabe` | 1,091 | 2,288 | complete for the documented standard encoding |
| Hitori | `hitori` | 941 | 475 | complete within the documented backend clue limits |
| Kuromasu | `kurodoko` | 537 | 516 | complete within the documented backend clue limits |
| Cave | `cave` (`bag`) | 416 | 433 | complete within the documented backend clue limits |
| Nurimisaki | `nurimisaki` | 100 | 1,156 | complete within the documented backend clue limits |

For a ten-puzzle candidate set, the next five are Slitherlink, Masyu, Heyawake,
Akari and Yajilin. These are inventory candidates, not claims that their
PuzzleKit state adapters are implemented. In particular, line and region
representations require separate mappings and verification.

## Contract

The result retains `board` exactly as returned by cspuz. For these five types,
`to_dict()` and `to_json()` additionally describe a row-major clue matrix and
black/white/unknown answers. The Rust implementations use irrefutable facts
for their answer variables. Their rendering conventions differ: `block` means
black for Nurikabe and Cave, while `fill` means black for Hitori, Kurodoko and
Nurimisaki; `dot` means white. Hitori can shade numbered cells. In the other
four puzzles, clue cells are intrinsically white. The serialized FileIO is
`pzprv3`: Nurikabe combines clues and marks; the other four store them in
separate grids. Extra line marks are absent because the solver does not infer
any. `to_pzpr()` returns that native text; `to_state()` compresses its UTF-8
bytes with raw DEFLATE and unpadded URL-safe Base64; `to_trace_url()` attaches
it to the canonical puzzle path.

`multiple` retains only common facts and leaves unknown cells blank. A
`no_solution` or `unknown` result cannot be exported as an answer state.
Player `state` and `trace` input is intentionally ignored when solving. The
parser rejects unrecognized query parameters or rule variants. `bag` is the
pzpr alias for Cave. The backend's clue limitations and accepted URL forms are
listed in the [README](../README.md). Values outside those solver limits can
still be round-tripped through the URL codec. This is not a dataset problem-text
converter or a migration of existing dataset files.

## Repeatable checks

Ten small real crawler records (two per puzzle) are fixed in
[`test_v040_shading.py`](../tests/test_v040_shading.py), including non-square
boards, unknown clues, the `bag` alias and pzpr's terminal `/`. Each solves
uniquely. The integration check opens each generated puzzle with the custom
pzprjs, decompresses and imports the state through `src-ui/state.js`, compares
clues and player marks, checks native FileIO equality, and runs pzpr's answer
checker. It also imports a multiple-solution Nurikabe as an incomplete state.
It also checks incomplete multiple-solution states for each of the five types
and rejects answer export for an unsatisfiable example of each. A separate
read-only spot check compared the decoded clues in 150 small crawler URLs
(30 per puzzle) against pzprjs, with no mismatches. The local integration
check uses the sibling checkout and Node 24+; set `PUZZLEKIT_PZPRJS`
to use another custom fork. When either dependency is unavailable, only that
integration test is skipped.

```sh
python -m pytest -c tests/native-pytest.ini tests/test_nurikabe.py tests/test_v040_shading.py tests/formats -q
```

The following links are generated from real crawler records and are convenient
for visual inspection:

- [Nurikabe: nurikabe1876](https://pzpr-trace.net/p?state=K6gqKCoz5sorLcrMTkxK5TLkMuEyUtBWUFYwVOACAA&nurikabe/4/1/2h1)
- [Hitori: hitori0021](https://pzpr-trace.net/p?state=VYoxCsAwDAN3vUKQMVPt5E_N1BBKh76-MvFShIx80nznehznuK810CXjwSZ3ouk4TS-6SDROeNZGbU0kOlSGiozCmsImGX-DzfEB&hitori/5/5/2141545324512133415222351)
- [Kuromasu: kurodoko0159](https://pzpr-trace.net/p?state=K6gqKCoz5souLcpPyc_O5zIBQj0FYwU9IOTSA1NmClwmCnoIEVMQQ1tBW0EZiMEMbQhDGcaASHIBAA&kurodoko/4/4/g3k64k5g)
- [Cave: cave0110](https://pzpr-trace.net/p?state=K6gqKCoz5kpOLEvlMuYy5TJT0INCLhBhhGCCoLECl7YCDAKZygoQzKWsAIFAJgA&cave/5/3/6l2l3)
- [Nurimisaki: nurimisaki0530](https://pzpr-trace.net/p?state=K6gqKCoz5sorLcrMzSxOzM7kMgZCPQVdBT0FBAWCXMoK2grKSBQIcgEA&nurimisaki/3/3/g.h.j)

The Kuromasu and Cave links were also opened on pzpr-trace.net and displayed
completed boards. The other three links have been checked via the custom
pzprjs state importer and answer checker locally.
