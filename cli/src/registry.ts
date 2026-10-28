import { PzkError } from "./errors.js";
import { slitherlink } from "./puzzles/slitherlink.js";
import type { PuzzleCodec } from "./types.js";

const CODECS: readonly PuzzleCodec[] = [slitherlink];

export function listCodecs(): readonly PuzzleCodec[] {
  return CODECS;
}

export function getCodec(name: string): PuzzleCodec {
  const key = name.trim().toLowerCase();
  const found = CODECS.find(
    (codec) =>
      codec.id === key || codec.urlId === key || codec.aliases.includes(key),
  );
  if (!found) {
    const known = CODECS.map((codec) => codec.id).join(", ");
    throw new PzkError(`Unknown puzzle type "${name}". Known types: ${known}.`);
  }
  return found;
}
