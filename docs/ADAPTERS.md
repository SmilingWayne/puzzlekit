# Adapter compatibility

These standard puzz.link puzzles support native pzpr FileIO and pzpr-trace
state export.

| Puzzle | Accepted path tokens | Answer marks |
| --- | --- | --- |
| Akari | `lightup`, `akari` | Bulbs and empty cells |
| Aquapelago | `aquapelago` | Cell shading |
| Aqre | `aqre` | Cell shading |
| Araf | `araf` | Region boundaries |
| Ayeheya | `ayeheya` | Cell shading |
| Canal View | `canal` | Cell shading |
| Cave | `cave`, `bag` | Cell shading |
| Chained Block | `chainedb` | Cell shading |
| Choco Banana | `cbanana` | Cell shading |
| Chocona | `chocona` | Cell shading |
| Context | `context` | Cell shading |
| Fillomino | `fillomino` | Cell numbers and region boundaries |
| Hashiwokakero | `hashikake`, `hashi`, `bridges` | Single and double bridges |
| Heyawake | `heyawake` | Cell shading |
| Hitori | `hitori` | Cell shading |
| Kuromasu | `kurodoko` | Cell shading |
| Kurotto | `kurotto` | Cell shading |
| LITS | `lits` | Cell shading |
| Masyu | `mashu`, `masyu`, `pearl` | Cell loop |
| Minesweeper | `mines` | Mines and empty cells |
| Nonogram | `nonogram` | Cell shading |
| Norinori | `norinori` | Cell shading |
| Nurikabe | `nurikabe` | Cell shading |
| Nurimisaki | `nurimisaki` | Cell shading |
| Shakashaka | `shakashaka` | Triangles and empty cells |
| Shikaku | `shikaku` | Region boundaries |
| Shimaguni | `shimaguni` | Cell shading |
| Simple Loop | `simpleloop` | Cell loop |
| Slant | `gokigen` | Slashes |
| Slitherlink | `slither`, `slitherlink` | Vertex loop |
| Square Jam | `squarejam` | Region boundaries |
| Stostone | `stostone` | Cell shading |
| Sudoku | `sudoku` | Cell numbers |
| Tapa | `tapa` | Cell shading |
| Tasquare | `tasquare` | Cell shading |
| Yajilin | `yajilin`, `yajirin` | Cell shading and cell loop |
| Yin-Yang | `yinyang` | Black and white circles |

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
- Araf and Fillomino accept cell clues 1 to 4095; Square Jam also accepts
  `?`. Fillomino's `t` rule variant is not supported. Sudoku accepts square
  sizes 4, 6, 9, 16 and 25, with clues from 1 to the board size. For a
  multiple-solution Sudoku, only determined numbers are exported; the
  backend's candidate sets are not player marks.
- Hashiwokakero requires at least two islands, each with a clue from 1 to 8
  or `?`. Tapa supports numeric and unknown clue lists but requires a
  nonzero or unknown clue. Nonogram accepts outside clues 1 to 255 and empty
  outside slots; unknown and zero clues are not supported.
- Shakashaka requires a positive clue or an irregular connected white area
  before any triangles are placed; either forces at least one triangle. The
  `nosquare` variant is not supported. Stostone requires an even number of
  rows and accepts room clues 1 to 4095 and `?`.
- Masyu, Yajilin, Heyawake, Aqre, LITS and Norinori require at least two
  rows and two columns.
- Ayeheya, Chocona, Shimaguni, Aquapelago, Chained Block, Choco Banana,
  Context, Canal View and Tasquare also require at least two rows and columns.
- Araf, Fillomino, Square Jam, Hashiwokakero, Shakashaka, Slant, Simple
  Loop, Stostone, Tapa and Yin-Yang require at least two rows and columns.
- Ayeheya rooms must be rotationally symmetric. Heyawake and Ayeheya
  require a positive room clue or a row or column crossing at least two room
  boundaries; either condition excludes cspuz's all-white solution, which
  pzpr rejects. Chocona, Context and Canal View require a positive clue,
  and Tasquare requires at least one clue, for the same reason.
- The pinned cspuz loop constraint allows an empty loop. To exclude that
  case, PuzzleKit requires a positive clue in Slitherlink, a pearl in Masyu
  and a pair of orthogonally adjacent non-clue cells in Yajilin. Inputs that
  fail these checks raise `ValueError`. Simple Loop must have at least one
  unblocked cell to exclude the empty loop.

See [cspuz integration](CSPUZ_INTEGRATION.md) for the board and export
semantics.
