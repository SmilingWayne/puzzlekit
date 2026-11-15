# PuzzleKit

PuzzleKit solves logic puzzles from links. Give it a puzz.link URL and get the cspuz solver's result, a pzpr FileIO solution, or a link you can open in
[pzpr-trace](https://pzpr-trace.net/).

The current development version uses the Rust
[cspuz_core](https://github.com/semiexp/cspuz_core) solver. It is being prepared
for the v0.4.0 release and its API differs from earlier versions.

## Installation

Once v0.4.0 is released, install it with:

```sh
pip install puzzlekit
```

Until then, `pip install puzzlekit` installs the latest published version,
which may have a different API. To try this development version, clone this
repository and run `python -m pip install .` from its root. Building from
source requires Rust, a C/C++ compiler, Git, and network access for the pinned
dependencies. Published wheels will not require Rust at runtime.

## Solve a puzzle

```python
import puzzlekit

result = puzzlekit.solve("https://puzz.link/p?nurikabe/2/2/1i")

print(result.status)          # unique
print(result.to_pzpr())       # puzzle and answer in pzpr FileIO format
print(result.to_trace_url())  # open the answer in pzpr-trace
```

`result.board` contains the original cspuz board as a Python dictionary;
`result.board_json` provides the same board as a JSON string. The board uses
cspuz's rendering format. `result.to_state()` returns the compressed state
used in the trace URL.

The result status is `unique`, `multiple`, `no_solution`, or `unknown`. For
the verified adapters below, a multiple-solution result contains only facts
that the solver establishes across solutions, leaving the other marks empty. FileIO and state export are
available for `unique` and `multiple` results; they raise `ValueError` for
`no_solution` or `unknown`.

## Puzzle support

See the [adapter compatibility guide](docs/ADAPTERS.md) for supported
puzzles, aliases and input limits. Other URLs can return a cspuz board when
the pinned backend supports them. The list returned by
`puzzlekit.supported_puzzles()` describes that upstream coverage.

### pzprjs and cspuz adapter targets

The current target set contains **145 puzzle types** registered in the custom
pzprjs checkout and dispatched by the pinned cspuz backend: **131 verified
adapters** and **14 candidates**. This is a static inventory, not a guarantee
that rules, variants, clues, URL formats or answer marks are compatible. Each
candidate still requires verification against pzprjs before FileIO and state
support can be claimed. Separate pzpr PIDs are counted separately; Numberlink's
standalone enumeration entry is outside this solve-dispatch inventory.

Snapshot: pzprjs `6a180ef71c29`, cspuz `d6424dc3da9f`. Update these lists
when adapters or the pinned backend change. The PID is the pzpr identifier;
it does not list every accepted URL alias.

<details>
<summary>Verified adapters (131)</summary>

| Puzzle | pzpr PID |
| --- | --- |
| Akari | `lightup` |
| Akichiwake | `akichi` |
| All or Nothing | `nothing` |
| Aqre | `aqre` |
| Aquapelago | `aquapelago` |
| Aquarium | `aquarium` |
| Araf | `araf` |
| Archipelago | `archipelago` |
| Ayeheya | `ayeheya` |
| Balloon Box | `balloon` |
| Barns | `barns` |
| Bosanowa | `bosanowa` |
| Bramble | `bramble` |
| Building Walk | `bdwalk` |
| Canal View | `canal` |
| Castle Wall | `castle` |
| Cave | `cave` |
| Chained Block | `chainedb` |
| Choco Banana | `cbanana` |
| Chocona | `chocona` |
| Circles and Squares | `circlesquare` |
| City Space | `cityspace` |
| Cocktail Lamp | `cocktail` |
| Coffee Milk | `coffeemilk` |
| Compass | `compass` |
| Context | `context` |
| Coral | `coral` |
| Country Road | `country` |
| Creek | `creek` |
| Cross the Streams | `cts` |
| Detour | `detour` |
| Disconnection | `disco` |
| Dominion | `dominion` |
| Doppelblock | `doppelblock` |
| Double Back | `doubleback` |
| Double Choco | `dbchoco` |
| Easy as ABC | `easyasabc` |
| Energy Walk | `energywalk` |
| Fillmat | `fillmat` |
| Fillomino | `fillomino` |
| FiveCells | `fivecells` |
| Forest Walk | `forestwalk` |
| FourCells | `fourcells` |
| Geradeweg | `geradeweg` |
| Guide Arrow | `guidearrow` |
| Hashiwokakero | `hashikake` |
| Hebi-Ichigo | `hebi` |
| Herugolf | `herugolf` |
| Heteromino | `heteromino` |
| Heyawake | `heyawake` |
| Hitori | `hitori` |
| Hotaru Beam | `firefly` |
| Ice Walk | `icewalk` |
| Inverse LITSO | `invlitso` |
| Isowatari | `isowatari` |
| Japanese Sums | `japanesesums` |
| Kakuro | `kakuro` |
| Key West | `keywest` |
| Koburin | `koburin` |
| Kropki | `kropki` |
| Kurodoko | `kurodoko` |
| Kurotto | `kurotto` |
| La Paz | `lapaz` |
| Light and Shadow | `lightshadow` |
| Litherslink | `lither` |
| LITS | `lits` |
| Lohkous | `lohkous` |
| Loop Special | `loopsp` |
| Masyu | `mashu` |
| Minesweeper | `mines` |
| Mintonette | `mintonette` |
| Moon or Sun | `moonsun` |
| Morning Walk | `morningwalk` |
| Nagenawa | `nagenawa` |
| Nanameguri | `nanameguri` |
| Nanro | `nanro` |
| Narrowfence | `narrow` |
| NIKOJI | `nikoji` |
| No Three | `nothree` |
| Nonogram | `nonogram` |
| Norinori | `norinori` |
| Norinuri | `norinuri` |
| Nuri-Maze | `nurimaze` |
| Nurikabe | `nurikabe` |
| Nurikabe Loop | `nuriloop` |
| Nurimisaki | `nurimisaki` |
| Nuritwin | `nuritwin` |
| Paintarea | `paintarea` |
| Pentominous | `pentominous` |
| Putteria | `putteria` |
| Reflect Link | `reflect` |
| Regional Yajilin | `yajilin-regions` |
| Ring-ring | `ringring` |
| Ripple Effect | `ripple` |
| Roma | `roma` |
| Sansa Road | `sansaroad` |
| Sashigane | `sashigane` |
| School Trip | `shugaku` |
| Sendai-Miyagi | `sendai` |
| Shakashaka | `shakashaka` |
| Shikaku | `shikaku` |
| Shimaguni | `shimaguni` |
| Simple Gako | `simplegako` |
| Simple Loop | `simpleloop` |
| Skyscrapers | `skyscrapers` |
| Slant | `gokigen` |
| Slash Pack | `slashpack` |
| Slitherlink | `slither` |
| Smullyanic Dynasty | `smullyan` |
| Snake | `snake` |
| Soul Mates | `soulmates` |
| Square Jam | `squarejam` |
| Star Battle | `starbattle` |
| Statue Park | `statuepark` |
| Stostone | `stostone` |
| Sudoku | `sudoku` |
| Sukoro | `sukoro` |
| Tapa | `tapa` |
| Tasquare | `tasquare` |
| Tents | `tents` |
| Tetro Chain-CTB | `tetroctb` |
| Tetro Chain-K | `tetrochaink` |
| Tetro Chain-Y | `tetrochain` |
| Tetrominous | `tetrominous` |
| Tile City | `tilecity` |
| Tontonbeya | `tontonbeya` |
| Water Walk | `waterwalk` |
| Yajilin | `yajilin` |
| Yajisan-Kazusan | `yajikazu` |
| Yajisan-Sokoban | `yajisoko` |
| Yin-Yang | `yinyang` |
</details>

<details>
<summary>Adapter candidates (14)</summary>

The data columns are a 2026-11-14 snapshot of the local sibling
`puzzlekit-dataset` checkout (`f4b71bc9170c`): raw rows in
`puzzlink_crawlers/logs/merged_puzzles.csv` matched by PID, and dataset-text
cases matched by puzzle type, respectively. Zero or `—` means none were
matched in that inventory, not that no examples exist.
Dataset text is not accepted directly by `solve()`; it needs puzzle-specific
conversion and validation. CSV entries may overlap dataset cases and are not
a count of verified solvable puzzles. The pinned cspuz backend tests also
contain sample URLs and expected boards for these candidates; those samples
have not all been checked through PuzzleKit and pzprjs.

| Puzzle | pzpr PID | CSV URLs | Dataset cases |
| --- | --- | ---: | ---: |
| Army Ants | `armyants` | 19 | — |
| Battleship | `battleship` | 1 | 859 |
| Curve Data | `curvedata` | 209 | — |
| Evolmino | `evolmino` | 10 | — |
| Fire Walk | `firewalk` | 3 | — |
| Kouchoku | `kouchoku` | 19 | — |
| Kurarin | `kurarin` | 2 | — |
| Number City | `numcity` | 0 | — |
| Pencils | `pencils` | 176 | — |
| Rail Pool | `railpool` | 42 | — |
| Seiza | `seiza` | 0 | — |
| Slalom | `slalom` | 561 | — |
| The Longest | `longest` | 0 | — |
| Time Bomb | `timebomb` | 0 | — |

</details>

## Development and licensing

Install with `python -m pip install -e '.[dev]'` and run
`python -m pytest -q`. See the [contributor guide](docs/CONTRIBUTING.md)
for the adapter development workflow. The target lists above reflect the
current registry; the [roadmap](docs/ROADMAP.md) is an older planning snapshot.

PuzzleKit is MIT licensed. The bundled cspuz components have their own terms
in [LICENSE-cspuz](LICENSE-cspuz).
