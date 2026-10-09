import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(join(root, "index.html"), "utf8");

test("every in-page link points at an existing id", () => {
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]));
  const anchors = [...html.matchAll(/href="#([^"]+)"/g)].map((match) => match[1]);

  assert.ok(anchors.length > 0, "expected at least one in-page link");
  for (const anchor of anchors) {
    assert.ok(ids.has(anchor), `No element has id="${anchor}" for the link to #${anchor}`);
  }
});

test("local stylesheets exist", () => {
  const stylesheets = [...html.matchAll(/<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"/g)]
    .map((match) => match[1])
    .filter((href) => !/^https?:/.test(href));

  assert.ok(stylesheets.length > 0, "expected a local stylesheet");
  for (const href of stylesheets) {
    assert.ok(existsSync(join(root, href)), `Missing stylesheet ${href}`);
  }
});

test("page has a title and a description", () => {
  assert.match(html, /<title>[^<]+<\/title>/);
  assert.match(html, /<meta\s+name="description"\s+content="[^"]+"/);
});
