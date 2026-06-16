import requests
import os
import csv
import io
from datetime import datetime, timezone, timedelta

ROMANIA_TZ = timezone(timedelta(hours=3))


def fetch_high_impact_events():
    today = datetime.now(ROMANIA_TZ).strftime("%Y-%m-%d")
    api_key = os.environ["ALPHAVANTAGE_API_KEY"]
    url = f"https://www.alphavantage.co/query?function=ECONOMIC_CALENDAR&horizon=1month&apikey={api_key}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    reader = csv.DictReader(io.StringIO(resp.text))
    events = []
    for row in reader:
        if row.get("date", "") == today and row.get("importance", "").lower() == "high":
            events.append(row)
    return events
