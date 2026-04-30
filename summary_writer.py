"""
Agent 5: Summary Writer
Generates 3 executive summary variants.
"""

import json
from anthropic import Anthropic
from pydantic import BaseModel


class ExecutiveSummary(BaseModel):
    company_name: str
    one_sentence: str
    one_paragraph: str
    one_page: str


def generate_summaries(company_name: str, profile_data: dict, competitors_data: dict, strategic_data: dict, rec_data: dict, client: Anthropic) -> ExecutiveSummary:
    system_prompt = """You are a strategy executive summarizing a competitive analysis report.
Generate three summary variants of increasing length.

Return ONLY valid JSON, no markdown:
{
    "company_name": "string",
    "one_sentence": "string (tweet-length, punchy, strategic)",
    "one_paragraph": "string (5 sentences max, arc: position -> challenge -> opportunity -> recommendation)",
    "one_page": "string (400 words, full executive summary: overview, competitive position, key findings, strategic priorities, conclusion)"
}"""

    top_recs = rec_data.get('recommendations', [])[:3]
    strengths = strategic_data.get('swot', {}).get('strengths', {}).get('items', [])[:2]
    threats = strategic_data.get('swot', {}).get('threats', {}).get('items', [])[:2]
    advantages = strategic_data.get('sustainable_advantages', [])[:2]

    prompt = f"""Summarize this competitive analysis:

COMPANY: {company_name}
INDUSTRY: {profile_data.get('industry')}
MODEL: {profile_data.get('business_model')}
STATUS: {profile_data.get('public_or_private')}
TOP COMPETITORS: {', '.join([c['name'] for c in competitors_data.get('competitors', [])[:3]])}
KEY STRENGTHS: {json.dumps(strengths)}
KEY THREATS: {json.dumps(threats)}
SUSTAINABLE ADVANTAGES: {json.dumps(advantages)}
TOP RECOMMENDATIONS:
{chr(10).join([f"- {r['title']}: {r['rationale']}" for r in top_recs])}"""

    print(f"\n[ Agent 5 ] Writing executive summaries for {company_name}...")

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]

        return ExecutiveSummary(**json.loads(result_text.strip()))
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse summaries: {e}")
        print(f"Raw response: {result_text}")
        raise


def display_summaries(summary: ExecutiveSummary) -> None:
    print(f"\n{'='*60}")
    print(f"EXECUTIVE SUMMARIES: {summary.company_name}")
    print(f"{'='*60}")

    print(f"\n  ONE SENTENCE:")
    print(f"  {summary.one_sentence}")

    print(f"\n  ONE PARAGRAPH:")
    print(f"  {summary.one_paragraph}")

    print(f"\n  ONE PAGE:")
    print(f"{summary.one_page}")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env")
        exit(1)

    client = Anthropic(api_key=api_key)

    with open("output/Anthropic_profile.json", "r") as f:
        profile_data = json.load(f)
    with open("output/Anthropic_competitors.json", "r") as f:
        competitors_data = json.load(f)
    with open("output/Anthropic_strategic_analysis.json", "r") as f:
        strategic_data = json.load(f)
    with open("output/Anthropic_recommendations.json", "r") as f:
        rec_data = json.load(f)

    summary = generate_summaries("Anthropic", profile_data, competitors_data, strategic_data, rec_data, client)
    display_summaries(summary)

    os.makedirs("output", exist_ok=True)
    with open("output/Anthropic_executive_summary.json", "w") as f:
        json.dump(summary.model_dump(), f, indent=2)
    print(f"\nDone. Executive summaries saved to output/Anthropic_executive_summary.json")
