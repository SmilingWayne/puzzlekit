# Adapter compatibility

These standard puzz.link puzzles support native pzpr FileIO and pzpr-trace
state export.

| Puzzle | Accepted path tokens | Answer marks |
| --- | --- | --- |
| Akari | `lightup`, `akari` | Bulbs and empty cells |
| Aqre | `aqre` | Cell shading |
| Cave | `cave`, `bag` | Cell shading |
| Heyawake | `heyawake` | Cell shading |
| Hitori | `hitori` | Cell shading |
| Kuromasu | `kurodoko` | Cell shading |
| Kurotto | `kurotto` | Cell shading |
| LITS | `lits` | Cell shading |
| Masyu | `mashu`, `masyu`, `pearl` | Cell loop |
| Norinori | `norinori` | Cell shading |
| Nurikabe | `nurikabe` | Cell shading |
| Nurimisaki | `nurimisaki` | Cell shading |
| Shikaku | `shikaku` | Region boundaries |
| Slitherlink | `slither`, `slitherlink` | Vertex loop |
| Yajilin | `yajilin`, `yajirin` | Cell shading and cell loop |

## Inputs and limits

The adapters accept puzz.link, pzplus and pzpr-trace URLs, along with
`?p=type/width/height/data`, `?type/width/height/data` and bare puzzle paths.
PuzzleKit solves from the clues and rules and ignores player `state` and
`trace`. It rejects unknown query options and unsupported rule variants.
Yajilin's display flag `b` is preserved.

- Hitori accepts clues from 1 to 35 and empty cells.
- Nurikabe, Kuromasu, Cave, Nurimisaki and Shikaku accept clues from 1 to
  4095 and `?`. Kurotto, Heyawake and Aqre also accept 0.
- Yajilin accepts arrow numbers from 0 to 255 and `?`.
- Masyu, Yajilin, Heyawake, Aqre, LITS and Norinori require at least two
  rows and two columns.
- The pinned cspuz loop constraint allows an empty loop. To exclude that
  case, PuzzleKit requires a positive clue in Slitherlink, a pearl in Masyu
  and a pair of orthogonally adjacent non-clue cells in Yajilin. Inputs that
  fail these checks raise `ValueError`.

See [cspuz integration](CSPUZ_INTEGRATION.md) for the board and export
semantics.
