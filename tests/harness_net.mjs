// Replay a recorded API response, so a page harness can run at every landing. (Desi, 2026-11-27.)
//
// Seven of the sixteen harnesses in tests/ call a live keyless API. The landing gate executes the
// Python tests; the workflow syntax-checks the .mjs files; so those seven had never run — and the
// pages they guard print "56 checks" to strangers. Requiring the network at every landing is not an
// option: an API having a bad afternoon is not a defect in this repository, and a guard that goes red
// for the weather gets switched off.
//
// So a harness with a hook may run in two modes:
//
//   node tests/validate_trials_page.mjs                 # live, as before
//   HARNESS_REPLAY=tests/fixtures/trials.replay.json node tests/validate_trials_page.mjs
//
// In replay mode the fetch is answered from the recorded file, and the harness must SAY which mode
// it ran in — a replay that quietly reported "live registry answers 200" would be a false claim about
// the world, which is the one thing these harnesses exist to prevent.
//
// What replay does not establish: that the API still answers, or that its shape has not changed. It
// establishes that the page's own code, run against a real recorded response, still passes every
// assertion the record supports. The liveness claims need the live run, which is a deliberate act.
import fs from "node:fs";
import path from "node:path";

// --- install(): replay a whole route table, for a harness that fetches many URLs ----------------
//
// `net()` above answers ONE url from a file a page-side harness knows in advance. A harness that
// exercises a page end to end cannot: the page builds its own queries, so the harness does not know
// them, and a recording keyed by hand would drift the moment the page changed a parameter. So
// `install()` patches globalThis.fetch instead — the page's own code calls it, unchanged.
//
//   HARNESS_RECORD=tests/fixtures/validate_recalls_page.replay.json node tests/validate_recalls_page.mjs
//   HARNESS_REPLAY=tests/fixtures/validate_recalls_page.replay.json node tests/validate_recalls_page.mjs
//
// A URL missing from the record is a LOUD failure, not an empty answer: silently answering nothing
// would let a page that changed its query keep passing against a record of the query it used to make.
export function install() {
  const replay = process.env.HARNESS_REPLAY;
  const record = process.env.HARNESS_RECORD;
  const real = globalThis.fetch;
  const today = new Date().toISOString().slice(0, 10);
  const used = new Set();

  const response = (status, text) => ({
    ok: status >= 200 && status < 300,
    status,
    headers: { get: () => null },
    clone() { return response(status, text); },
    json: async () => JSON.parse(text),
    text: async () => text,
  });

  if (replay) {
    const rec = JSON.parse(fs.readFileSync(replay, "utf8"));
    const routes = rec.responses || (rec.url ? { [rec.url]: { status: rec.status, body: rec.body } } : null);
    if (!routes || !Object.keys(routes).length) {
      throw new Error(`replay file ${replay} records no responses: refusing to run against a half-record`);
    }
    globalThis.fetch = async url => {
      const key = String(url);
      used.add(key);
      const hit = routes[key];
      if (!hit) {
        throw new Error(
          `replay file ${replay} has no response for\n    ${key}\n` +
          `  it records ${Object.keys(routes).length} url(s):\n    ` +
          Object.keys(routes).join("\n    ") +
          `\n  the page now asks something the record does not answer — re-record it, and say why ` +
          `the query changed`);
      }
      return response(hit.status || 200, typeof hit.body === "string" ? hit.body : JSON.stringify(hit.body));
    };
    return {
      mode: "replay",
      label: `recorded ${rec.recorded || "unknown date"}`,
      recorded: rec.recorded || null,
      urls: Object.keys(routes),
      used: () => [...used],
      expect_all_used() {
        const idle = Object.keys(routes).filter(u => !used.has(u));
        if (idle.length) {
          throw new Error(`the record answers ${idle.length} url(s) this run never asked for:\n    ` +
                          idle.join("\n    ") + `\n  the page stopped asking them; re-record`);
        }
      },
    };
  }

  if (record) {
    const out = { recorded: today, responses: {} };
    const flush = () => {
      fs.mkdirSync(path.dirname(path.resolve(record)), { recursive: true });
      fs.writeFileSync(record, JSON.stringify(out, null, 1) + "\n");
    };
    globalThis.fetch = async (url, opts) => {
      const res = await real(url, opts);
      const text = await res.clone().text();
      out.responses[String(url)] = { status: res.status, body: text };
      used.add(String(url));
      flush();                     // after every call: a harness that dies still leaves what it got
      return res;
    };
    return { mode: "record", label: `live, recording ${record}`, urls: [], used: () => [...used], flush };
  }

  return { mode: "live", label: "live", urls: [], used: () => [] };
}


export function net() {
  const path = process.env.HARNESS_REPLAY;
  if (!path) {
    return { live: true, label: "live", fetch: globalThis.fetch };
  }
  const rec = JSON.parse(fs.readFileSync(path, "utf8"));
  if (!rec || typeof rec !== "object" || !("body" in rec)) {
    throw new Error(`replay file ${path} has no "body": refusing to run against a half-record`);
  }
  return {
    live: false,
    label: `recorded ${rec.recorded || "unknown date"}`,
    url: rec.url || null,
    fetch: async () => ({
      ok: (rec.status || 200) >= 200 && (rec.status || 200) < 300,
      status: rec.status || 200,
      json: async () => rec.body,
      text: async () => JSON.stringify(rec.body),
    }),
  };
}

// Record one response for replay:
//   node tests/harness_net.mjs record <url> <outfile>
// The file records its own URL and date, because a fixture that does not say what it is a record of
// is indistinguishable from a hand-written object that happens to satisfy the assertions.
if (process.argv[2] === "record") {
  const [, , , url, out] = process.argv;
  if (!url || !out) {
    console.error("usage: node tests/harness_net.mjs record <url> <outfile>");
    process.exit(2);
  }
  const res = await fetch(url);
  const body = await res.json();
  fs.mkdirSync(new URL(".", new URL("file://" + out)), { recursive: true });
  fs.writeFileSync(out, JSON.stringify({
    url,
    status: res.status,
    recorded: new Date().toISOString().slice(0, 10),
    body,
  }, null, 1) + "\n");
  console.log(`recorded ${url} -> ${out} (HTTP ${res.status})`);
}
