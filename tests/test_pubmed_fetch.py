#!/usr/bin/env python3
"""Offline tests for scripts/pubmed_fetch.py: no network, a synthetic XML fixture only.

Written 2026-09-28 with the tool, for agenda item 32. The tool exists so a PubMed retrieval is
reproducible and its query is recorded; the three things pinned here are the three things a
reader of an evidence table depends on:

1. a record is parsed with its PMID (the traceable handle) and its abstract, not just its title;
2. a multi-section abstract (BACKGROUND/METHODS/RESULTS) is joined, not silently dropped to its
   first section -- the failure mode that would make a table quote the wrong half of a paper;
3. an empty id list makes no efetch call at all (an empty query is a result, not a crash).

The network is replaced, never exercised.
"""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pubmed_fetch.py"
spec = importlib.util.spec_from_file_location("pubmed_fetch", SCRIPT)
pf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pf)

FIXTURE_XML = b"""<?xml version="1.0"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID Version="1">12345678</PMID>
      <Article>
        <Journal>
          <JournalIssue>
            <PubDate><Year>2026</Year></PubDate>
          </JournalIssue>
          <Title>Journal of Synthetic Tests</Title>
        </Journal>
        <ArticleTitle>A needle and a nerve walked into a bar.</ArticleTitle>
        <Abstract>
          <AbstractText Label="BACKGROUND">Chronic pain is common.</AbstractText>
          <AbstractText Label="METHODS">We measured heart rate variability.</AbstractText>
          <AbstractText Label="RESULTS">Autonomic tone rose and catastrophizing did not.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author><LastName>Rivera</LastName><Initials>J</Initials></Author>
          <Author><LastName>Okonkwo</LastName><Initials>A</Initials></Author>
        </AuthorList>
      </Article>
      <MeshHeadingList>
        <MeshHeading><DescriptorName>Chronic Pain</DescriptorName></MeshHeading>
      </MeshHeadingList>
    </MedlineCitation>
    <MedlineJournalInfo/>
    <PublicationTypeList>
      <PublicationType>Randomized Controlled Trial</PublicationType>
    </PublicationTypeList>
  </PubmedArticle>
</PubmedArticleSet>
"""


class _StubNet:
    """Replace pf._get with a stub; restore on exit. Records every URL it was asked for."""

    def __init__(self, payloads):
        self.payloads = payloads  # list of (url_substring, bytes)
        self.calls = []

    def __call__(self, url, params):
        self.calls.append((url, params))
        for needle, blob in self.payloads:
            if needle in url:
                return blob
        raise AssertionError(f"unexpected url: {url}")


class ParseTests(unittest.TestCase):
    def test_efetch_parses_pmid_and_joins_all_abstract_sections(self):
        stub = _StubNet([("efetch.fcgi", FIXTURE_XML)])
        saved = pf._get
        pf._get = stub
        try:
            recs = pf.efetch(["12345678"])
        finally:
            pf._get = saved

        self.assertEqual(len(recs), 1)
        r = recs[0]
        self.assertEqual(r["pmid"], "12345678")
        self.assertEqual(r["title"], "A needle and a nerve walked into a bar.")
        self.assertEqual(r["journal"], "Journal of Synthetic Tests")
        self.assertEqual(r["year"], "2026")
        # all three labelled sections present, in order -- not just BACKGROUND
        self.assertIn("Chronic pain is common.", r["abstract"])
        self.assertIn("heart rate variability", r["abstract"])
        self.assertIn("catastrophizing did not", r["abstract"])
        self.assertLess(r["abstract"].index("Chronic pain"), r["abstract"].index("catastrophizing"))
        self.assertIn("Randomized Controlled Trial", r["pubtypes"])
        self.assertEqual(r["authors"], ["Rivera J", "Okonkwo A"])

    def test_esearch_reads_the_idlist(self):
        stub = _StubNet([("esearch.fcgi", json.dumps({"esearchresult": {"idlist": ["1", "2"]}}).encode())])
        saved = pf._get
        pf._get = stub
        try:
            ids = pf.esearch("anything", 10)
        finally:
            pf._get = saved
        self.assertEqual(ids, ["1", "2"])

    def test_empty_query_result_makes_no_efetch_call(self):
        stub = _StubNet([("esearch.fcgi", json.dumps({"esearchresult": {"idlist": []}}).encode())])
        saved = pf._get
        pf._get = stub
        try:
            recs = pf.efetch(pf.esearch("nothing", 10))
        finally:
            pf._get = saved
        self.assertEqual(recs, [])
        # only the esearch call happened; efetch was never invoked
        self.assertEqual(len(stub.calls), 1)
        self.assertIn("esearch.fcgi", stub.calls[0][0])


class EndToEndTests(unittest.TestCase):
    def test_main_writes_json_with_query_and_records(self):
        stub = _StubNet(
            [
                ("esearch.fcgi", json.dumps({"esearchresult": {"idlist": ["12345678"]}}).encode()),
                ("efetch.fcgi", FIXTURE_XML),
            ]
        )
        saved = pf._get
        pf._get = stub
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp.close()
        argv = sys.argv
        sys.argv = ["pubmed_fetch.py", "--query", "chronic pain[tiab]", "--out", tmp.name, "--retmax", "5"]
        try:
            rc = pf.main()
        finally:
            pf._get = saved
            sys.argv = argv
        self.assertEqual(rc, 0)
        with open(tmp.name) as fh:
            payload = json.load(fh)
        self.assertEqual(payload["query"], "chronic pain[tiab]")
        self.assertEqual(payload["count"], 1)
        self.assertTrue(payload["retrieved_utc"].endswith("Z"))
        self.assertEqual(payload["records"][0]["pmid"], "12345678")


if __name__ == "__main__":
    unittest.main(verbosity=2)
