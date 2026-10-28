import {
  cellQnums,
  createBoard,
  setCellQnums,
  type Board,
  type BoardFlags,
} from "../board.js";
import { formatCellGrid, parseCellGrid } from "../dataset.js";
import { PzkError } from "../errors.js";
import { decode4Cell, encode4Cell } from "../qnum.js";
import {
  DOT,
  EMPTY,
  type BodyEncoding,
  type CodecContext,
  type PuzzleCodec,
} from "../types.js";

/** pzpr Slitherlink allocates frame borders and uses them as the loop. */
const SLITHER_FLAGS: BoardFlags = { hasborder: 2 };

function parseCell(token: string): number {
  if (token === "-") {
    return EMPTY;
  }
  if (token === "." || token === "?") {
    return DOT;
  }
  if (/^[0-4]$/.test(token)) {
    return Number(token);
  }
  throw new PzkError(
    `Slitherlink cell "${token}" is not "-" , "." , or a digit 0-4.`,
  );
}

function formatCell(value: number): string {
  if (value === EMPTY) {
    return "-";
  }
  if (value === DOT) {
    return ".";
  }
  return String(value);
}

export const slitherlink: PuzzleCodec = {
  id: "slitherlink",
  urlId: "slither",
  aliases: ["slither"],
  title: "Slitherlink",

  parseDataset(text: string): Board {
    return parseCellGrid(text, parseCell, SLITHER_FLAGS);
  },

  formatDataset(board: Board): string {
    return formatCellGrid(board, formatCell);
  },

  encodeBody(board: Board, context: CodecContext): BodyEncoding {
    const full = context.full === true || context.pflag.includes("f");
    return {
      body: encode4Cell(cellQnums(board)),
      pflag: full ? "f" : "",
    };
  },

  decodeBody(body: string, cols: number, rows: number): Board {
    const board = createBoard(cols, rows, SLITHER_FLAGS);
    setCellQnums(board, decode4Cell(body, rows * cols));
    return board;
  },
};
