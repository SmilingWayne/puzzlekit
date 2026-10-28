import assert from "node:assert/strict";
import { test } from "node:test";

import { formatLocation, parseLocation, payloadOf } from "../src/url.ts";

test("v3 payload is host-independent and keeps the pzpr flag and trailing slash", () => {
  const location = {
    urlId: "slither",
    cols: 1,
    rows: 1,
    body: ".",
    pflag: "",
    variant: null,
    mode: "" as const,
  };

  assert.equal(formatLocation(location, "pzv"), "http://pzv.jp/p.html?slither/1/1/./");
  assert.equal(formatLocation(location, "puzzlink"), "https://puzz.link/p?slither/1/1/./");
  assert.equal(
    formatLocation(location, "pzplus"),
    "https://pzplus.tck.mn/p.html?slither/1/1/./",
  );
  assert.equal(payloadOf(formatLocation(location, "puzzlink")), "slither/1/1/./");
});

test("parse accepts puzz.link, pzplus, pzv, and a bare path", () => {
  const expected = {
    urlId: "slither",
    cols: 2,
    rows: 2,
    body: "ab",
    pflag: "",
    variant: null,
    mode: "",
  };
  const inputs = [
    "https://puzz.link/p?slither/2/2/ab",
    "https://pzplus.tck.mn/p.html?slither/2/2/ab",
    "http://pzv.jp/p.html?slither/2/2/ab",
    "?slither/2/2/ab",
    "slither/2/2/ab",
    "slither_play/2/2/ab",
  ];
  for (const input of inputs) {
    const parsed = parseLocation(input);
    assert.equal(parsed.urlId, expected.urlId);
    assert.equal(parsed.cols, expected.cols);
    assert.equal(parsed.rows, expected.rows);
    assert.equal(parsed.body, expected.body);
    assert.equal(parsed.pflag, expected.pflag);
  }
  assert.equal(parseLocation("slither_play/2/2/ab").mode, "player");
  assert.equal(parseLocation("http://pzv.jp/p.html?slither/f/2/2/bc").pflag, "f");
  assert.equal(parseLocation("slither/1/1/./").body, ".");
});
