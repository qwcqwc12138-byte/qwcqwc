import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);

  return worker.fetch(
    new Request("https://market-portfolio-lab.example/", {
      headers: { accept: "text/html" },
    }),
    {
      ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) },
    },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the English research site", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>Market Portfolio Lab \| Reproducible Portfolio Research<\/title>/i);
  assert.match(html, /Evidence over/);
  assert.match(html, /Fifteen companies/);
  assert.match(html, /Maximum Sharpe/);
  assert.match(html, /31 daily runs/);
  assert.match(html, /does not provide investment advice/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Your site is taking shape/i);
});

test("keeps the project facts and social preview wired", async () => {
  const [page, layout] = await Promise.all([
    readFile(new URL("../app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../app/layout.tsx", import.meta.url), "utf8"),
    access(new URL("../public/og.png", import.meta.url)),
  ]);

  for (const ticker of ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "JPM", "GS", "BAC", "V", "MA", "COST", "WMT", "PG", "KO", "NKE"]) {
    assert.match(page, new RegExp(`\\b${ticker}\\b`));
  }
  assert.match(page, /13,605/);
  assert.match(page, /Aug 15–Sep 14, 2026/);
  assert.match(layout, /new URL\("\/og\.png", baseUrl\)/);
  assert.doesNotMatch(page + layout, /_sites-preview|codex-preview/);
});
