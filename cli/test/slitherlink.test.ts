import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

import { decodeToDataset, encodeDataset, payloadOf, reencode } from "../src/index.ts";

const root = fileURLToPath(new URL("../..", import.meta.url));
const cli = fileURLToPath(new URL("../src/cli.ts", import.meta.url));

const GOLDEN: Array<[string, string, string]> = [
  ["1 1\n3\n", "http://pzv.jp/p.html?slither/1/1/d", ""],
  ["1 1\n0\n", "http://pzv.jp/p.html?slither/1/1/a", ""],
  ["1 1\n.\n", "http://pzv.jp/p.html?slither/1/1/./", ""],
  ["1 1\n-\n", "http://pzv.jp/p.html?slither/1/1/g", ""],
  ["2 2\n0 -\n- 1\n", "http://pzv.jp/p.html?slither/2/2/ab", ""],
  ["2 2\n- -\n- -\n", "http://pzv.jp/p.html?slither/2/2/j", ""],
  ["2 2\n1 2\n3 4\n", "http://pzv.jp/p.html?slither/2/2/123e", ""],
  ["3 3\n0 - -\n- - -\n- - 2\n", "http://pzv.jp/p.html?slither/3/3/akc", ""],
  ["1 3\n1 - 0\n", "http://pzv.jp/p.html?slither/3/1/6a", ""],
  ["1 5\n4 - - - -\n", "http://pzv.jp/p.html?slither/5/1/eh", ""],
  ["2 2\n1 -\n- 2\n", "http://pzv.jp/p.html?slither/f/2/2/bc", "full"],
];

test("dataset text matches pzpr Node getURL", () => {
  for (const [text, url, flag] of GOLDEN) {
    const encoded = encodeDataset("slitherlink", text, {
      site: "pzv",
      full: flag === "full",
    });
    assert.equal(encoded, url);
    assert.equal(payloadOf(encodeDataset("slither", text, { site: "puzzlink", full: flag === "full" })), payloadOf(url));
    const decoded = decodeToDataset(url);
    assert.equal(decoded.id, "slitherlink");
    assert.equal(decoded.text, text.endsWith("\n") ? text : `${text}\n`);
    assert.equal(payloadOf(reencode(url)), payloadOf(url));
  }
});

test("a 17x17 dataset grid matches pzpr", () => {
  const text = readFileSync(new URL("./fixtures/slither-17.txt", import.meta.url), "utf8");
  const url = encodeDataset("slitherlink", text, { site: "pzv" });
  assert.equal(
    url,
    "http://pzv.jp/p.html?slither/17/17/i232dcg2chbg1dm73218d72227dg70836711cl1dg33c183bdh17c26172ci203722223cbj1327c23bgcbh2671cl732228270726231677di162112dh22733372821d3272021326671ch232777872723c2ci2d",
  );
  assert.equal(decodeToDataset(url).text, text.endsWith("\n") ? text : `${text}\n`);
});

test("cli encode and decode", () => {
  const encoded = spawnSync(
    process.execPath,
    ["--import", "tsx", cli, "encode", "--type", "slitherlink", "--site", "pzv"],
    { cwd: root, input: "2 2\n0 -\n- 1\n", encoding: "utf8" },
  );
  assert.equal(encoded.status, 0, encoded.stderr);
  assert.equal(encoded.stdout, "http://pzv.jp/p.html?slither/2/2/ab\n");

  const decoded = spawnSync(
    process.execPath,
    ["--import", "tsx", cli, "decode", encoded.stdout.trim()],
    { cwd: root, encoding: "utf8" },
  );
  assert.equal(decoded.status, 0, decoded.stderr);
  assert.equal(decoded.stdout, "2 2\n0 -\n- 1\n");

  const listed = spawnSync(process.execPath, ["--import", "tsx", cli, "varieties"], {
    cwd: root,
    encoding: "utf8",
  });
  assert.equal(listed.status, 0, listed.stderr);
  assert.match(listed.stdout, /slitherlink\turl=slither/);
});
