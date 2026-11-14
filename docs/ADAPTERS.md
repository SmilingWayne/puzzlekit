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
| Circles and Squares | `circlesquare` | Cell shading |
| Context | `context` | Cell shading |
| Country Road | `country` | Cell loop |
| Dominion | `dominion` | Cell shading |
| Double Back | `doubleback` | Cell loop |
| Double Choco | `dbchoco` | Region boundaries |
| Fillmat | `fillmat` | Region boundaries |
| Fillomino | `fillomino` | Cell numbers and region boundaries |
| FiveCells | `fivecells` | Region boundaries |
| FourCells | `fourcells` | Region boundaries |
| Geradeweg | `geradeweg` | Cell loop |
| Hashiwokakero | `hashikake`, `hashi`, `bridges` | Single and double bridges |
| Heteromino | `heteromino` | Region boundaries |
| Heyawake | `heyawake` | Cell shading |
| Hitori | `hitori` | Cell shading |
| Kuromasu | `kurodoko` | Cell shading |
| Kurotto | `kurotto` | Cell shading |
| LITS | `lits` | Cell shading |
| Masyu | `mashu`, `masyu`, `pearl` | Cell loop |
| Minesweeper | `mines` | Mines and empty cells |
| Moon or Sun | `moonsun` | Cell loop |
| Nagenawa | `nagenawa` | Rectangular loops |
| Nanro | `nanro` | Cell numbers and empty marks |
| NIKOJI | `nikoji` | Region boundaries |
| Nonogram | `nonogram` | Cell shading |
| Norinori | `norinori` | Cell shading |
| Nurikabe | `nurikabe` | Cell shading |
| Nurimisaki | `nurimisaki` | Cell shading |
| Paintarea | `paintarea` | Cell shading |
| Putteria | `putteria` | Cell numbers and empty marks |
| Ring-ring | `ringring` | Rectangular loops |
| Ripple Effect | `ripple` | Cell numbers |
| Sashigane | `sashigane` | Region boundaries |
| Shakashaka | `shakashaka` | Triangles and empty cells |
| Shikaku | `shikaku` | Region boundaries |
| Shimaguni | `shimaguni` | Cell shading |
| Simple Loop | `simpleloop` | Cell loop |
| Slant | `gokigen` | Slashes |
| Slitherlink | `slither`, `slitherlink` | Vertex loop |
| Square Jam | `squarejam` | Region boundaries |
| Stostone | `stostone` | Cell shading |
| Sudoku | `sudoku` | Cell numbers |
| Sukoro | `sukoro` | Cell numbers and empty marks |
| Tapa | `tapa` | Cell shading |
| Tasquare | `tasquare` | Cell shading |
| Yajilin | `yajilin`, `yajirin` | Cell shading and cell loop |
| Yin-Yang | `yinyang` | Black and white circles |

## Inputs and limits

The adapters accept puzz.link, pzplus and pzpr-trace URLs, along with
`?p=type/width/height/data`, `?type/width/height/data` and bare puzzle paths.
PuzzleKit solves from the clues and rules and ignores player `state` and
`trace`. It rejects unknown query options and unsupported rule variants.
Yajilin's display flag `b`, Country Road's empty-room variant `e` and
Geradeweg's full-loop variant `f` are preserved.

- The new room, loop, and partition adapters require at least two rows and
  columns. Country Road requires a room boundary or a positive clue; otherwise
  cspuz may count the empty loop. Geradeweg
  requires a clue unless the full-loop variant is selected. Nagenawa requires
  a positive room clue, and Ring-ring requires an unblocked cell, to exclude
  empty loop answers. Double Back supports optional hole cells.
- FiveCells and FourCells accept blocked cells, unknown clues, and numeric
  clues 0–4. Heteromino supports blocked cells only; its numbered variant is
  not available in the pinned backend. Fillmat accepts clues 1–4 and `?`.
- Double Choco accepts color cells and clues 1–4095 or `?`. Circles and
  Squares accepts both circle colors, but on a square board requires a black
  clue to rule out cspuz's all-white answer. Dominion accepts positive clues
  1–4095; unknown clues are not supported because backend semantics differ.
- Sashigane supports directional clues, unnumbered corners and corner numbers
  0–255; the unspecified-direction clue is not supported. NIKOJI accepts
  positive clues 1–4095 and requires at least one clue.
- Paintarea accepts cell clues 0–4 and `?`. Sukoro accepts clues 1–4 or `?`
  and requires at least one clue to exclude the empty answer. Nanro accepts
  clues 1–4095 or `?`. Putteria accepts clues 1–4095 and fixed empty cells.
  Ripple Effect accepts clues 1–4095 or `?` and optional holes; holes cannot
  also carry clues. Multiple answers retain only established numbers and marks.
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
