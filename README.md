# lcusd-lunch-calendar

Legacy subscription link, kept alive as a courtesy through **August 31, 2026**.

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

## The two dates

`mirror_feed.py` has both hard-coded near the top:

- Events dated **Sept 1, 2026 or later are dropped** on the way in. If the
  pipeline publishes September while this link is still syncing, September food
  does not appear here.
- After **Sept 1, 2026** the script exits without writing anything, so the feed
  freezes on the final August sync and stops changing.

Nothing needs to be turned off on that date. If you want the link to truly go
dead rather than serve a stale August, delete `docs/lunch.ics` or disable Pages.

## Running it by hand

```bash
python mirror_feed.py                      # pulls the published Pages feed
SOURCE_URL=file:///path/to/lunch.ics python mirror_feed.py   # or a local copy
```

The workflow (`.github/workflows/monthly.yml`) runs daily at 8:30am PT and
reads the feed out of a checkout of the pipeline repo rather than its Pages
URL, so there's no publish lag.
