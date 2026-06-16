import requests
import smtplib
import os
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ROMANIA_TZ = timezone(timedelta(hours=3))

IMPORTANCE_LABELS = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.investing.com/economic-calendar/",
}


def fetch_high_impact_events():
    url = "https://economic-calendar.investing.com/economic-calendar/Service/getCalendarFilteredData"
    today = datetime.now(ROMANIA_TZ)
    payload = {
        "country[]": "",
        "importance[]": 3,
        "timeZone": 55,
        "timeFilter": "timeRemain",
        "currentTab": "today",
        "submitFilters": 1,
        "limit_from": 0,
        "dateFrom": today.strftime("%Y-%m-%d"),
        "dateTo": today.strftime("%Y-%m-%d"),
    }
    resp = requests.post(url, data=payload, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


def parse_events(data):
    from html.parser import HTMLParser

    class TableParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.events = []
            self.current = {}
            self.in_row = False
            self.col = 0
            self.capture = False
            self.importance = 0

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "tr" and "js-event-item" in attrs.get("class", ""):
                self.in_row = True
                self.current = {}
                self.col = 0
                self.importance = 0
            if self.in_row:
                if tag == "td":
                    self.capture = True
                if tag == "i" and "grayFullBullishIcon" in attrs.get("class", ""):
                    self.importance += 1

        def handle_endtag(self, tag):
            if tag == "tr" and self.in_row:
                self.in_row = False
                if self.importance >= 3:
                    self.events.append(self.current.copy())
            if tag == "td":
                self.capture = False
                self.col += 1

        def handle_data(self, data):
            data = data.strip()
            if self.capture and data:
                if self.col == 0:
                    self.current["time"] = data
                elif self.col == 1:
                    self.current["currency"] = data
                elif self.col == 3:
                    self.current["event"] = data
                elif self.col == 5:
                    self.current["actual"] = data
                elif self.col == 6:
                    self.current["forecast"] = data
                elif self.col == 7:
                    self.current["previous"] = data

    html = data.get("data", "")
    parser = TableParser()
    parser.feed(html)
    return parser.events


def build_email(events, date_str):
    if not events:
        body = (
            f"Bună dimineața! 🌅\n\n"
            f"Nu există știri economice de importanță majoră programate pentru astăzi, {date_str}.\n\n"
            "O zi liniștită pe piețe!\n\n"
            "---\nRaport generat automat de Claude Code."
        )
        return body

    lines = [f"Bună dimineața! 🌅\n", f"Știri economice ⭐⭐⭐ pentru {date_str} (ora României UTC+3):\n"]
    for ev in events:
        time = ev.get("time", "?")
        currency = ev.get("currency", "?")
        event = ev.get("event", "?")
        actual = ev.get("actual", "-")
        forecast = ev.get("forecast", "-")
        previous = ev.get("previous", "-")
        lines.append(f"⏰ {time} | {currency} | {event}")
        lines.append(f"   Actual: {actual} | Prognoză: {forecast} | Anterior: {previous}\n")

    lines.append("---\nRaport generat automat de Claude Code.")
    return "\n".join(lines)


def send_email(subject, body):
    sender = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = "sebastianlup2001@gmail.com"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
    print("Email trimis cu succes.")


def main():
    today = datetime.now(ROMANIA_TZ)
    date_str = today.strftime("%d.%m.%Y")
    subject = f"📊 Știri economice importante - {date_str}"

    try:
        data = fetch_high_impact_events()
        events = parse_events(data)
    except Exception as e:
        body = f"Bună dimineața!\n\nNu s-a putut genera raportul de astăzi ({date_str}).\nEroare: {e}\n\n---\nClaude Code"
        send_email(f"⚠️ Raport indisponibil - {date_str}", body)
        return

    body = build_email(events, date_str)
    send_email(subject, body)


if __name__ == "__main__":
    main()
