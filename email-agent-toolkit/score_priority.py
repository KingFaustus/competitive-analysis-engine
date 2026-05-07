"""
Priority Scorer Agent
Scores each email 1-10 based on urgency, deadlines, action items, and sender importance.
"""

import json
import anthropic

client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are an email priority scoring assistant. Score each email from 1 to 10.

Use these factors to determine the score:

1. Classification (base score):
   - URGENT: 8-10
   - ACTION-REQUIRED: 5-7
   - ROUTINE: 2-4
   - SPAM: 1

2. Adjust up or down based on:
   - Deadline urgency: "immediately" or "now" = +2, "this week" = +1, no deadline = 0
   - Action item count: 3 or more items = +1
   - Sender importance: manager, client, executive, or C-suite = +1; automated sender = -1

Return a score (integer 1-10) and one concise sentence explaining the main factors."""

SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {
            "type": "integer"
        },
        "explanation": {
            "type": "string"
        }
    },
    "required": ["score", "explanation"],
    "additionalProperties": False
}

BATCH_SCORE_SCHEMA = {
    "type": "object",
    "properties": {
        "results": {"type": "array", "items": SCORE_SCHEMA}
    },
    "required": ["results"],
    "additionalProperties": False
}


def score_priority(email: dict, classification: dict, contact: dict = None, reputation: dict = None) -> dict:
    """
    Score the priority of a classified email.

    Args:
        email:          dict with 'sender', 'subject', 'body'
        classification: dict with 'classification', 'confidence', 'action_items'
        contact:        optional enrichment dict with 'company', 'domain_type', 'title'
        reputation:     optional dict with 'response_rate', 'total_received',
                        'is_frequent', 'is_responsive'

    Returns:
        dict with 'score' (int 1-10) and 'explanation' (str)
    """
    prompt = _build_prompt(email, classification, contact, reputation)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": SCORE_SCHEMA
            }
        },
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)


def _build_prompt(email, classification, contact=None, reputation=None):
    action_text = ""
    if classification["action_items"]:
        lines = "\n".join(f"  - {item}" for item in classification["action_items"])
        action_text = f"\n\nAction items:\n{lines}"

    contact_text = ""
    if contact:
        parts = []
        if contact.get("company"):
            parts.append(f"Company: {contact['company']}")
        if contact.get("title"):
            parts.append(f"Role: {contact['title']}")
        if contact.get("domain_type"):
            parts.append(f"Domain type: {contact['domain_type']}")
        if parts:
            contact_text = "\n\nContact info:\n" + "\n".join(f"  {p}" for p in parts)

    reputation_text = ""
    if reputation and reputation["total_received"] > 0:
        rate_pct = int((reputation["response_rate"] or 0) * 100)
        parts = [
            f"Total received: {reputation['total_received']}",
            f"Response rate: {rate_pct}%",
        ]
        if reputation["is_responsive"]:
            parts.append("(sender you frequently respond to — boost priority)")
        elif reputation["is_frequent"] and not reputation["is_responsive"]:
            parts.append("(frequent sender with low response rate — lower priority)")
        reputation_text = "\n\nSender reputation:\n" + "\n".join(f"  {p}" for p in parts)

    body_snippet = "\n".join(email['body'].splitlines()[:3])
    return (
        f"From: {email['sender']}\n"
        f"Subject: {email['subject']}\n\n"
        f"{body_snippet}\n\n"
        f"Classification: {classification['classification'].upper()}"
        f"{action_text}{contact_text}{reputation_text}"
    )


def score_priorities_batch(items: list) -> list:
    """
    Score up to 5 emails in a single API call.

    Args:
        items: list of (email, classification, contact, reputation) tuples

    Returns:
        list of score dicts in the same order
    """
    parts = []
    for i, (email, classification, contact, reputation) in enumerate(items, 1):
        parts.append(f"--- Email {i} ---\n" + _build_prompt(email, classification, contact, reputation))
    prompt = "\n\n".join(parts) + f"\n\nScore all {len(items)} emails above. Return one result per email, in order."

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=min(100 * len(items), 2048),
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"}
        }],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": BATCH_SCORE_SCHEMA
            }
        },
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text)["results"]
