import { createBoard, setCellQnums, type Board, type BoardFlags } from "./board.js";
import { PzkError } from "./errors.js";

export function parseCellGrid(
  text: string,
  parseCell: (token: string) => number,
  flags: BoardFlags = {},
): Board {
  const lines = text
    .trim()
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  const header = lines[0]?.split(/\s+/) ?? [];
  if (header.length !== 2) {
    throw new PzkError('Dataset text must start with "<rows> <cols>".');
  }

  const rows = Number(header[0]);
  const cols = Number(header[1]);
  if (!Number.isInteger(rows) || !Number.isInteger(cols) || rows < 1 || cols < 1) {
    throw new PzkError(`Invalid grid size "${lines[0]}".`);
  }

  const body = lines.slice(1);
  if (body.length !== rows) {
    throw new PzkError(`Expected ${rows} grid rows, found ${body.length}.`);
  }

  const qnum: number[] = [];
  for (let r = 0; r < rows; r++) {
    const tokens = body[r]?.split(/\s+/) ?? [];
    if (tokens.length !== cols) {
      throw new PzkError(`Row ${r + 1} has ${tokens.length} cells, expected ${cols}.`);
    }
    for (const token of tokens) {
      qnum.push(parseCell(token));
    }
  }

  const board = createBoard(cols, rows, flags);
  setCellQnums(board, qnum);
  return board;
}

export function formatCellGrid(
  board: Board,
  formatCell: (value: number) => string,
): string {
  const lines = [`${board.rows} ${board.cols}`];
  for (let r = 0; r < board.rows; r++) {
    const row: string[] = [];
    for (let c = 0; c < board.cols; c++) {
      row.push(formatCell(board.cell[r * board.cols + c]?.qnum ?? 0));
    }
    lines.push(row.join(" "));
  }
  return `${lines.join("\n")}\n`;
}
