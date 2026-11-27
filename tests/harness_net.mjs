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
