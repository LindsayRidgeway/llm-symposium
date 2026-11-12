// Recovered offline Europe PMC guards, 2026-11-12, OpenAI (Tarik).
// Original checks: Desi, public 30ea19fdea6783302baa7a575a5a68c3315b063f,
// test blob 64f42bd67daf77c3006d38dabd6724339dd621e9. These fixtures establish
// parser/model/render behavior, not live registry availability or medical truth.
import fs from 'node:fs';
import assert from 'node:assert/strict';

globalThis.fetch = () => { throw Error('EPMC fixture suite must not call a registry'); };
const file = process.argv[2] || new URL('../docs/works/retraction.html', import.meta.url);
const html = fs.readFileSync(file, 'utf8');
const blocks = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)];
assert.equal(blocks.length, 1, 'expected one inline page script');
const el = () => ({ value:'', textContent:'', innerHTML:'', style:{}, dataset:{},
  addEventListener(){}, querySelectorAll:()=>[], appendChild(){} });
globalThis.document = { getElementById:el, createElement:el, querySelectorAll:()=>[] };
globalThis.location = { search:'' };
const mod = new Function(blocks[0][1] + '\nreturn {epmcSearchUrl,epmcTypes,isRetractedType,buildModel,renderReport};')();
let checks = 0;
const check = (name, condition) => { assert(condition, name); checks++; };
const WAKEFIELD = '10.1016/S0140-6736(97)11096-0';

const epmcUrl = mod.epmcSearchUrl(WAKEFIELD.toLowerCase());
check("the Europe PMC query quotes the DOI inside the index's own query language, and asks for the core record",
  epmcUrl.includes(encodeURIComponent('DOI:"' + WAKEFIELD.toLowerCase() + '"')) &&
  epmcUrl.includes("resultType=core") && epmcUrl.includes("pageSize=1"), epmcUrl);

// the pure reader, on the three shapes Europe PMC actually returns
const epmcFound = mod.epmcTypes({ resultList: { result: [{ id: "9500320", source: "MED",
  pubTypeList: { pubType: ["Retracted Publication", "Journal Article"] } }] } });
check("epmcTypes lifts a found record's type list out of the nested payload",
  epmcFound.found === true && epmcFound.types.join("|") === "Retracted Publication|Journal Article",
  JSON.stringify(epmcFound));
check("a single type delivered as a bare string, not an array, is still read as one",
  mod.epmcTypes({ resultList: { result: [{ pubTypeList: { pubType: "Letter" } }] } }).types.join("|") === "Letter");
check("'the index holds it but typed nothing' is distinct from 'the index holds no record'",
  (() => { const held = mod.epmcTypes({ resultList: { result: [{ id: "1" }] } });
           const none = mod.epmcTypes({ resultList: { result: [] } });
           return held.found === true && held.types.length === 0 && none.found === false; })());
check("a record the index types 'Retracted Publication' is recognised by that exact label",
  mod.isRetractedType(epmcFound.types) === true);
check("an ordinary research article is not mistaken for a retracted-record type",
  mod.isRetractedType(["Journal Article", "Research Support, Non-U.S. Gov't"]) === false);



// The original model/render checks now use explicit synthetic responses. No
// live fixture is called a successful service query.
const epmcModel = epmc => mod.buildModel({ doi:'10.1000/fixture',
  work:{id:'https://openalex.org/W1',display_name:'Fixture',publication_date:'1998-01-01',
    publication_year:1998,is_retracted:false,cited_by_count:5},
  crossref:{},counts:{total:5,after:null,noMention:null,recent:[]},epmc });
const typed = epmcModel(epmcFound);
check('parsed document types and retracted flag reach the model',
  typed.epmc.found && typed.epmc.retracted && typed.epmc.types.join('|') === epmcFound.types.join('|'));
const rendered = mod.renderReport(typed);
check('renderer names Europe PMC and its document type',
  rendered.includes('Europe PMC') && rendered.includes('Retracted Publication'));
check('document type is qualified as a label rather than a study', /none of which is a study/.test(rendered));
check('unreachable index remains explicit', /could not be reached/.test(
  mod.renderReport(epmcModel({found:false,types:[],unreachable:true}))));
check('held but untyped record remains explicit', /publishes no type list/.test(
  mod.renderReport(epmcModel({found:true,types:[]}))));
check('absent record remains explicit', /holds no record for this DOI/.test(
  mod.renderReport(epmcModel({found:false,types:[]}))));
check('publisher document-type labels are HTML escaped',
  mod.renderReport(epmcModel({found:true,types:['<img src=x onerror=alert(1)>']}))
    .includes('&lt;img src=x onerror=alert(1)&gt;'));
check('parser preserves record identity', epmcFound.pmid === '9500320' && epmcFound.index === 'MED');
check('missing response remains absent', mod.epmcTypes(null).found === false && mod.epmcTypes(null).types.length === 0);
console.log(checks + ' EPMC checks passed; no registry requests');
