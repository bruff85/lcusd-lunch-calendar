#!/usr/bin/env python3
"""
Mirror the maintained pipeline's published feed into this repo's docs/lunch.ics.

This legacy repo no longer fetches or parses menus itself. The maintained
pipeline (bruff85/graphql-calendar-pipeline) does the fetching, parsing, and
ICS generation; this script copies its published feed here so the legacy
subscription URL serves the same calendar, with two limits:

  * Events dated Sept 1, 2026 or later are dropped — this link only ever
    carries menus through August 2026.
  * After Sept 1, 2026 the script refuses to run; the feed freezes as-is
    and the workflow schedule ends with it.
"""

import os
import re
import sys
import urllib.request
from datetime import date

SOURCE_URL = os.environ.get(
    "SOURCE_URL",
    "https://bruff85.github.io/graphql-calendar-pipeline/lunch.ics",
)
OUTPUT = "docs/lunch.ics"

# The legacy link is only promised through the end of August 2026.
LAST_MIRROR_DAY = date(2026, 9, 1)   # last day this script will sync at all
EVENT_CUTOFF = "20260901"            # drop events with DTSTART on/after this

EVENT_RE = re.compile(r"BEGIN:VEVENT.*?END:VEVENT\r?\n", re.DOTALL)
DTSTART_RE = re.compile(r"DTSTART[^:]*:(\d{8})")


def fetch_source():
    req = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "lcusd-legacy-mirror/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def drop_future_events(ics):
    def keep_or_drop(match):
        block = match.group(0)
        m = DTSTART_RE.search(block)
        if m and m.group(1) >= EVENT_CUTOFF:
            return ""
        return block

    return EVENT_RE.sub(keep_or_drop, ics)


def main():
    today = date.today()
    if today > LAST_MIRROR_DAY:
        print(f"Past {LAST_MIRROR_DAY} — this legacy feed is frozen. Nothing to do.")
        return 0

    print(f"Mirroring {SOURCE_URL}")
    ics = fetch_source()

    if "BEGIN:VCALENDAR" not in ics or "END:VCALENDAR" not in ics:
        print("Source does not look like an ICS file — leaving existing feed untouched.")
        return 1

    before = len(EVENT_RE.findall(ics))
    ics = drop_future_events(ics)
    after = len(EVENT_RE.findall(ics))
    if before != after:
        print(f"Dropped {before - after} event(s) dated {EVENT_CUTOFF} or later.")
    print(f"Feed carries {after} event(s).")

    existing = ""
    if os.path.exists(OUTPUT):
        # newline="" is load-bearing: the default translates the file's CRLF
        # line endings to LF on read, so the comparison below would never match
        # the CRLF-carrying source and every run would report a change.
        with open(OUTPUT, "r", encoding="utf-8", newline="") as f:
            existing = f.read()

    if existing == ics:
        print("Already up to date — nothing left to mirror.")
        return 0

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        f.write(ics)
    print(f"Updated {OUTPUT}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
