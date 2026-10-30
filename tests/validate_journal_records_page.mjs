#!/usr/bin/env node
// Validator for docs/works/journal-records.html.
//
// The page reads four keyless public registers and reports where they disagree. This harness does
// three things, in the order the page itself does them:
//
//   1. OFFLINE — runs the page's own ISSN parser (check digit included) by loading its script with
//      stubs for window/document, so the test exercises the shipped code rather than a copy of it.
//   2. OFFLINE — asserts the page still carries the statements that make it honest: that it refuses
//      to call any journal predatory, that absence from DOAJ is described as normal, and that the
//      hijack limit is stated. A page like this is worse than useless without them.
//   3. LIVE — re-runs the four controls pinned in docs/works/journal-records-sources.json. If the
//      network is unavailable these are reported as SKIPPED, not as passes.
//
// Usage: node tests/validate_journal_records_page.mjs

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, '..');
const pagePath = join(root, 'docs/works/journal-records.html');
const sourcesPath = join(root, 'docs/works/journal-records-sources.json');

const html = readFileSync(pagePath, 'utf8');
const sources = JSON.parse(readFileSync(sourcesPath, 'utf8'));

let pass = 0;
let fail = 0;
let skip = 0;
const failures = [];

function check(name, condition, detail) {
  if (condition) {
    pass += 1;
    console.log(`  ok   ${name}`);
  } else {
    fail += 1;
    failures.push(name + (detail ? ` — ${detail}` : ''));
    console.log(`  FAIL ${name}${detail ? ` — ${detail}` : ''}`);
  }
}
function skipCheck(name, why) {
  skip += 1;
  console.log(`  skip ${name} — ${why}`);
}

console.log('journal-records.html — offline: does the page say the things that make it honest?');

const requiredStatements = [
  ['refuses to call a journal predatory', 'It does not call any journal predatory'],
  ['says a blacklist is not evidence', 'A list nobody stands behind is not evidence'],
  ['calls DOAJ absence normal', 'This is normal and is not a warning'],
  ['names DOAJ as open-access only', 'DOAJ deliberately lists only fully open-access journals'],
  ['states the hijack limit', 'The classic hijack is a website wearing a real journal'],
  ['states that a clean result is not an endorsement', 'A clean result is not an endorsement'],
  ['states the biomedical index scope limit', 'It indexes life sciences only'],
  ['qualifies the OpenAlex DOAJ flag as a mirror', 'not an independent second opinion'],
  ['prints the request it made', 'Every request this search made'],
  ['warns about a false negative from a typo', 'false “not found”']
];
for (const [name, needle] of requiredStatements) {
  check(`the page ${name}`, html.includes(needle), `missing string: ${needle}`);
}

const requiredEndpoints = [
  'https://api.crossref.org/journals/',
  'https://doaj.org/api/search/journals/issn%3A',
  'https://api.openalex.org/sources/issn:',
  'https://www.ebi.ac.uk/europepmc/webservices/rest/search'
];
for (const url of requiredEndpoints) {
  check(`the page calls ${url.slice(8, 34)}…`, html.includes(url));
}

check('the page sends no search to a server of ours', !/action=|method="post"/i.test(html));
check('the page loads no analytics or third-party script', !/<script[^>]+src=/i.test(html));
check('the pinned sources file names this validator', sources.validator === 'tests/validate_journal_records_page.mjs');
check('the pinned sources file records four controls', sources.controls_measured_2026_10_30.length === 4);
check('the pinned sources file records what the page refuses to do', sources.what_the_page_refuses_to_do.length >= 3);

console.log('journal-records.html — offline: the page\'s own ISSN parser');

// Run the page's script with just enough of a browser to let it define itself.
const scriptMatch = /<script>\n([\s\S]*?)\n<\/script>/.exec(html);
check('the page has exactly one inline script', Boolean(scriptMatch) && (html.match(/<script>/g) || []).length === 1);

if (scriptMatch) {
  const stub = () => ({
    value: '', textContent: '', innerHTML: '', disabled: false,
    set onclick(fn) { this._click = fn; }, get onclick() { return this._click; },
    addEventListener() {}, getElementsByTagName() { return []; }
  });
  const fakeWindow = { location: { search: '' } };
  const sandbox = {
    window: fakeWindow,
    document: { getElementById: stub },
    fetch: () => Promise.reject(new Error('no network in the offline parser check')),
    encodeURIComponent, decodeURIComponent, parseInt, String, Number, Promise, Math, console
  };
  const runner = new Function('window', 'document', 'fetch', 'encodeURIComponent', 'decodeURIComponent',
    scriptMatch[1]);
  let exported = null;
  try {
    runner(fakeWindow, sandbox.document, sandbox.fetch, sandbox.encodeURIComponent, sandbox.decodeURIComponent);
    exported = fakeWindow.__journalRecords;
  } catch (err) {
    check('the page script evaluates without a browser', false, String(err && err.message));
  }
  check('the page exports its parser for testing', Boolean(exported && exported.parseIssn));

  if (exported && exported.parseIssn) {
    const cases = [
      ['0028-4793', '0028-4793', true],
      ['00284793', '0028-4793', true],
      [' 1932-6203 ', '1932-6203', true],
      ['1234-575x', '1234-575X', true],   // the X check digit, in lower case as people type it
      ['9999-9994', '9999-9994', true],
      ['0028-479X', '0028-479X', false],
      ['0028-4790', '0028-4790', false],
      ['not-an-issn', null, null],
      ['', null, null]
    ];
    for (const [input, issn, valid] of cases) {
      const got = exported.parseIssn(input);
      if (issn === null) {
        check(`"${input}" is not an ISSN`, got === null);
      } else {
        check(`"${input}" normalises to ${issn}${valid ? ' and passes its check digit' : ' and fails its check digit'}`,
          Boolean(got) && got.issn === issn && got.valid === valid,
          got ? `got ${got.issn} valid=${got.valid}` : 'got null');
      }
    }
    const bad = exported.parseIssn('0028-479X');
    check('the failing case names the character that should have been there', bad && bad.expected === '3', bad ? `expected ${bad.expected}` : 'no parse');
  }
}

console.log('journal-records.html — live: the four pinned controls');

async function json(url) {
  const res = await fetch(url, { headers: { Accept: 'application/json' } });
  let body = null;
  try { body = await res.json(); } catch { body = null; }
  return { status: res.status, body };
}

let networkUp = true;
try {
  await fetch('https://api.crossref.org/journals/0028-4793', { method: 'HEAD' });
} catch {
  networkUp = false;
}

if (!networkUp) {
  for (const name of ['Crossref resolves a subscription journal', 'DOAJ omits it, correctly',
    'PLOS ONE is listed with its APC', 'an unregistered ISSN is a 404']) {
    skipCheck(name, 'no network on this machine');
  }
} else {
  // Control 1a: Crossref resolves NEJM and holds a large DOI corpus.
  try {
    const { status, body } = await json('https://api.crossref.org/journals/0028-4793');
    const total = body && body.message && body.message.counts && body.message.counts['total-dois'];
    check('Crossref resolves a subscription journal', status === 200 && total > 180000, `status ${status}, total-dois ${total}`);
  } catch (err) {
    skipCheck('Crossref resolves a subscription journal', String(err.message));
  }

  // Control 1b: DOAJ returns nothing for it — the zero that must not be read as a warning.
  try {
    const { status, body } = await json('https://doaj.org/api/search/journals/issn%3A0028-4793');
    check('DOAJ omits it, correctly', status === 200 && body && body.total === 0, `status ${status}, total ${body && body.total}`);
  } catch (err) {
    skipCheck('DOAJ omits it, correctly', String(err.message));
  }

  // Control 2: PLOS ONE is listed, with the charge the page displays.
  try {
    const { status, body } = await json('https://doaj.org/api/search/journals/issn%3A1932-6203');
    const rec = body && body.results && body.results[0] && body.results[0].bibjson;
    const apc = rec && rec.apc && rec.apc.max && rec.apc.max[0];
    check('PLOS ONE is listed with its APC', status === 200 && Boolean(rec) &&
      apc && apc.price === 2477 && apc.currency === 'USD',
      `status ${status}, apc ${JSON.stringify(apc)}`);
    check('PLOS ONE record names a licence and a preservation arrangement',
      Boolean(rec) && Array.isArray(rec.license) && rec.license.length > 0 && Boolean(rec.preservation));
  } catch (err) {
    skipCheck('PLOS ONE is listed with its APC', String(err.message));
  }

  // Control 3: an unregistered ISSN is a 404 and not a guess.
  try {
    const { status } = await json('https://api.crossref.org/journals/0000-0000');
    check('an unregistered ISSN is a 404', status === 404, `status ${status}`);
  } catch (err) {
    skipCheck('an unregistered ISSN is a 404', String(err.message));
  }

  // Control 4: the biomedical index answers by ISSN at all.
  try {
    const { status, body } = await json('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=ISSN:%220028-4793%22&format=json&pageSize=1');
    check('the biomedical index answers by ISSN', status === 200 && body && body.hitCount > 80000, `status ${status}, hits ${body && body.hitCount}`);
  } catch (err) {
    skipCheck('the biomedical index answers by ISSN', String(err.message));
  }
}

console.log(`\n${pass} checks passed, ${fail} failed, ${skip} skipped.`);
if (fail > 0) {
  console.log('\nFailures:');
  for (const f of failures) { console.log(`  - ${f}`); }
  process.exit(1);
}
