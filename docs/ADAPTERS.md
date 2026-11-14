# Adapter compatibility

These standard puzz.link puzzles support native pzpr FileIO and pzpr-trace
state export.

| Puzzle | Accepted path tokens | Answer marks |
| --- | --- | --- |
| Akari | `lightup`, `akari` | Bulbs and empty cells |
| Aquapelago | `aquapelago` | Cell shading |
| Aqre | `aqre` | Cell shading |
| Ayeheya | `ayeheya` | Cell shading |
| Canal View | `canal` | Cell shading |
| Cave | `cave`, `bag` | Cell shading |
| Chained Block | `chainedb` | Cell shading |
| Choco Banana | `cbanana` | Cell shading |
| Chocona | `chocona` | Cell shading |
| Context | `context` | Cell shading |
| Heyawake | `heyawake` | Cell shading |
| Hitori | `hitori` | Cell shading |
| Kuromasu | `kurodoko` | Cell shading |
| Kurotto | `kurotto` | Cell shading |
| LITS | `lits` | Cell shading |
| Masyu | `mashu`, `masyu`, `pearl` | Cell loop |
| Minesweeper | `mines` | Mines and empty cells |
| Norinori | `norinori` | Cell shading |
| Nurikabe | `nurikabe` | Cell shading |
| Nurimisaki | `nurimisaki` | Cell shading |
| Shikaku | `shikaku` | Region boundaries |
| Shimaguni | `shimaguni` | Cell shading |
| Slitherlink | `slither`, `slitherlink` | Vertex loop |
| Tasquare | `tasquare` | Cell shading |
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
- Aquapelago, Chained Block, Choco Banana and Tasquare accept clues 1 to
  4095 and `?`. Minesweeper, Context and Canal View also accept 0.
- Ayeheya and Chocona accept room clues 0 to 4095 and `?`; Shimaguni
  accepts 1 to 4095 and `?`. The cspuz Chocona board renders a zero clue
  as `?`, although solving and exported FileIO retain zero.
- Masyu, Yajilin, Heyawake, Aqre, LITS and Norinori require at least two
  rows and two columns.
- Ayeheya, Chocona, Shimaguni, Aquapelago, Chained Block, Choco Banana,
  Context, Canal View and Tasquare also require at least two rows and columns.
- Ayeheya rooms must be rotationally symmetric. Heyawake and Ayeheya
  require a positive room clue or a row or column crossing at least two room
  boundaries; either condition excludes cspuz's all-white solution, which
  pzpr rejects. Chocona, Context and Canal View require a positive clue,
  and Tasquare requires at least one clue, for the same reason.
- The pinned cspuz loop constraint allows an empty loop. To exclude that
  case, PuzzleKit requires a positive clue in Slitherlink, a pearl in Masyu
  and a pair of orthogonally adjacent non-clue cells in Yajilin. Inputs that
  fail these checks raise `ValueError`.

See [cspuz integration](CSPUZ_INTEGRATION.md) for the board and export
semantics.
