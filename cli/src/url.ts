import { PzkError } from "./errors.js";

/** Where the same pzpr payload is pasted. The path after `?` does not change. */
export const SITES = {
  puzzlink: "https://puzz.link/p?",
  pzv: "http://pzv.jp/p.html?",
  pzplus: "https://pzplus.tck.mn/p.html?",
} as const;

export type SiteId = keyof typeof SITES;

export interface PzprLocation {
  urlId: string;
  cols: number;
  rows: number;
  body: string;
  pflag: string;
  variant: string | null;
  mode: "" | "player" | "editor";
}

const ALNUM_END = /[a-zA-Z0-9]$/;

export function parseSite(value: string | undefined): SiteId {
  if (value === undefined || value === "") {
    return "puzzlink";
  }
  if (value === "puzzlink" || value === "pzv" || value === "pzplus") {
    return value;
  }
  throw new PzkError(`Unknown site "${value}". Use puzzlink, pzv, or pzplus.`);
}

/**
 * Build a v3 URL. `site: "pzv"` matches pzpr's Node `getURL()` host.
 * Every site shares the payload `urlId[/v:variant][/pflag]/cols/rows/body`.
 */
export function formatLocation(loc: PzprLocation, site: SiteId = "puzzlink"): string {
  const parts: string[] = [];
  if (loc.variant !== null) {
    parts.push(`v:${loc.variant}`);
  }
  if (loc.pflag) {
    parts.push(loc.pflag);
  }
  parts.push(String(loc.cols), String(loc.rows), loc.body);

  let payload = parts.join("/");
  if (!ALNUM_END.test(payload)) {
    payload += "/";
  }

  let urlId = loc.urlId;
  if (loc.mode === "player") {
    urlId += "_play";
  } else if (loc.mode === "editor") {
    urlId += "_edit";
  }

  return SITES[site] + urlId + "/" + payload;
}

/** Accept a full URL, a `?pid/...` paste, or a bare `pid/cols/rows/body` path. */
export function parseLocation(input: string): PzprLocation {
  let raw = input.trim();
  if (!raw) {
    throw new PzkError("URL is empty.");
  }

  const queryAt = raw.indexOf("?");
  if (queryAt >= 0) {
    raw = raw.slice(queryAt + 1);
  }
  raw = raw.replace(/^\/+/, "");

  try {
    raw = decodeURIComponent(raw);
  } catch {
    throw new PzkError("URL query is not valid percent-encoding.");
  }

  let mode: PzprLocation["mode"] = "";
  const typeMatch = /^type=(player|editor)&/i.exec(raw);
  if (typeMatch?.[1]) {
    mode = typeMatch[1].toLowerCase() === "player" ? "player" : "editor";
    raw = raw.slice(typeMatch[0].length);
  }

  const segments = raw.split("/");
  if (segments.length > 0 && segments[segments.length - 1] === "") {
    segments.pop();
  }
  if (segments.length < 3) {
    throw new PzkError(
      `Cannot read a pzpr path from "${input.trim()}". Expected pid/cols/rows/body.`,
    );
  }

  let urlId = segments.shift() ?? "";
  if (/^pzprv/i.test(urlId)) {
    throw new PzkError("pzpr file URLs (pzprv3) are not supported.");
  }
  if (urlId.endsWith("_play")) {
    mode = "player";
    urlId = urlId.slice(0, -"_play".length);
  } else if (urlId.endsWith("_edit")) {
    mode = "editor";
    urlId = urlId.slice(0, -"_edit".length);
  }
  if (!urlId) {
    throw new PzkError("URL is missing a puzzle id.");
  }

  let variant: string | null = null;
  if (segments[0]?.startsWith("v:")) {
    variant = (segments.shift() ?? "").slice(2);
  }

  let pflag = "";
  const head = segments[0];
  if (head !== undefined && Number.isNaN(Number(head))) {
    pflag = segments.shift() ?? "";
  }

  const cols = Number(segments.shift());
  const rows = Number(segments.shift());
  if (!Number.isInteger(cols) || !Number.isInteger(rows) || cols < 1 || rows < 1) {
    throw new PzkError(`Invalid grid size in "${input.trim()}".`);
  }

  return {
    urlId,
    cols,
    rows,
    body: segments.join("/"),
    pflag,
    variant,
    mode,
  };
}

/** The comparable part: everything after `?`, without a trailing slash we added only for `.`. */
export function payloadOf(url: string): string {
  const queryAt = url.indexOf("?");
  return queryAt >= 0 ? url.slice(queryAt + 1) : url;
}
