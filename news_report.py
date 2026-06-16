import smtplib
import os
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fetcher import fetch_high_impact_events, ROMANIA_TZ


def format_time(time_str):
    if not time_str or time_str.strip() == "":
        return "Toată ziua"
    try:
        dt = datetime.strptime(time_str, "%H:%M")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        dt_ro = dt_utc.astimezone(ROMANIA_TZ)
        return dt_ro.strftime("%H:%M")
    except Exception:
        return time_str


def build_email(events, date_str):
    if not events:
        return (
            f"Bună dimineața! 🌅\n\n"
            f"Nu există știri economice de importanță majoră pentru astăzi, {date_str}.\n\n"
            "O zi liniștită pe piețe!\n\n"
            "---\nRaport generat automat de Claude Code."
        )

    lines = [
        f"Bună dimineața! 🌅\n",
        f"Știri economice ⭐⭐⭐ pentru {date_str} (ora României UTC+3):\n",
    ]

    for ev in sorted(events, key=lambda e: e.get("time", "")):
        time = format_time(ev.get("time", ""))
        country = ev.get("country", "?")
        event = ev.get("event", ev.get("name", "?"))
        actual = ev.get("actual", "-") or "-"
        estimate = ev.get("estimate", "-") or "-"
        previous = ev.get("previous", "-") or "-"

        lines.append(f"⏰ {time} | 🏳️ {country} | {event}")
        lines.append(f"   Actual: {actual} | Prognoză: {estimate} | Anterior: {previous}\n")

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
        events = fetch_high_impact_events()
    except Exception as e:
        body = f"Bună dimineața!\n\nNu s-a putut genera raportul de astăzi ({date_str}).\nEroare: {e}\n\n---\nClaude Code"
        send_email(f"⚠️ Raport indisponibil - {date_str}", body)
        return

    body = build_email(events, date_str)
    send_email(subject, body)
    print(body)


if __name__ == "__main__":
    main()
