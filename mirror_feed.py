#!/usr/bin/env python3
"""
Mirror the maintained pipeline's published feed into this repo's docs/lunch.ics.

This legacy repo no longer fetches or parses menus itself. The maintained
pipeline (bruff85/graphql-calendar-pipeline) does the fetching, parsing, and
ICS generation; this script copies its published feed here so the legacy
subscription URL serves the same calendar.

It tracks every month the pipeline publishes, indefinitely — there is no end
date baked in, because how long this link needs to stay up depends on when the
agreement is signed, which is not something a hard-coded date can predict.
See RETIRE_AFTER below for how to end it when that day comes.
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

# ─────────────────────────────────────────────
# HOW TO TURN THIS OFF
# ─────────────────────────────────────────────
# Leave as None and the link keeps tracking new months for as long as the
# workflow runs. To end it, pick whichever matches what you mean:
#
#   1. Freeze the feed where it is, keeping the URL alive and serving the last
#      month it saw:  set RETIRE_AFTER = date(YYYY, M, D)  (or set the
#      RETIRE_AFTER env var / repo variable to an ISO date, no code edit).
#      After that date the script stops writing. Subscribers keep the calendar
#      they have; it just stops gaining months.
#
#   2. Stop syncing but leave today's feed served: disable the workflow in the
#      Actions tab. Same visible result as (1), no commit required.
#
#   3. Make the link genuinely dead: delete docs/lunch.ics, or turn off GitHub
#      Pages for this repo. Subscribers then get a 404 rather than stale food.
#
# (1) and (2) are reversible; (3) is the one that actually ends the link.
_RETIRE_ENV = os.environ.get("RETIRE_AFTER", "").strip()
RETIRE_AFTER = date.fromisoformat(_RETIRE_ENV) if _RETIRE_ENV else None

EVENT_RE = re.compile(r"BEGIN:VEVENT.*?END:VEVENT", re.DOTALL)
DTSTART_RE = re.compile(r"DTSTART[^:]*:(\d{8})")


def fetch_source():
    req = urllib.request.Request(
        SOURCE_URL, headers={"User-Agent": "lcusd-legacy-mirror/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def describe(ics):
    """A one-line summary of what the feed covers, for the run log.

    Worth printing on every run: this is the only place the months actually
    being served are visible without opening the file.
    """
    dates = sorted(DTSTART_RE.findall(ics))
    if not dates:
        return "0 events"
    months = sorted({d[:6] for d in dates})
    span = ", ".join(f"{m[:4]}-{m[4:]}" for m in months)
    return f"{len(dates)} events covering {span}"


def main():
    if RETIRE_AFTER and date.today() > RETIRE_AFTER:
        print(f"Past RETIRE_AFTER ({RETIRE_AFTER}) — this feed is frozen. Nothing to do.")
        return 0

    print(f"Mirroring {SOURCE_URL}")
    ics = fetch_source()

    # Refuse to overwrite a working feed with something that isn't a calendar.
    # A stale-but-valid feed beats a broken one: the failure this guards against
    # is the source 404ing or returning an error page, which would otherwise be
    # copied over the top of a calendar parents are subscribed to.
    if "BEGIN:VCALENDAR" not in ics or "END:VCALENDAR" not in ics:
        print("Source does not look like an ICS file — leaving existing feed untouched.")
        return 1
    if not EVENT_RE.search(ics):
        print("Source has no events — leaving existing feed untouched.")
        return 1

    print(f"Source: {describe(ics)}")

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

    if existing:
        print(f"Updated {OUTPUT} (was: {describe(existing)}).")
    else:
        print(f"Created {OUTPUT}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
