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

    python scripts/literature_search.py harvest --out docs/LITERATURE_SEARCH_V1.json
    python scripts/literature_search.py verify docs/PAPER_S2_RELATED_WORK_DRAFT.md \\
        --record docs/LITERATURE_SEARCH_V1.json
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

#: Seconds between requests. Below the rate limits of all three services; the
#: search is run once, so there is nothing to gain by going faster.
REQUEST_INTERVAL_SECONDS = 1.0

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


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def _crossref(query: str) -> tuple[str, list[dict]]:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {
            "query.bibliographic": query,
            "rows": HITS_PER_QUERY,
            "select": (
                "DOI,title,author,issued,container-title,type,"
                "is-referenced-by-count"
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


def harvest(destination: pathlib.Path) -> dict:
    """Execute every registered query and write what came back."""
    results = []
    for search_pass, subsection, source, query in QUERIES:
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
        time.sleep(REQUEST_INTERVAL_SECONDS)

    record = {
        "schema": "cardiosentinel.literature_search/1",
        "generated_by": "scripts/literature_search.py",
        "hits_per_query": HITS_PER_QUERY,
        "query_count": len(QUERIES),
        "results": results,
    }
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
CITATION = re.compile(r"\[((?:doi|arxiv|pmid):[^\]\s]+)\]")


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


def verify(draft: pathlib.Path, record_path: pathlib.Path) -> int:
    """Fail if a draft cites anything the recorded search did not return."""
    record = json.loads(record_path.read_text(encoding="utf-8"))
    harvested = {
        _normalise(hit["identifier"])
        for result in record["results"]
        for hit in result["hits"]
    }
    cited = sorted(set(CITATION.findall(draft.read_text(encoding="utf-8"))))
    unresolved = [key for key in cited if _normalise(key) not in harvested]
    for key in cited:
        print(f"  {'MISS' if key in unresolved else ' ok '}  {key}")
    print(f"\n{len(cited)} citations, {len(unresolved)} unresolved")
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
        default=REPOSITORY_ROOT / "docs" / "LITERATURE_SEARCH_V1.json",
    )

    verify_parser = subparsers.add_parser("verify", help="check a draft's citations")
    verify_parser.add_argument("draft", type=pathlib.Path)
    verify_parser.add_argument(
        "--record",
        type=pathlib.Path,
        default=REPOSITORY_ROOT / "docs" / "LITERATURE_SEARCH_V1.json",
    )

    arguments = parser.parse_args(argv)
    if arguments.command == "harvest":
        record = harvest(arguments.out)
        returned = sum(len(r["hits"]) for r in record["results"])
        failed = sum(1 for r in record["results"] if r["error"])
        print(
            f"\n{record['query_count']} queries, {returned} hits, {failed} failed\n"
            f"payload_sha256 {record['payload_sha256']}\n"
            f"written to {arguments.out}"
        )
        return 0
    return verify(arguments.draft, arguments.record)


if __name__ == "__main__":
    raise SystemExit(main())
