# pzk

TypeScript CLI and library that turns PuzzleKit dataset text into a pzpr URL, and reads those URLs back.

The string after `?` matches pzpr. `puzzle.getURL()` on the same clues produces the same path. The host is chosen when you print the URL:

| `--site` | URL |
| --- | --- |
| `puzzlink` (default) | `https://puzz.link/p?slither/10/10/...` |
| `pzv` | `http://pzv.jp/p.html?slither/10/10/...` |
| `pzplus` | `https://pzplus.tck.mn/p.html?slither/10/10/...` |

`--site pzv` is the host pzpr prints from Node. puzz.link and pzplus take the same path.

The terminal command is `pzk`. The npm package name is `@smilingwayne/pzk`. The unscoped name `pzk` is already registered to an empty package, so it is not the publish name. The package stays local until you publish it.

This package does not import the Python solvers. Python code stays under `src/puzzlekit`.

## Layout

```text
cli/
├── src/
│   ├── cli.ts                 # `pzk` command
│   ├── index.ts               # library API
│   ├── board.ts               # pzpr Board: cell, cross, border, excell
│   ├── url.ts                 # URL shell: host, pid, size, flags, body
│   ├── qnum.ts                # pzpr encode4Cell / decode4Cell
│   ├── dataset.ts             # "<rows> <cols>" text → cell.qnum
│   ├── registry.ts            # type name → codec
│   └── puzzles/slitherlink.ts # first codec
└── test/                      # node:test, golden strings from pzpr
```

Every input is parsed into a `Board` (`cell`, `cross`, `border`, `excell`), the same lists and piece fields pzpr uses. A codec then writes the URL body from that board. A new variety is a `PuzzleCodec` plus one line in `registry.ts`.

## Setup

Requires Node 20 or newer.

```bash
pnpm install
pnpm test
pnpm build
pnpm exec pzk varieties
```

Run these from the puzzlekit repository root, next to `pyproject.toml`. `package.json`, `pnpm-lock.yaml`, and `tsconfig.json` live there. Source stays in `cli/`. `pnpm pzk` runs TypeScript directly; `pnpm exec pzk` uses `cli/dist`.

```bash
pnpm pzk encode --type slitherlink --site pzv puzzle.txt
```

## Commands

```bash
pzk encode --type slitherlink [--site puzzlink|pzv|pzplus] [--full] [file]
pzk decode [url]
pzk varieties
```

`encode` reads a dataset grid. The first line is `rows cols`. `-` is an empty cell. Slitherlink clues are `0`–`4`. `.` is pzpr's dot clue (`qnum = -2`).

```text
2 2
0 -
- 1
```

```bash
printf '2 2\n0 -\n- 1\n' | pnpm pzk encode --type slitherlink --site pzv
# http://pzv.jp/p.html?slither/2/2/ab

pnpm pzk decode 'https://puzz.link/p?slither/2/2/ab'
```

After `pnpm build`, `pnpm exec pzk` runs the same command from `dist/cli.js`. `pnpm link --global` puts `pzk` on your PATH.

`--full` writes the Slitherlink `f` flag: `slither/f/2/2/...`.

`decode` accepts a full URL, a `?slither/...` paste, or a bare `slither/cols/rows/body` path. It prints dataset text.

## Library

```ts
import { decodeToDataset, encodeDataset } from "@smilingwayne/pzk";

const url = encodeDataset("slitherlink", "2 2\n0 -\n- 1\n", { site: "pzv" });
const decoded = decodeToDataset(url);
```

`encode4Cell` / `decode4Cell` are exported for varieties that share the 4-cell body. They follow `pzprjs` `src/variety-common/Encode.js`.

## What is in this slice

Slitherlink only (`slitherlink`, URL id `slither`, alias `slither`). The body is pzpr's 4-cell encoding. Tests compare payloads with `Puzzle.getURL()` from pzprjs, including one 17×17 dataset grid.

Not in this slice: other varieties, Kanpen URLs, pzpr file URLs (`pzprv3`), solutions, or the Python API. Vertex Slitherlink and Sheep-Wolf Slitherlink use different bodies, so they are separate codecs when added.

## Adding a variety

1. Add `src/puzzles/<id>.ts` implementing `PuzzleCodec`.
2. Register it in `src/registry.ts`.
3. Add a test whose expected path comes from pzpr `getURL()`, not from the Python puzz.link codec. The Python number encoder drops trailing empty cells, so it is not the oracle.
