import type { Board } from "./board.js";

/** No clue. Matches pzpr `qnum === -1`. */
export const EMPTY = -1;

/** Explicit dot / question mark. Matches pzpr `qnum === -2`, URL character `.`. */
export const DOT = -2;

/**
 * Flags that travel with a URL but are not part of the cell body.
 * `pflag` is the raw pzpr flag segment (for example `f` on Slitherlink).
 */
export interface CodecContext {
  pflag: string;
  variant: string | null;
  /** Slitherlink: when true, emit pflag `f` (the "full" URL form). */
  full?: boolean;
}

export interface BodyEncoding {
  body: string;
  pflag: string;
}

/**
 * One puzzle variety. Dataset text and URL bodies both pass through a pzpr `Board`.
 * The URL shell (host, pid, size, flags) lives outside the codec.
 */
export interface PuzzleCodec {
  readonly id: string;
  readonly urlId: string;
  readonly aliases: readonly string[];
  readonly title: string;
  parseDataset(text: string): Board;
  formatDataset(board: Board): string;
  encodeBody(board: Board, context: CodecContext): BodyEncoding;
  decodeBody(body: string, cols: number, rows: number): Board;
}
