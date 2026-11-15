# Adapter compatibility

These standard puzz.link puzzles support native pzpr FileIO and pzpr-trace
state export.

| Puzzle | Accepted path tokens | Answer marks |
| --- | --- | --- |
| Akari | `lightup`, `akari` | Bulbs and empty cells |
| Akichiwake | `akichi` | Cell shading |
| All or Nothing | `nothing` | Cell loop |
| Aqre | `aqre` | Cell shading |
| Aquapelago | `aquapelago` | Cell shading |
| Aquarium | `aquarium` | Cell shading |
| Araf | `araf` | Region boundaries |
| Archipelago | `archipelago` | Cell shading |
| Ayeheya | `ayeheya` | Cell shading |
| Barns | `barns` | Cell loop |
| Bramble | `bramble` | Cell shading |
| Canal View | `canal` | Cell shading |
| Cave | `cave`, `bag` | Cell shading |
| Chained Block | `chainedb` | Cell shading |
| Choco Banana | `cbanana` | Cell shading |
| Chocona | `chocona` | Cell shading |
| Circles and Squares | `circlesquare` | Cell shading |
| City Space | `cityspace` | Cell shading |
| Cocktail Lamp | `cocktail` | Cell shading |
| Context | `context` | Cell shading |
| Coral | `coral` | Cell shading |
| Country Road | `country` | Cell loop |
| Creek | `creek` | Cell shading |
| Cross the Streams | `cts` | Cell shading |
| Detour | `detour` | Cell loop |
| Disconnection | `disco` | Cell shading |
| Dominion | `dominion` | Cell shading |
| Doppelblock | `doppelblock` | Cell numbers and blocks |
| Double Back | `doubleback` | Cell loop |
| Double Choco | `dbchoco` | Region boundaries |
| Easy as ABC | `easyasabc` | Letters and empty marks |
| Energy Walk | `energywalk` | Cell loop |
| Fillmat | `fillmat` | Region boundaries |
| Fillomino | `fillomino` | Cell numbers and region boundaries |
| FiveCells | `fivecells` | Region boundaries |
| Forest Walk | `forestwalk` | Cell loop |
| FourCells | `fourcells` | Region boundaries |
| Geradeweg | `geradeweg` | Cell loop |
| Guide Arrow | `guidearrow` | Cell shading |
| Hashiwokakero | `hashikake`, `hashi`, `bridges` | Single and double bridges |
| Heteromino | `heteromino` | Region boundaries |
| Heyawake | `heyawake` | Cell shading |
| Hitori | `hitori` | Cell shading |
| Hotaru Beam | `firefly` | Cell paths |
| Ice Walk | `icewalk` | Cell loop |
| Inverse LITSO | `invlitso` | Cell shading |
| Kakuro | `kakuro` | Cell numbers |
| Koburin | `koburin` | Cell shading and cell loop |
| Kropki | `kropki` | Cell numbers |
| Kuromasu | `kurodoko` | Cell shading |
| Kurotto | `kurotto` | Cell shading |
| La Paz | `lapaz` | Cell shading and region boundaries |
| Light and Shadow | `lightshadow` | Black and white shading |
| Litherslink | `lither` | Vertex lines |
| LITS | `lits` | Cell shading |
| Lohkous | `lohkous` | Region boundaries |
| Loop Special | `loopsp` | Cell loops |
| Masyu | `mashu`, `masyu`, `pearl` | Cell loop |
| Minesweeper | `mines` | Mines and empty cells |
| Moon or Sun | `moonsun` | Cell loop |
| Morning Walk | `morningwalk` | Cell loop |
| Nagenawa | `nagenawa` | Rectangular loops |
| Nanro | `nanro` | Cell numbers and empty marks |
| NIKOJI | `nikoji` | Region boundaries |
| No Three | `nothree` | Cell shading |
| Nonogram | `nonogram` | Cell shading |
| Norinori | `norinori` | Cell shading |
| Norinuri | `norinuri` | Cell shading |
| Nurikabe | `nurikabe` | Cell shading |
| Nurikabe Loop | `nuriloop` | Cell loop |
| Nurimisaki | `nurimisaki` | Cell shading |
| Nuritwin | `nuritwin` | Cell shading |
| Paintarea | `paintarea` | Cell shading |
| Pentominous | `pentominous` | Region boundaries and piece letters |
| Putteria | `putteria` | Cell numbers and empty marks |
| Reflect Link | `reflect` | Cell loop |
| Regional Yajilin | `yajilin-regions`, `yajirin-regions` | Cell shading and cell loop |
| Ring-ring | `ringring` | Rectangular loops |
| Ripple Effect | `ripple` | Cell numbers |
| Roma | `roma` | Cell arrows |
| Sansa Road | `sansaroad` | Cell shading |
| Sashigane | `sashigane` | Region boundaries |
| Shakashaka | `shakashaka` | Triangles and empty cells |
| Shikaku | `shikaku` | Region boundaries |
| Shimaguni | `shimaguni` | Cell shading |
| Simple Gako | `simplegako` | Cell numbers |
| Simple Loop | `simpleloop` | Cell loop |
| Skyscrapers | `skyscrapers` | Cell numbers |
| Slant | `gokigen` | Slashes |
| Slitherlink | `slither`, `slitherlink` | Vertex loop |
| Snake | `snake` | Cell shading |
| Square Jam | `squarejam` | Region boundaries |
| Star Battle | `starbattle` | Stars and empty marks |
| Stostone | `stostone` | Cell shading |
| Sudoku | `sudoku` | Cell numbers |
| Sukoro | `sukoro` | Cell numbers and empty marks |
| Tapa | `tapa` | Cell shading |
| Tasquare | `tasquare` | Cell shading |
| Tetro Chain-CTB | `tetroctb` | Cell shading |
| Tetro Chain-K | `tetrochaink` | Cell shading |
| Tetro Chain-Y | `tetrochain` | Cell shading |
| Tetrominous | `tetrominous` | Region boundaries and piece letters |
| Water Walk | `waterwalk` | Cell loop |
| Yajilin | `yajilin`, `yajirin` | Cell shading and cell loop |
| Yajisan-Kazusan | `yajikazu` | Cell shading |
| Yin-Yang | `yinyang` | Black and white circles |

## Inputs and limits

- Archipelago requires a clue to exclude empty shading. City Space requires at
  least 2×2; both accept clues 1–4095 and `?`.
- Bramble and Tetro Chain-CTB require a positive room clue to exclude empty
  shading. Tetro Chain-CTB does not accept `?`; Nuritwin accepts 0–4095 or `?`.
  Disconnection and All or Nothing require at least 2×2, and All or Nothing
  requires a room boundary to exclude an empty loop.
- Tetro Chain-Y accepts arrow clues 0–255 or `?` and requires a positive arrow
  pointing into the grid. Tetro Chain-K requires a black or gray dot; Sansa Road
  accepts only triangle clues in cells. Neither accepts a bottom-right dot,
  which the pinned backend cannot preserve.
- Nurikabe Loop accepts positive clues below 4096 whose sum is smaller than the
  grid area; this excludes the empty loop and differing zero/unknown semantics.
  Regional Yajilin supports the `o` rule flag. Koburin supports `o`, `m` and `b`
  flags and requires adjacent non-clue cells to exclude an empty loop.
- Pentominous and Tetrominous support holes, unknown clues and given borders.
  Piece letters are inferred only for fully determined regions. La Paz supports
  the standard variant without holes; Snake accepts outside numbers up to the
  corresponding row or column length, capped at 255.
  Barns, Litherslink and Loop Special require at least two rows and columns.

- Akichiwake supports the `x` variant and room clues 0–4095; unknown
  clues are unsupported. It requires a zero clue or a row or column crossing
  at least two room boundaries to exclude cspuz's empty shading. Inverse
  LITSO requires a room larger than four cells for the same reason.
- Aquarium supports the `r` variant, outside clues 0–255, and requires at
  least one positive outside clue. Coral accepts outside clues 1–255 or
  empty slots. Cross the Streams accepts clues 1–255, `?`, `*`, and empty slots.
- Creek accepts vertex clues 0–4 or `?` and requires a positive clue. No
  Three accepts ordinary dots and requires at least one dot. Both conditions
  exclude cspuz's empty shading. Norinuri accepts clues 1–4095 or `?`.
- Yajisan-Kazusan accepts arrow numbers 0–255 or `?`; at least one positive
  arrow must point into the grid, and positive arrows cannot point outside.
  Guide Arrow accepts directions 1–4 or `?` and requires an in-grid goal
  without an arrow. Cocktail Lamp accepts room clues 0–4095 or `?`.
- Detour accepts room clues 0–4095 or `?`. Reflect Link accepts a cross or
  triangle, with triangle numbers 1–15 or an unnumbered triangle. Hotaru
  Beam requires at least one directional clue, numbered 0–255 or `?`.
- Ice, Forest, Water, Morning and Energy Walk support the `f` variant and
  clues 1–4095 or `?`; a colored cell cannot also contain a clue. These
  new shading, loop and partition adapters require at least two rows and
  columns, except Kakuro, which accepts positive dimensions.
- Roma accepts arrow clues 1–4 and requires a goal. Star Battle requires a
  square board and a positive star count. Kropki requires a square board and
  complete packed circle data. Simple Gako accepts positive clues 1–4095;
  unknown given numbers are unsupported.
- Skyscrapers and Doppelblock require square boards. Easy as ABC accepts a
  letter count from 1 to the smaller board dimension, up to 26. Outside and
  cell clues must be within their respective puzzle ranges; Doppelblock's
  outside sums can be 0–255. Kakuro accepts sums 0–45 or empty clues, and
  treats a zero sum as unspecified to match pzpr while retaining it in FileIO.
- Light and Shadow accepts encoded clues below 4096 and requires at least one
  clue. Lohkous requires at least one segment clue with digits 1–9 or `?`.

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
