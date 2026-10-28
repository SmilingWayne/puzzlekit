#!/usr/bin/env node

import { readFileSync } from "node:fs";
import { parseArgs } from "node:util";

import { PzkError } from "./errors.js";
import { decodeToDataset, encodeDataset, listVarieties } from "./index.js";
import { parseSite } from "./url.js";

const HELP = `pzk — puzzlekit pzpr URL codec

Usage:
  pzk encode --type <id> [--site puzzlink|pzv|pzplus] [--full] [file]
  pzk decode [url-or-file]
  pzk varieties

encode reads dataset text (rows cols, then the grid) and prints one URL.
decode reads a pzpr, puzz.link, or pzplus URL and prints dataset text.
Omit the file to read stdin. Default site is puzzlink.
--site pzv prints the host pzpr itself uses in Node (http://pzv.jp/p.html).
The path after "?" is the same on every site.

Supported types: ${listVarieties().map((item) => item.id).join(", ")}
`;

function fail(error: unknown): never {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${message}\n`);
  process.exit(1);
}

function readSource(file: string | undefined): string {
  if (file) {
    return readFileSync(file, "utf8");
  }
  if (process.stdin.isTTY) {
    throw new PzkError("Pass a file, or pipe text on stdin.");
  }
  return readFileSync(0, "utf8");
}

function main(): void {
  const { values, positionals } = parseArgs({
    args: process.argv.slice(2),
    allowPositionals: true,
    options: {
      type: { type: "string", short: "t" },
      site: { type: "string", short: "s" },
      full: { type: "boolean" },
      help: { type: "boolean", short: "h" },
    },
  });

  const command = positionals[0] ?? "";
  if (values.help || command === "" || command === "help") {
    process.stdout.write(HELP);
    return;
  }

  if (command === "varieties") {
    for (const item of listVarieties()) {
      const aliases = item.aliases.length > 0 ? ` aliases=${item.aliases.join(",")}` : "";
      process.stdout.write(`${item.id}\turl=${item.urlId}\t${item.title}${aliases}\n`);
    }
    return;
  }

  if (command === "encode") {
    const type = values.type;
    if (!type) {
      throw new PzkError("encode needs --type. Example: pzk encode --type slitherlink puzzle.txt");
    }
    const text = readSource(positionals[1]);
    const url = encodeDataset(type, text, {
      site: parseSite(values.site),
      full: values.full === true,
    });
    process.stdout.write(`${url}\n`);
    return;
  }

  if (command === "decode") {
    const source = positionals[1];
    const input = source ? readFileOrUrl(source) : readSource(undefined);
    const decoded = decodeToDataset(input.trim());
    process.stdout.write(decoded.text);
    return;
  }

  throw new PzkError(`Unknown command "${command}". Run pzk --help.`);
}

function readFileOrUrl(source: string): string {
  if (source.includes("://") || source.startsWith("?")) {
    return source;
  }
  try {
    return readFileSync(source, "utf8");
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === "ENOENT" && (source.includes("/") || source.includes("?"))) {
      return source;
    }
    throw error;
  }
}

try {
  main();
} catch (error) {
  fail(error);
}
