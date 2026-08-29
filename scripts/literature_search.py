"""The §2 literature search, run against bibliographic APIs rather than by hand.

`PAPER_OUTLINE_V2.md` §2 says the gap statement must be written *after* the
search and that "inventing a citation would be the same class of error the
programme's entire apparatus exists to prevent." A search conducted by reading
and remembering leaves no artifact, so a reader has to trust that it happened.
This script leaves one.

**Every record in the output came out of an API response, not out of an author.**
The registry below fixes the queries; `harvest` executes them and writes what
came back, with the request URL and the retrieval timestamp beside each hit.
`verify` then checks that every citation key used in a draft resolves to a
harvested record, so a citation that no search returned cannot reach the
manuscript unnoticed.

Three sources, chosen because each has a public API that returns authoritative
metadata for a stable identifier:

* **Crossref** -- DOIs, journal and conference literature.
* **arXiv** -- preprints, which is where §2.3 and §2.5 mostly live.
* **PubMed** -- the clinical half of §2.1 and §2.2, which Crossref indexes but
  does not surface well by topic.

Usage::

    python scripts/literature_search.py harvest --out
    docs/literature/LITERATURE_SEARCH_V1.json
    python scripts/literature_search.py verify \\
        paper/PAPER_S2_RELATED_WORK_DRAFT.md \\
        --record docs/literature/LITERATURE_SEARCH_V1.json
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Crossref asks for a contact address in the User-Agent so it can route load
#: complaints. It is the project's public repository, not a personal address.
CONTACT = "https://github.com/DebalekhaChakraborty/CardioSentinel"
USER_AGENT = f"CardioSentinel-literature-search/1.0 (+{CONTACT})"

#: Seconds between requests. Below the rate limits of Crossref and PubMed; the
#: search is run once, so there is nothing to gain by going faster.
REQUEST_INTERVAL_SECONDS = 1.0

#: **arXiv needs three, and this number was set by being wrong about it.** The
#: first V2 harvest ran every source at one second and came back *"97 queries,
#: 308 hits, 54 failed"* -- every failure an arXiv `HTTP 429`, including all
#: eleven title-pinned confirmatory queries. The record written by that run was
#: green at the exit code and empty where it mattered, which is the failure the
#: module docstring already describes for pass 1. arXiv asks callers for one
#: request every three seconds; this obeys it.
ARXIV_INTERVAL_SECONDS = 3.0

#: A 429 is a request to wait, not a result. Retrying it a few times with a
#: growing pause turns a transient refusal into a hit; **not retrying it writes
#: the refusal into the provenance record as though the literature were absent**,
#: which is a false negative in the same direction as the citation-bracket
#: defect this module also carried.
RETRY_ON_STATUS = frozenset({429, 503})
MAX_RETRIES = 4

#: The registered queries. **This tuple is the search protocol.** Each entry is
#: `(pass, outline subsection, source, query)`.
#:
#: **Pass 1 is recorded unedited, including the part of it that did not work.**
#: Its arXiv queries were written as natural-language phrases against `all:`,
#: which the arXiv API scores loosely; four of the five subsections came back
#: with hits that were on-topic for individual words and unrelated to the
#: subject. The harvest reported *"22 queries, 161 hits, 0 failed"* while
#: returning almost no usable arXiv literature -- a green result measuring
#: reachability rather than coverage, which is the failure class
#: `PAPER_S9_DISCUSSION_DRAFT.md` §9.5 is about. Deleting the pass would have
#: hidden it.
#:
#: **Pass 2 amends only the arXiv syntax**, to field-scoped quoted phrases
#: (`ti:`, `abs:`), and adds two Crossref queries for literatures pass 1 named
#: but did not reach. Crossref and PubMed queries are re-run unchanged so that
#: the whole record comes from one retrieval session.
QUERIES: tuple[tuple[str, str, str, str], ...] = (
    # -- pass 1: as registered ------------------------------------------------
    ("1", "2.1", "crossref", "ischemic ST episode detection long-term ambulatory ECG"),
    ("1", "2.1", "crossref", "ST segment change detection European ST-T Database"),
    (
        "1",
        "2.1",
        "pubmed",
        "transient myocardial ischemia detection ambulatory ECG ST episode",
    ),
    ("1", "2.1", "pubmed", "Long-Term ST Database ST episode annotation"),
    ("1", "2.2", "crossref", "deep learning ambulatory Holter ECG classification"),
    (
        "1",
        "2.2",
        "arxiv",
        "structured state space sequence model time series classification",
    ),
    ("1", "2.2", "arxiv", "self-supervised representation learning electrocardiogram"),
    (
        "1",
        "2.2",
        "pubmed",
        "deep neural network electrocardiogram myocardial ischemia detection",
    ),
    ("1", "2.3", "arxiv", "preregistration machine learning research"),
    ("1", "2.3", "arxiv", "reproducibility checklist machine learning experiments"),
    (
        "1",
        "2.3",
        "arxiv",
        "data leakage machine learning based science reproducibility",
    ),
    ("1", "2.3", "crossref", "blind analysis experimental particle physics bias"),
    ("1", "2.3", "crossref", "registered reports preregistration publication bias"),
    ("1", "2.4", "arxiv", "selective classification risk coverage deep networks"),
    ("1", "2.4", "arxiv", "learning to defer to an expert classification"),
    ("1", "2.4", "arxiv", "calibration of modern neural networks confidence"),
    (
        "1",
        "2.4",
        "pubmed",
        "selective prediction deferral clinical machine learning abstention",
    ),
    ("1", "2.5", "arxiv", "retrieval augmented generation knowledge intensive tasks"),
    ("1", "2.5", "arxiv", "guardrails large language model output validation"),
    (
        "1",
        "2.5",
        "arxiv",
        "attribution faithfulness grounded natural language generation",
    ),
    ("1", "2.5", "arxiv", "hallucination detection evidence grounding generated text"),
    (
        "1",
        "2.5",
        "pubmed",
        "large language model guardrails clinical text generation safety",
    ),
    # -- pass 2: field-scoped arXiv syntax, plus two Crossref additions --------
    ("2", "2.2", "arxiv", 'ti:"structured state spaces"'),
    ("2", "2.2", "arxiv", 'ti:"diagonal state space"'),
    ("2", "2.2", "arxiv", 'abs:"electrocardiogram" AND abs:"self-supervised"'),
    ("2", "2.2", "arxiv", 'ti:"electrocardiogram" AND abs:"deep learning"'),
    ("2", "2.3", "arxiv", 'ti:"leakage" AND abs:"reproducibility"'),
    ("2", "2.3", "arxiv", 'abs:"preregistration" AND abs:"machine learning"'),
    ("2", "2.3", "arxiv", 'abs:"pre-registration" AND abs:"machine learning"'),
    ("2", "2.3", "arxiv", 'ti:"reproducibility" AND abs:"checklist"'),
    (
        "2",
        "2.3",
        "crossref",
        "leakage reproducibility crisis machine learning based science",
    ),
    ("2", "2.4", "arxiv", 'ti:"selective classification"'),
    ("2", "2.4", "arxiv", 'ti:"selective prediction"'),
    ("2", "2.4", "arxiv", 'ti:"calibration of modern neural networks"'),
    ("2", "2.4", "arxiv", 'ti:"conformal prediction" AND abs:"clinical"'),
    ("2", "2.5", "arxiv", 'ti:"retrieval-augmented generation"'),
    ("2", "2.5", "arxiv", 'ti:"guardrails" AND abs:"language model"'),
    ("2", "2.5", "arxiv", 'ti:"measuring attribution"'),
    ("2", "2.5", "arxiv", 'ti:"hallucination" AND ti:"survey"'),
    ("2", "2.5", "arxiv", 'ti:"faithfulness" AND abs:"generation"'),
    (
        "2",
        "2.5",
        "crossref",
        "grounded text generation clinical evidence provenance constraint",
    ),
    # -- pass 3: presence tests for named works -------------------------------
    # A different kind of query, recorded separately because it is a different
    # kind of evidence. Passes 1 and 2 ask what a literature contains; pass 3
    # asks whether a work the authors expected to exist is really there and
    # what its metadata actually says. **A search that only returns what you
    # already knew is not a search**, so these are segregated rather than mixed
    # into the topic queries, and §2 marks which citations came from here.
    (
        "3",
        "2.1",
        "crossref",
        "European ST-T Database evaluation of algorithms ST segment analysis",
    ),
    (
        "3",
        "2.1",
        "crossref",
        "PhysioBank PhysioToolkit PhysioNet components new research resource complex "
        "physiologic signals",
    ),
    (
        "3",
        "2.3",
        "crossref",
        "TRIPOD+AI statement reporting guideline prediction model artificial "
        "intelligence",
    ),
    ("3", "2.3", "arxiv", 'ti:"Model Cards for Model Reporting"'),
    ("3", "2.3", "arxiv", 'ti:"Datasheets for Datasets"'),
    ("3", "2.4", "arxiv", 'ti:"Selective Classification for Deep Neural Networks"'),
    ("3", "2.4", "arxiv", 'ti:"SelectiveNet"'),
    (
        "3",
        "2.4",
        "crossref",
        "On the foundations of noise-free selective classification",
    ),
    ("3", "2.4", "crossref", "On optimum recognition error and reject tradeoff Chow"),
    (
        "3",
        "2.5",
        "arxiv",
        'ti:"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"',
    ),
    ("3", "2.5", "arxiv", 'ti:"NeMo Guardrails"'),
    (
        "3",
        "2.5",
        "arxiv",
        'ti:"Survey of Hallucination in Natural Language Generation"',
    ),
    # Two presence tests that pass 3 above failed to satisfy, retried against a
    # second authority. Both outcomes are reported in LITERATURE_SEARCH_V1.md
    # §4 whichever way they fall: a work that cannot be resolved is not cited.
    (
        "3",
        "2.1",
        "pubmed",
        "European ST-T database standard evaluating systems analysis ST-T changes "
        "ambulatory electrocardiography",
    ),
    (
        "3",
        "2.4",
        "crossref",
        "El-Yaniv Wiener foundations noise-free selective classification journal "
        "machine learning research",
    ),
    # -- pass 4: adversarial queries against the gap statement -----------------
    # §2's gap statement claims no neighbouring literature *ships the machinery*
    # that makes an outcome checkable by a third party who does not trust the
    # authors. Passes 1-3 were written to find each literature. **These are
    # written to break that claim**, by looking for exactly the thing it says
    # does not exist: executable papers, computational provenance, held-out
    # evaluation servers, tamper-evident result binding. A gap statement that
    # was never attacked is an assertion about the authors' reading, not about
    # the literature.
    ("4", "2.3", "arxiv", 'ti:"Nonrepudiable Experimental Results"'),
    ("4", "2.3", "arxiv", 'ti:"executable paper"'),
    (
        "4",
        "2.3",
        "arxiv",
        'abs:"provenance" AND abs:"reproducibility" AND abs:"workflow"',
    ),
    ("4", "2.3", "arxiv", 'abs:"tamper-evident" AND abs:"machine learning"'),
    ("4", "2.3", "arxiv", 'ti:"leaderboard" AND abs:"held-out"'),
    ("4", "2.3", "arxiv", 'ti:"reproducibility" AND abs:"container"'),
    (
        "4",
        "2.3",
        "crossref",
        "executable paper reproducible research compendium computational provenance",
    ),
    (
        "4",
        "2.3",
        "crossref",
        "evaluation server hidden test set benchmark leaderboard adaptive overfitting",
    ),
    (
        "4",
        "2.3",
        "crossref",
        "Code Ocean Whole Tale reproducibility platform computational research",
    ),
    ("4", "2.5", "arxiv", 'abs:"claim" AND abs:"verification" AND ti:"generated text"'),
)

#: Hits to keep per query. Enough to see whether a literature exists and who is
#: in it; not a substitute for reading, which happens afterwards and by hand.
HITS_PER_QUERY = 8


#: **The V2 query set: V1 unchanged, plus the two passes that found what V1
#: missed.** `LITERATURE_SEARCH_V1.json` is evidence of what V1 actually
#: searched and is never edited or back-filled; V2 is a separate record with its
#: own digest. **V1's four passes are reproduced verbatim and keep their numbers**,
#: so a reader can diff the two records by pass; the new work is passes 5 and 6
#: and cannot be mistaken for something V1 searched.
#:
#: **Pass 5 is the falsification search.** V1's gap statement rested on five
#: targeted searches and asserted that no prior system enforced a claim.
#: `CARDIOSENTIN_RELATED_WORK_VERIFICATION_V1.md` §5 ran these queries against
#: that assertion instead of in support of it, and they refuted part of it:
#: `arxiv:2509.06902` already verifies claims in a renderer and fails closed,
#: and `arxiv:2603.10742` already enforces an evaluation boundary at call time.
#: **The queries that cost the paper a claim are registered, not the ones that
#: would have flattered it.**
#:
#: **Pass 6 is confirmatory and title-pinned.** Pass 3 found these works through
#: relevance ranking, which is not reproducible across time -- a rerun next year
#: will rank differently. A `ti:` query for each work fixes its provenance to a
#: deterministic retrieval, so the record still resolves after the ranking has
#: moved. Pass 4 adds no work that pass 3 did not already surface.
QUERIES_V2: tuple[tuple[str, str, str, str], ...] = QUERIES + (
    # -- pass 5: the falsification search -------------------------------------
    ("5", "2.3", "arxiv", 'all:"preregistration" AND all:"machine learning"'),
    ("5", "2.3", "arxiv", 'all:"registered report" AND all:"machine learning"'),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"reusable holdout" OR all:"adaptive data analysis" AND all:"holdout"',
    ),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"leaderboard" AND all:"overfitting" AND all:"competition"',
    ),
    ("5", "2.6", "arxiv", 'all:"proof of learning" OR all:"proof-of-learning"'),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"data leakage" AND all:"prevention" AND all:"machine learning"',
    ),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"fail-closed" OR all:"policy enforcement" AND all:"model selection"',
    ),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"machine-checkable" OR all:"machine checkable" '
        'AND all:"scientific claims"',
    ),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"provenance" AND all:"machine learning pipeline" '
        'AND all:"reproducibility"',
    ),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"ML governance" OR all:"model governance" AND all:"runtime"',
    ),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"runtime enforcement" AND all:"experiment" AND all:"protocol"',
    ),
    ("5", "2.6", "arxiv", 'all:"experiment nonrepudiation" OR all:"nonrepudiable"'),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"scientific workflow" AND all:"provenance" AND all:"reproducibility"',
    ),
    (
        "5",
        "2.6",
        "arxiv",
        'all:"cryptographic" AND all:"provenance" AND all:"machine learning"',
    ),
    ("5", "2.6", "arxiv", 'all:"proof-carrying" AND all:"claims"'),
    (
        "5",
        "2.5",
        "arxiv",
        'all:"agentic" AND all:"validation" AND all:"structured evidence"',
    ),
    # -- pass 5: intelligent physical systems, absent from V1 entirely --------
    (
        "5",
        "2.7",
        "arxiv",
        'all:"wearable" AND all:"physiological monitoring" AND all:"deep learning"',
    ),
    ("5", "2.7", "arxiv", 'all:"edge computing" AND all:"ECG" AND all:"real-time"'),
    (
        "5",
        "2.7",
        "arxiv",
        'all:"streaming" AND all:"physiological signals" '
        'AND all:"continuous monitoring"',
    ),
    (
        "5",
        "2.7",
        "arxiv",
        'all:"cyber-physical system" AND all:"trustworthy" AND all:"autonomous"',
    ),
    (
        "5",
        "2.7",
        "arxiv",
        'all:"large language model" AND all:"sensor data" AND all:"physiological"',
    ),
    # -- pass 6: confirmatory, one per work §2 now cites ----------------------
    ("6", "2.6", "arxiv", 'ti:"Proof-Carrying Numbers"'),
    ("6", "2.6", "arxiv", 'ti:"A Grammar of Machine Learning Workflows"'),
    (
        "6",
        "2.6",
        "arxiv",
        'ti:"Reliable Leaderboard for Machine Learning Competitions"',
    ),
    (
        "6",
        "2.6",
        "arxiv",
        'ti:"Generalization in Adaptive Data Analysis and Holdout Reuse"',
    ),
    ("6", "2.6", "arxiv", 'ti:"Runtime Governance for Agentic AI"'),
    ("6", "2.7", "arxiv", 'ti:"Edge computing in 5G cellular networks"'),
    (
        "6",
        "2.7",
        "arxiv",
        'ti:"A Scoping Review of Deep Learning Methods for Photoplethysmography Data"',
    ),
    ("6", "2.7", "arxiv", 'ti:"Health-LLM"'),
    ("6", "2.7", "arxiv", 'ti:"VitalAgent"'),
    (
        "6",
        "2.7",
        "arxiv",
        'ti:"Building Trust in AI-Driven Decision Making for Cyber-Physical Systems"',
    ),
    (
        "6",
        "2.6",
        "crossref",
        "Operationalising artificial intelligence bills of materials for "
        "verifiable AI provenance and lifecycle assurance",
    ),
)

#: The registered query sets, by name. `harvest --queries v1` reproduces the V1
#: protocol exactly; the default is v2 because v2 is what the manuscript now
#: cites against.
QUERY_SETS = {"v1": QUERIES, "v2": QUERIES_V2}


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in RETRY_ON_STATUS or attempt == MAX_RETRIES - 1:
                raise
            time.sleep(ARXIV_INTERVAL_SECONDS * (attempt + 2))
    raise AssertionError("unreachable")


def _crossref(query: str) -> tuple[str, list[dict]]:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {
            "query.bibliographic": query,
            "rows": HITS_PER_QUERY,
            "select": (
                "DOI,title,author,issued,container-title,type,is-referenced-by-count"
            ),
            "mailto": "cardiosentinel@example.invalid",
        }
    )
    payload = json.loads(_get(url))
    hits = []
    for item in payload["message"]["items"]:
        authors = [
            " ".join(filter(None, (a.get("given"), a.get("family"))))
            for a in item.get("author", [])
        ]
        hits.append(
            {
                "identifier": f"doi:{item['DOI']}",
                "title": (item.get("title") or [""])[0],
                "authors": authors,
                "year": (item.get("issued", {}).get("date-parts") or [[None]])[0][0],
                "venue": (item.get("container-title") or [""])[0],
                "type": item.get("type"),
                "cited_by": item.get("is-referenced-by-count"),
            }
        )
    return url, hits


#: arXiv field prefixes. A query that already names a field is passed through;
#: one that does not is scoped to `all:`, which is what pass 1 did to every
#: query and is why pass 1's arXiv results are what they are.
ARXIV_FIELDS = ("ti:", "abs:", "au:", "cat:", "co:", "jr:", "rn:", "all:")


def _arxiv(query: str) -> tuple[str, list[dict]]:
    scoped = query if query.startswith(ARXIV_FIELDS) else f"all:{query}"
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {
            "search_query": scoped,
            "start": 0,
            "max_results": HITS_PER_QUERY,
            "sortBy": "relevance",
        }
    )
    namespace = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(_get(url))
    hits = []
    for entry in root.findall("a:entry", namespace):
        raw_id = entry.findtext("a:id", default="", namespaces=namespace)
        published = entry.findtext("a:published", default="", namespaces=namespace)
        hits.append(
            {
                "identifier": "arxiv:" + raw_id.rsplit("/abs/", 1)[-1],
                "title": " ".join(
                    entry.findtext("a:title", default="", namespaces=namespace).split()
                ),
                "authors": [
                    a.findtext("a:name", default="", namespaces=namespace)
                    for a in entry.findall("a:author", namespace)
                ],
                "year": int(published[:4]) if published[:4].isdigit() else None,
                "venue": "arXiv",
                "type": "preprint",
                "cited_by": None,
            }
        )
    return url, hits


def _pubmed(query: str) -> tuple[str, list[dict]]:
    search_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
        + urllib.parse.urlencode(
            {"db": "pubmed", "term": query, "retmax": HITS_PER_QUERY, "retmode": "json"}
        )
    )
    identifiers = json.loads(_get(search_url))["esearchresult"]["idlist"]
    if not identifiers:
        return search_url, []
    time.sleep(REQUEST_INTERVAL_SECONDS)
    summary_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
        + urllib.parse.urlencode(
            {"db": "pubmed", "id": ",".join(identifiers), "retmode": "json"}
        )
    )
    payload = json.loads(_get(summary_url))["result"]
    hits = []
    for pmid in identifiers:
        item = payload.get(pmid, {})
        year = item.get("pubdate", "")[:4]
        hits.append(
            {
                "identifier": f"pmid:{pmid}",
                "title": item.get("title", ""),
                "authors": [a.get("name", "") for a in item.get("authors", [])],
                "year": int(year) if year.isdigit() else None,
                "venue": item.get("fulljournalname") or item.get("source", ""),
                "type": "journal-article",
                "cited_by": None,
            }
        )
    return search_url, hits


SOURCES = {"crossref": _crossref, "arxiv": _arxiv, "pubmed": _pubmed}


def harvest(
    destination: pathlib.Path,
    queries: tuple[tuple[str, str, str, str], ...] = QUERIES,
    query_set: str = "v1",
) -> dict:
    """Execute every registered query and write what came back."""
    results = []
    for search_pass, subsection, source, query in queries:
        started = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        try:
            url, hits = SOURCES[source](query)
            error = None
        except (urllib.error.URLError, ET.ParseError, KeyError, ValueError) as exc:
            url, hits, error = "", [], f"{type(exc).__name__}: {exc}"
        print(
            f"  p{search_pass} {subsection:<4} {source:<9} {len(hits):>2} hits  {query}"
            + (f"  [{error}]" if error else ""),
            file=sys.stderr,
        )
        results.append(
            {
                "pass": search_pass,
                "subsection": subsection,
                "source": source,
                "query": query,
                "request_url": url,
                "retrieved_utc": started,
                "error": error,
                "hits": hits,
            }
        )
        time.sleep(
            ARXIV_INTERVAL_SECONDS if source == "arxiv" else REQUEST_INTERVAL_SECONDS
        )

    record = {
        "schema": f"cardiosentinel.literature_search/{1 if query_set == 'v1' else 2}",
        "generated_by": "scripts/literature_search.py",
        "hits_per_query": HITS_PER_QUERY,
        "query_count": len(queries),
        "results": results,
    }
    if query_set != "v1":
        # V2 carries what V1's schema left implicit: when the session ran, which
        # registered query set produced it, and the normalised keys the record
        # resolves. **`supersedes` is a pointer, not a merge.** V1 remains the
        # evidence of what V1 searched, and nothing here is back-filled into it.
        record["query_set"] = query_set
        record["supersedes"] = "docs/literature/LITERATURE_SEARCH_V1.json"
        record["generated_utc"] = _dt.datetime.now(_dt.timezone.utc).isoformat(
            timespec="seconds"
        )
        record["normalised_identifiers"] = sorted(
            {
                _normalise(hit["identifier"])
                for result in results
                for hit in result["hits"]
            }
        )
    body = json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False)
    record["payload_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    destination.write_text(
        json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return record


#: A citation in the draft looks like `[doi:10.1234/x]`, `[arxiv:2101.00001]`
#: or `[pmid:12345678]`. The key *is* the identifier, so a citation cannot be
#: written without one and `verify` can resolve it without a bibliography file
#: in between.
#:
#: **Extraction is two-stage, and the reason is a defect this check had for its
#: whole working life.** The original pattern was a single regex,
#: ``\[((?:doi|arxiv|pmid):[^\]\s]+)\]``, which requires the closing bracket to
#: follow the identifier immediately. A bracket holding more than one key --
#: ``[doi:10.1016/j.patter.2023.100804, arxiv:2207.07048]``, and six others like
#: it in the section -- therefore matched *nothing at all*, and **neither key was
#: checked**. The check reported 71 citations against 77 and called itself clean.
#:
#: That is a false negative in the direction that matters. An invented citation
#: placed second in a shared bracket would have passed a gate whose entire
#: purpose is to make an invented citation impossible. The failure is the one
#: `PAPER_S9_DISCUSSION_DRAFT.md` §9.5 names: a green result measuring the
#: convenient case rather than the case that matters.
#:
#: So brackets are found first, and every key inside one is found independently.
#: `KEY` ends at whitespace or a separator rather than at the bracket, and its
#: identifier part is ``*`` rather than ``+`` on purpose: a scheme written with no
#: identifier (``[doi:]``) is extracted as the malformed key it is, resolves
#: against nothing, and is reported as unresolved. **Malformed input fails
#: closed rather than disappearing.**
BRACKET = re.compile(r"\[([^\[\]]*)\]")
KEY = re.compile(r"(?:doi|arxiv|pmid):[^\s,;]*")

#: Trailing sentence punctuation is presentation, not identity, and is stripped
#: for the same reason the arXiv version suffix is. No identifier in any of the
#: three schemes ends in one of these characters.
#:
#: **The colon is deliberately not in this set.** Stripping it would rewrite the
#: malformed key ``doi:`` into ``doi``, which is a different and more confusing
#: thing to see in a MISS line -- the report would name a scheme that does not
#: exist instead of the empty citation the author actually wrote.
_TRAILING = ".,;"


def citation_keys(text: str) -> list[str]:
    """Every citation key in `text`, in order, including repeats.

    Newlines are collapsed first because the manuscript wraps prose at 79
    columns and a shared bracket can straddle a line break.
    """
    flat = re.sub(r"\s+", " ", text)
    return [
        key.rstrip(_TRAILING)
        for inner in BRACKET.findall(flat)
        for key in KEY.findall(inner)
    ]


#: arXiv returns version-qualified identifiers (`arxiv:2005.11401v4`); a
#: manuscript cites the work (`arxiv:2005.11401`). The version suffix is
#: presentation, not identity, so it is normalised away on both sides.
#:
#: **This was found the way §5.6's fourth finding was found.** The first run of
#: `verify` reported 38 of 61 citations unresolved, every one of them an arXiv
#: key whose only difference from a harvested record was a trailing `v4`. The
#: check was comparing surface forms and reporting the difference as a
#: provenance failure. **The fix is here and not in the draft**: the citations
#: were correct, and rewriting them to carry version suffixes would have been
#: the same governance failure as rewording prose until a claim guard is quiet.
ARXIV_VERSION = re.compile(r"^(arxiv:.+?)v\d+$")


def _normalise(identifier: str) -> str:
    identifier = identifier.strip().lower()
    match = ARXIV_VERSION.match(identifier)
    return match.group(1) if match else identifier


def verify(draft: pathlib.Path, *record_paths: pathlib.Path) -> int:
    """Fail if a draft cites anything no recorded search returned.

    **More than one record may be supplied, and for this project that is the
    normal case rather than a convenience.** A re-harvest is not idempotent:
    Crossref, arXiv and PubMed rank by relevance, and relevance moves. Running
    the V2 set on 2026-08-28 returned 509 hits, but four of V1's own pass-2
    arXiv queries were refused with `429` and four PubMed queries came back with
    a different top eight than they did on 2026-08-25 -- so ten works that V1
    demonstrably returned are absent from V2 through no fault of the draft.

    The alternative to a union would be to re-run V1's queries until they
    reproduce, or to paste the missing hits into V2. **Both are back-filling.**
    A citation is legitimate if *some* registered harvest returned it and that
    harvest is on disk with its digest intact, so the check is the union and
    each record stays exactly as its retrieval session left it.
    """
    harvested: set[str] = set()
    for record_path in record_paths:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        harvested |= {
            _normalise(hit["identifier"])
            for result in record["results"]
            for hit in result["hits"]
        }
    occurrences = citation_keys(draft.read_text(encoding="utf-8"))
    cited = sorted(set(occurrences))
    unresolved = [key for key in cited if _normalise(key) not in harvested]
    for key in cited:
        print(f"  {'MISS' if key in unresolved else ' ok '}  {key}")
    works = {_normalise(key) for key in cited}
    print(
        f"\n{len(occurrences)} citation keys found, "
        f"{len(cited)} unique keys, "
        f"{len(works)} unique bibliographic works, "
        f"{len(unresolved)} unresolved"
    )
    if unresolved:
        print(
            "\nUnresolved citations are not necessarily invented -- a source read "
            "outside\nthe registered queries is legitimate -- but each one must be "
            "justified in\nthe search record before it reaches the manuscript.",
        )
    return 1 if unresolved else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    harvest_parser = subparsers.add_parser("harvest", help="run the registered queries")
    harvest_parser.add_argument(
        "--out",
        type=pathlib.Path,
        default=REPOSITORY_ROOT / "docs" / "literature" / "LITERATURE_SEARCH_V2.json",
    )
    harvest_parser.add_argument(
        "--queries",
        choices=sorted(QUERY_SETS),
        default="v2",
        help="which registered query set to execute (default: v2)",
    )

    verify_parser = subparsers.add_parser("verify", help="check a draft's citations")
    verify_parser.add_argument("draft", type=pathlib.Path)
    verify_parser.add_argument(
        "--record",
        type=pathlib.Path,
        action="append",
        dest="records",
        help=(
            "a harvest record to resolve citations against; repeatable, and "
            "resolution is the union (default: V1 and V2)"
        ),
    )

    arguments = parser.parse_args(argv)
    if arguments.command == "harvest":
        record = harvest(
            arguments.out,
            QUERY_SETS[arguments.queries],
            arguments.queries,
        )
        returned = sum(len(r["hits"]) for r in record["results"])
        failed = sum(1 for r in record["results"] if r["error"])
        print(
            f"\n{record['query_count']} queries, {returned} hits, {failed} failed\n"
            f"payload_sha256 {record['payload_sha256']}\n"
            f"written to {arguments.out}"
        )
        return 0
    records = arguments.records or [
        REPOSITORY_ROOT / "docs" / "literature" / "LITERATURE_SEARCH_V1.json",
        REPOSITORY_ROOT / "docs" / "literature" / "LITERATURE_SEARCH_V2.json",
    ]
    return verify(arguments.draft, *records)


if __name__ == "__main__":
    raise SystemExit(main())
