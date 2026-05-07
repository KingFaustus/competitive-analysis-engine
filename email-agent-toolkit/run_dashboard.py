"""
Dashboard Runner
Processes the Gmail inbox through the full pipeline, saves results to
dashboard_data.json, then launches the Flask web dashboard.

Usage:
    python3 run_dashboard.py
    python3 run_dashboard.py --count 20 --port 8080 --no-browser
"""

import argparse
import collections
import datetime
import json
import os
import threading
import time
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic as _anthropic

from gmail_reader import read_inbox
from classify_emails import classify_email, classify_emails_batch
from score_priority import score_priority, score_priorities_batch
from suggest_responses import suggest_responses
from enrich_contact import enrich_contact
from reputation import get_reputation, record_interaction
from detect_calendar_event import detect_calendar_event, detect_calendar_events_batch
from followup_tracker import get_followup_reminders
from export_csv import export_csv

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard_data.json")
_print_lock = threading.Lock()


class _RateLimiter:
    """Sliding-window rate limiter shared across all threads."""
    def __init__(self, max_per_minute: int):
        self._max = max_per_minute
        self._times: collections.deque = collections.deque()
        self._lock = threading.Lock()

    def acquire(self):
        while True:
            with self._lock:
                now = time.time()
                while self._times and now - self._times[0] > 60:
                    self._times.popleft()
                if len(self._times) < self._max:
                    self._times.append(now)
                    return
                wait = 60.0 - (now - self._times[0]) + 0.1
            time.sleep(wait)


_limiter = _RateLimiter(45)  # stay under the 50 RPM org limit


def _call(fn, *args, **kwargs):
    """Rate-limit then call fn, retrying on transient rate-limit errors."""
    for attempt in range(4):
        _limiter.acquire()
        try:
            return fn(*args, **kwargs)
        except _anthropic.RateLimitError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def _batch_all(items: list, batch_fn, batch_size: int, max_workers: int = 6) -> list:
    """Run batch_fn over items in parallel chunks, preserving order."""
    batches = [(i, items[i:i + batch_size]) for i in range(0, len(items), batch_size)]
    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_call, batch_fn, batch): start for start, batch in batches}
        for future in as_completed(futures):
            start = futures[future]
            for j, result in enumerate(future.result()):
                results[start + j] = result
    return results


def build_dashboard_data(hours: int = 48) -> dict:
    """
    Run the full pipeline and return a JSON-serializable dict ready for the dashboard.

    Args:
        hours: fetch emails from the last N hours (default: 48)

    Returns:
        dict with 'processed_at', 'emails', and 'followup_reminders'
    """
    emails = read_inbox(count=500, query=f"newer_than:{hours}h")
    n = len(emails)
    print(f"Processing {n} emails from the last {hours}h")

    # Step 1: Batch classify (10 per call → ~15 API calls)
    print("  [1/4] Classifying...  ", end="", flush=True)
    classifications = _batch_all(emails, classify_emails_batch, batch_size=5, max_workers=3)
    print("done.")

    # Step 2: Enrich unique senders (cached after first run)
    print("  [2/4] Enriching contacts...  ", end="", flush=True)
    unique_senders = list(dict.fromkeys(e["sender"] for e in emails))
    with ThreadPoolExecutor(max_workers=6) as pool:
        sender_futures = {pool.submit(_call, enrich_contact, s): s for s in unique_senders}
        contact_map = {sender_futures[f]: f.result() for f in as_completed(sender_futures)}
    contacts = [contact_map[e["sender"]] for e in emails]
    reputations = [get_reputation(e["sender"]) for e in emails]
    for email in emails:
        record_interaction(email["sender"])
    print("done.")

    # Step 3: Batch detect calendar events (10 per call → ~15 API calls)
    print("  [3/4] Detecting meetings...  ", end="", flush=True)
    events = _batch_all(emails, detect_calendar_events_batch, batch_size=5, max_workers=3)
    print("done.")

    # Step 4: Batch score priorities (5 per call → ~30 API calls)
    print("  [4/4] Scoring priorities...  ", end="", flush=True)
    score_items = list(zip(emails, classifications, contacts, reputations))
    scores = _batch_all(score_items, score_priorities_batch, batch_size=5, max_workers=2)
    print("done.")

    # Assemble records (suggestions are generated on demand from the dashboard)
    rows, email_records, suggested_subjects = [], [], []
    for i, email in enumerate(emails):
        clf = classifications[i]
        pri = scores[i]
        rows.append((email, clf, pri))
        suggested_subjects.append("")
        email_records.append({
            "sender":               email["sender"],
            "subject":              email["subject"],
            "body":                 email.get("body", ""),
            "date":                 email.get("date", ""),
            "classification":       clf["classification"],
            "confidence":           clf["confidence"],
            "priority_score":       pri["score"],
            "priority_explanation": pri["explanation"],
            "action_items":         clf["action_items"],
            "suggested_subject":    "",
            "suggestions":          [],
            "calendar_event":       events[i],
        })

    rows.sort(key=lambda r: r[2]["score"], reverse=True)
    email_records.sort(key=lambda e: e["priority_score"], reverse=True)

    print("Checking follow-up reminders...")
    reminders = get_followup_reminders()

    # Save CSV log
    csv_path = export_csv(rows, [None] * len(rows), suggested_subjects)
    print(f"CSV saved: {csv_path}")

    return {
        "processed_at":      datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "emails":            email_records,
        "followup_reminders": reminders,
    }


def main():
    parser = argparse.ArgumentParser(description="Process inbox and launch the web dashboard.")
    parser.add_argument("--hours",      type=int,  default=24,    help="Hours of email history to process (default: 24)")
    parser.add_argument("--port",       type=int,  default=5000,  help="Flask port (default: 5000)")
    parser.add_argument("--no-browser", action="store_true",      help="Don't open browser automatically")
    args = parser.parse_args()

    data = build_dashboard_data(hours=args.hours)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    url = f"http://127.0.0.1:{args.port}"
    print(f"\nDashboard ready at {url} (opening browser...)")

    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    from dashboard import app
    app.run(debug=False, port=args.port)


if __name__ == "__main__":
    main()
