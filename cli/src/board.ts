import { PzkError } from "./errors.js";
import { EMPTY } from "./types.js";

/**
 * One square, vertex, edge, or margin cell.
 *
 * Field names and defaults match pzpr `BoardPiece` in
 * `pzprjs-origin/src/puzzle/Piece.js`. Problem clues live in `ques`, `qdir`,
 * `qnum`–`qnum4`, `qnums`, and `qchar`. Answer ink lives in `qans`, `anum`,
 * and `line`. Display-only fields (`error`, `qinfo`, `trial`) are omitted.
 */
export interface Piece {
  id: number;
  ques: number;
  qdir: number;
  qnum: number;
  qnum2: number;
  qnum3: number;
  qnum4: number;
  qnums: number[];
  qchar: number | string;
  qans: number;
  anum: number;
  line: number;
  qsub: number;
  qcmp: number;
  snum: number;
}

/**
 * Which lists a variety allocates, matching `Board.hasborder` / `hasexcell`.
 * Crosses are always `(cols + 1) * (rows + 1)`, as in pzpr `estimateSize`.
 */
export interface BoardFlags {
  /** 0: no borders. 1: inner edges. 2: inner edges plus the outer frame. */
  hasborder?: 0 | 1 | 2;
  /** 0: none. 1: top band and left band. 2: all four sides. */
  hasexcell?: 0 | 1 | 2;
  /** pzpr `excellRows`, used when `hasexcell` is 1. Default 1. */
  excellRows?: number;
  /** pzpr `excellCols`, used when `hasexcell` is 1. Default 1. */
  excellCols?: number;
  /** pzpr adds one corner when `emptyexcell.ques === 51` (Kakuro). */
  excellCorner?: boolean;
}

/** The structure every input format is parsed into, and every URL is read from. */
export interface Board {
  cols: number;
  rows: number;
  hasborder: 0 | 1 | 2;
  hasexcell: 0 | 1 | 2;
  /** Row-major, `id` 0 is the top-left cell. Length `cols * rows`. */
  cell: Piece[];
  /** Length `(cols + 1) * (rows + 1)`. */
  cross: Piece[];
  border: Piece[];
  excell: Piece[];
}

export function createPiece(id: number): Piece {
  return {
    id,
    ques: 0,
    qdir: 0,
    qnum: EMPTY,
    qnum2: EMPTY,
    qnum3: EMPTY,
    qnum4: EMPTY,
    qnums: [],
    qchar: 0,
    qans: 0,
    anum: EMPTY,
    line: 0,
    qsub: 0,
    qcmp: 0,
    snum: EMPTY,
  };
}

function createPieces(count: number): Piece[] {
  return Array.from({ length: count }, (_, id) => createPiece(id));
}

/** Same counts as pzpr `Board.estimateSize`. */
export function pieceCounts(
  cols: number,
  rows: number,
  flags: BoardFlags = {},
): { cell: number; cross: number; border: number; excell: number } {
  const hasborder = flags.hasborder ?? 0;
  const hasexcell = flags.hasexcell ?? 0;
  let border = 0;
  if (hasborder === 1) {
    border = 2 * cols * rows - (cols + rows);
  } else if (hasborder === 2) {
    border = 2 * cols * rows + (cols + rows);
  }

  let excell = 0;
  if (hasexcell === 1) {
    const exrows = flags.excellRows ?? 1;
    const excols = flags.excellCols ?? 1;
    excell = cols * exrows + rows * excols + (flags.excellCorner ? 1 : 0);
  } else if (hasexcell === 2) {
    excell = 2 * (cols + rows);
  }

  return {
    cell: cols * rows,
    cross: (cols + 1) * (rows + 1),
    border,
    excell,
  };
}

export function createBoard(cols: number, rows: number, flags: BoardFlags = {}): Board {
  const hasborder = flags.hasborder ?? 0;
  const hasexcell = flags.hasexcell ?? 0;
  const counts = pieceCounts(cols, rows, flags);
  return {
    cols,
    rows,
    hasborder,
    hasexcell,
    cell: createPieces(counts.cell),
    cross: createPieces(counts.cross),
    border: createPieces(counts.border),
    excell: createPieces(counts.excell),
  };
}

export function cellQnums(board: Board): number[] {
  return board.cell.map((piece) => piece.qnum);
}

export function setCellQnums(board: Board, qnums: readonly number[]): void {
  if (qnums.length !== board.cell.length) {
    throw new PzkError(
      `Expected ${board.cell.length} cell clues, received ${qnums.length}.`,
    );
  }
  for (let i = 0; i < qnums.length; i++) {
    const piece = board.cell[i];
    const value = qnums[i];
    if (piece && value !== undefined) {
      piece.qnum = value;
    }
  }
}
