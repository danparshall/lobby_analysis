"""FTM API query runner for task #44 (NY sample query, 2026-06-10).

Implements the discipline items from the 20260609 parity-session plan:
- raw response saved to disk BEFORE any parsing (`<seq>_<name>.json`, exact bytes)
- every query appended to `query_log.jsonl`: UTC timestamp, redacted URL,
  HTTP status, byte count
- quota-gate detection: if the response carries the Institute-review gate
  message (or any non-JSON body), the runner prints the body verbatim and
  refuses to continue — capture the wording, don't burn budget.

Usage:
    FTM_KEY=<key> python _run_query.py <seq> <name> 'param=val&param=val'
e.g.:
    FTM_KEY=$FTM_KEY python _run_query.py 01 eid_lookup 'dt=1&s=NY&y=2024&gro=c-t-id&so=u-tot&sod=0&p=0'

The API key is read from the FTM_KEY env var and never written to the log or
the saved filename; the saved raw body is whatever FTM returns (FTM does not
echo the key in responses, per the WI 2026-06-03 specimens).
"""

import json
import os
import sys
import datetime
import urllib.request
import urllib.error

RAW_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(RAW_DIR, "query_log.jsonl")
GATE_PHRASES = ("free api call limit", "institute review", "api call limit")


def run(seq: str, name: str, params: str) -> None:
    key = os.environ.get("FTM_KEY")
    if not key:
        sys.exit("FTM_KEY not set")
    url = f"https://api.followthemoney.org/?{params}&mode=json&APIKey={key}"
    url_redacted = f"https://api.followthemoney.org/?{params}&mode=json&APIKey=<REDACTED>"
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            status = resp.status
            body = resp.read()
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read()
    except Exception as e:  # network-level failure: log it, don't lose the attempt
        status = -1
        body = repr(e).encode()

    out_path = os.path.join(RAW_DIR, f"{seq}_{name}.json")
    with open(out_path, "wb") as f:
        f.write(body)

    entry = {
        "ts_utc": ts,
        "seq": seq,
        "name": name,
        "url": url_redacted,
        "status": status,
        "bytes": len(body),
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(json.dumps(entry, indent=2))

    text = body.decode("utf-8", errors="replace")
    lowered = text.lower()
    if any(p in lowered for p in GATE_PHRASES):
        print("\n*** QUOTA GATE FIRED — verbatim response below; STOP querying ***\n")
        print(text)
        sys.exit(2)
    try:
        parsed = json.loads(text)
        records = parsed.get("records", parsed)
        n = len(records) if isinstance(records, list) else "?"
        print(f"parsed OK; records on page: {n}")
    except json.JSONDecodeError:
        print("\n*** NON-JSON RESPONSE (404-class or integration bug?) — first 500 chars ***\n")
        print(text[:500])
        sys.exit(3)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    run(sys.argv[1], sys.argv[2], sys.argv[3])
