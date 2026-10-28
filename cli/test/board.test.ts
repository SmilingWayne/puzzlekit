import assert from "node:assert/strict";
import { test } from "node:test";

import { createBoard } from "../src/board.ts";
import { EMPTY } from "../src/types.ts";
import { slitherlink } from "../src/puzzles/slitherlink.ts";

test("board sizes follow pzpr, dataset text fills cell.qnum", () => {
  const samples: Array<[Parameters<typeof createBoard>[2], number, number, number[]]> = [
    [{ hasborder: 2 }, 2, 3, [6, 12, 17, 0]],
    [{ hasborder: 1, hasexcell: 2 }, 4, 5, [20, 30, 31, 18]],
    [{ hasborder: 1, hasexcell: 1, excellCorner: true }, 6, 6, [36, 49, 60, 13]],
    [{}, 5, 5, [25, 36, 0, 0]],
  ];
  for (const [flags, cols, rows, [cells, crosses, borders, excells]] of samples) {
    const board = createBoard(cols, rows, flags);
    assert.deepEqual(
      [board.cell.length, board.cross.length, board.border.length, board.excell.length],
      [cells, crosses, borders, excells],
    );
  }

  const board = slitherlink.parseDataset("2 2\n0 -\n- 1\n");
  assert.deepEqual(board.cell.map((piece) => piece.qnum), [0, EMPTY, EMPTY, 1]);
  assert.equal(board.border.length, 12);
});
