import { DOT, EMPTY } from "./types.js";

/**
 * pzpr v3 "4-cell" run encoding (`encode4Cell` / `decode4Cell`).
 *
 * Ported from pzprjs `src/variety-common/Encode.js` (MIT, sabo2).
 * The branches follow that file so a body string matches `puzzle.getURL()`.
 *
 * A value 0–4 may also swallow the next one or two empty cells (`-1`):
 * - `0`–`4`  value, next cell is not empty
 * - `5`–`9`  value 0–4, then one empty
 * - `a`–`e`  value 0–4, then two empties
 * - `g`–`z`  1–20 empties
 * - `.`      qnum -2
 */

export function encode4Cell(qnum: readonly number[]): string {
  let count = 0;
  let cm = "";

  for (let c = 0; c < qnum.length; c++) {
    let pstr = "";
    const qn = qnum[c] ?? EMPTY;

    if (qn >= 0) {
      const next = qnum[c + 1];
      const next2 = qnum[c + 2];
      if (next !== undefined && next !== EMPTY) {
        pstr = qn.toString(16);
      } else if (next2 !== undefined && next2 !== EMPTY) {
        pstr = (5 + qn).toString(16);
        c += 1;
      } else {
        pstr = (10 + qn).toString(16);
        c += 2;
      }
    } else if (qn === DOT) {
      pstr = ".";
    } else {
      count += 1;
    }

    if (count === 0) {
      cm += pstr;
    } else if (pstr || count === 20) {
      cm += (count + 15).toString(36) + pstr;
      count = 0;
    }
  }

  if (count > 0) {
    cm += (count + 15).toString(36);
  }

  return cm;
}

export function decode4Cell(body: string, length: number): number[] {
  const qnum = Array.from({ length }, () => EMPTY);
  let c = 0;

  for (let i = 0; i < body.length; i++) {
    const ca = body.charAt(i);
    if (c < length) {
      if (ca >= "0" && ca <= "4") {
        qnum[c] = Number.parseInt(ca, 16);
      } else if (ca >= "5" && ca <= "9") {
        qnum[c] = Number.parseInt(ca, 16) - 5;
        c += 1;
      } else if (ca >= "a" && ca <= "e") {
        qnum[c] = Number.parseInt(ca, 16) - 10;
        c += 2;
      } else if (ca >= "g" && ca <= "z") {
        c += Number.parseInt(ca, 36) - 16;
      } else if (ca === ".") {
        qnum[c] = DOT;
      }
    }
    c += 1;
    if (c >= length) {
      break;
    }
  }

  return qnum;
}
