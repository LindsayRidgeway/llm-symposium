// Offline regression of the shipped renderer and the exact guard used by the live harness.
import fs from "node:fs";
import assert from "node:assert/strict";
import { scanVoice } from "./retraction_voice.mjs";
globalThis.fetch = () => { throw new Error("This suite must not call a registry"); };
const html = fs.readFileSync(new URL("../docs/works/retraction.html", import.meta.url), "utf8");
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
assert.equal(blocks.length, 1);
const el = () => ({ value: "", textContent: "", innerHTML: "", style: {}, dataset: {},
  addEventListener() {}, querySelectorAll: () => [], appendChild() {} });
globalThis.document = { getElementById: el, createElement: el, querySelectorAll: () => [] };
globalThis.location = { search: "" };
const page = new Function(blocks[0] + "\nreturn { recentCitationsHtml, renderReport, buildModel };")();
let checks = 0;
const check = (name, fn) => { fn(); checks++; console.log("PASS " + name); };
const citation = (doi, title = "OFICINA SOBRE VACINAS E FAKE NEWS") =>
  page.recentCitationsHtml([{ publication_date: "2026-10-22", display_name: title, doi }]);
check("publisher title with a DOI is quoted", () => assert.deepEqual(scanVoice(citation("10.22289/sg.v7n2a103")), []));
check("publisher title without a DOI is quoted", () => assert.deepEqual(scanVoice(citation(null)), []));
check("plain own accusation still fails", () => assert(scanVoice("The data were fabricated.").includes("fabricat")));
check("linked own accusation still fails", () => assert(scanVoice('The data were <a href="evidence.html">fabricated</a>.').includes("fabricat")));
check("a quoted title cannot hide adjacent own prose", () => assert(scanVoice(citation(null) + "<p>We call this fraud.</p>").includes("fraud")));
check("nested inline markup preserves our own text", () => assert(scanVoice("<b>fab</b>ricated").includes("fabricat")));
check("quoted title markup is escaped", () => {
  const rendered = citation(null, '</span><script>fake</script><span data-publisher-title>');
  assert(rendered.includes("&lt;script&gt;")); assert(!rendered.includes("<script>")); assert.deepEqual(scanVoice(rendered), []);
});
check("an ordinary span is not a quotation", () => assert(scanVoice("<span>fake</span>").includes("fake")));
check("link attributes are not reader-visible accusations", () => assert.deepEqual(scanVoice('<a href="https://example.test/fake">A neutral source</a>'), []));
const modelFor = work => page.buildModel({doi:"10.1000/example",work,
  crossref:{},counts:{total:0,after:null,noMention:null,recent:[]}});
check("a recent publisher venue is quoted with or without a DOI", () => {
  for (const doi of [null,"10.1000/example"]) {
    const rendered=page.recentCitationsHtml([{display_name:"A neutral title",doi,
      primary_location:{source:{display_name:"Journal of Fraud Studies"}}}]);
    assert.deepEqual(scanVoice(rendered),[]);
  }
});
check("the queried paper title is a quotation", () => {
  assert.deepEqual(scanVoice(page.renderReport(modelFor({display_name:"A review of fake news"}))),[]);
});
check("the queried paper venue is a quotation", () => {
  assert.deepEqual(scanVoice(page.renderReport(modelFor({display_name:"A neutral title",
    primary_location:{source:{display_name:"Journal of Misconduct Studies"}}}))),[]);
});
check("publisher venue markup remains escaped and cannot hide adjacent own prose", () => {
  const rendered=page.recentCitationsHtml([{display_name:"A neutral title",doi:null,
    primary_location:{source:{display_name:'</span><script>fake</script>'}}}]);
  assert(!rendered.includes("<script>")); assert(rendered.includes("&lt;script&gt;"));
  assert.deepEqual(scanVoice(rendered),[]);
  assert(scanVoice(rendered+"<p>Our own claim is fabricated.</p>").includes("fabricat"));
});
check("the published title marker remains compatible", () => {
  assert.deepEqual(scanVoice("<span data-publisher-title>fake</span>"),[]);
});
console.log(checks + " offline checks passed; no registry requests");
