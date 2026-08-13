# lcusd-lunch-calendar

Legacy subscription link, kept alive as a courtesy. It tracks each new month
the pipeline publishes and runs until you decide to end it — see
[Turning it off](#turning-it-off).

```
https://bruff85.github.io/lcusd-lunch-calendar/lunch.ics
```

## What this repo does now

Nothing but copy. Menus are fetched, parsed, and turned into an ICS by
**[`bruff85/graphql-calendar-pipeline`](https://github.com/bruff85/graphql-calendar-pipeline)**;
`mirror_feed.py` copies that repo's published `docs/lunch.ics` here so the old
URL serves the same calendar. The generator that used to live here
(`fetch_menu.py`) is gone — it had drifted behind the pipeline (notably the
0-indexed-month fix and the removal of the month-relabel heuristic) and having
two copies of that logic is how they disagree.

Nothing about tokenization, watermarking, or subscriptions is mirrored — this
link serves one plain feed to everyone. Subscriber-specific feeds are the
backend's job.

## Turning it off

There is deliberately no end date in the code. How long this link needs to stay
up depends on when the agreement is signed, and a hard-coded date would either
cut the club off early or quietly outlive its welcome. Pick whichever of these
matches what you actually mean:

| You want to… | Do this | Reversible? |
|---|---|---|
| Freeze the feed, keep the URL serving the last month it saw | Set a repo variable `RETIRE_AFTER` to an ISO date (`2026-09-01`), or set `RETIRE_AFTER` in `mirror_feed.py` | Yes |
| Stop syncing, no commit needed | Disable the workflow in the Actions tab | Yes |
| Make the link genuinely dead | Delete `docs/lunch.ics`, or turn off GitHub Pages | No |

The first two leave subscribers holding a calendar that stops gaining months —
it stays on their phone and stops changing. Only the third makes the URL 404.
That distinction matters: a frozen feed looks fine to a parent right up until
they notice next month never filled in, so if the intent is "this link is over,"
the third row is the one that says so.

## Running it by hand

```bash
python mirror_feed.py                      # pulls the published Pages feed
SOURCE_URL=file:///path/to/lunch.ics python mirror_feed.py   # or a local copy
```

The workflow (`.github/workflows/monthly.yml`) reads the feed out of a checkout
of the pipeline repo rather than its Pages URL, so there's no publish lag.

## The schedule

It tracks the *pipeline's* rhythm, since that's the only thing that changes
what there is to copy:

- **27th–31st and 1st–15th, daily.** The pipeline is searching for the next
  month and retrying, so a new month can land on any of those days.
- **16th–26th, Mondays only.** The pipeline has found the month and gone quiet
  until the 27th. Nothing new is coming; the weekly pass exists only to catch a
  *correction* to a month already published.

A run with nothing to do prints `nothing left to mirror` and pushes no commit,
so the quiet days cost nothing. Every run logs which months the feed covers,
which is the quickest way to confirm the club's link picked up the new month.

Note for editing those crons: within a *single* cron expression, restricting
both day-of-month and day-of-week ORs them rather than ANDing them. That's why
the weekly pass is its own entry with `*` for day-of-month instead of being
folded into the ranges above.
