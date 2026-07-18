"""Fetch the public contribution calendar (no token needed) and write
data/contributions.json with raw days plus derived stats.

GitHub serves the calendar as public HTML at
https://github.com/users/<username>/contributions — the same fragment the
profile page uses.

Usage:
    python scripts/fetch_contributions.py                # real data
    python scripts/fetch_contributions.py --placeholder  # deterministic sample
"""

import datetime as dt
import json
import pathlib
import re
import sys

USERNAME = "HasanDroid18"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"


def fetch_days():
    import requests
    from bs4 import BeautifulSoup

    url = f"https://github.com/users/{USERNAME}/contributions"
    resp = requests.get(url, headers={"User-Agent": "profile-art"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tooltips = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for", "")
        m = re.match(r"(\d+|No) contributions?", tip.get_text(strip=True))
        if target and m:
            tooltips[target] = 0 if m.group(1) == "No" else int(m.group(1))

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        date = td.get("data-date")
        if not date:
            continue
        days.append({
            "date": date,
            "level": int(td.get("data-level", 0)),
            "count": tooltips.get(td.get("id", ""), int(td.get("data-level", 0))),
        })
    days.sort(key=lambda d: d["date"])
    if not days:
        raise RuntimeError("no contribution cells parsed — page layout changed?")
    return days


def placeholder_days():
    """Deterministic sample so the SVG can be generated before the workflow's
    first real fetch replaces this data."""
    rnd = 41
    days = []
    today = dt.date.today()
    for i in range(365, -1, -1):
        d = today - dt.timedelta(days=i)
        rnd = (rnd * 1103515245 + 12345) % (1 << 31)
        roll = rnd % 10
        count = 0 if roll < 4 else (roll - 3 if d.weekday() < 5 else roll - 6)
        count = max(count, 0)
        days.append({"date": d.isoformat(), "level": min(count, 4), "count": count})
    return days


def derive_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)
    current = 0
    seq = list(days)
    if seq and seq[-1]["count"] == 0:
        seq.pop()  # today with no contributions yet doesn't break the streak
    for d in reversed(seq):
        if d["count"] > 0:
            current += 1
        else:
            break
    return {
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]},
        "longest_streak": longest,
        "current_streak": current,
    }


def main():
    placeholder = "--placeholder" in sys.argv
    if placeholder:
        days = placeholder_days()
    else:
        days = fetch_days()
    data = {
        "username": USERNAME,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "placeholder": placeholder,
        "stats": derive_stats(days),
        "days": days,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(f"wrote {OUT}: {len(days)} days, {data['stats']['total']} contributions"
          + (" (placeholder)" if placeholder else ""))


if __name__ == "__main__":
    main()
