import type { Board } from "./board.js";
import { getCodec, listCodecs } from "./registry.js";
import type { CodecContext, PuzzleCodec } from "./types.js";
import {
  formatLocation,
  parseLocation,
  type PzprLocation,
  type SiteId,
} from "./url.js";

export {
  cellQnums,
  createBoard,
  createPiece,
  pieceCounts,
  setCellQnums,
} from "./board.js";
export type { Board, BoardFlags, Piece } from "./board.js";
export { PzkError } from "./errors.js";
export { DOT, EMPTY } from "./types.js";
export type { CodecContext, PuzzleCodec } from "./types.js";
export { decode4Cell, encode4Cell } from "./qnum.js";
export {
  formatLocation,
  parseLocation,
  parseSite,
  payloadOf,
  SITES,
} from "./url.js";
export type { PzprLocation, SiteId } from "./url.js";

export interface EncodeOptions {
  site?: SiteId;
  /** Slitherlink: emit the `f` flag (`slither/f/cols/rows/...`). */
  full?: boolean;
}

export interface DecodedDataset {
  id: string;
  urlId: string;
  text: string;
  location: PzprLocation;
}

export interface VarietyInfo {
  id: string;
  urlId: string;
  title: string;
  aliases: readonly string[];
}

export function listVarieties(): VarietyInfo[] {
  return listCodecs().map((codec) => ({
    id: codec.id,
    urlId: codec.urlId,
    title: codec.title,
    aliases: codec.aliases,
  }));
}

/** Dataset text → pzpr URL. Default host is puzz.link. */
export function encodeDataset(
  type: string,
  text: string,
  options: EncodeOptions = {},
): string {
  const codec = getCodec(type);
  const grid = codec.parseDataset(text);
  return encodeGrid(codec, grid, {
    pflag: "",
    variant: null,
    full: options.full,
  }, options.site ?? "puzzlink");
}

/** pzpr / puzz.link / pzplus URL, or a bare path → dataset text. */
export function decodeToDataset(input: string): DecodedDataset {
  const location = parseLocation(input);
  const codec = getCodec(location.urlId);
  const grid = codec.decodeBody(location.body, location.cols, location.rows);
  return {
    id: codec.id,
    urlId: codec.urlId,
    text: codec.formatDataset(grid),
    location,
  };
}

/**
 * Decode then encode again. The payload matches the input when the codec
 * is a faithful pzpr port. Host follows `site` (default `pzv`).
 */
export function reencode(input: string, site: SiteId = "pzv"): string {
  const location = parseLocation(input);
  const codec = getCodec(location.urlId);
  const grid = codec.decodeBody(location.body, location.cols, location.rows);
  return encodeGrid(
    codec,
    grid,
    { pflag: location.pflag, variant: location.variant },
    site,
    location.mode,
  );
}

function encodeGrid(
  codec: PuzzleCodec,
  board: Board,
  context: CodecContext,
  site: SiteId,
  mode: PzprLocation["mode"] = "",
): string {
  const encoded = codec.encodeBody(board, context);
  return formatLocation(
    {
      urlId: codec.urlId,
      cols: board.cols,
      rows: board.rows,
      body: encoded.body,
      pflag: encoded.pflag,
      variant: context.variant,
      mode,
    },
    site,
  );
}
