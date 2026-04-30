"""
Agent 2: Competitor Finder
Identifies top 5 competitors given a company profile.
"""

import json
from anthropic import Anthropic
from pydantic import BaseModel


class Competitor(BaseModel):
    name: str
    why_competitor: str
    threat_level: int
    market_overlap: int
    confidence: str


class CompetitorAnalysis(BaseModel):
    company_name: str
    competitors: list[Competitor]


def find_competitors(company_name: str, company_data: dict, client: Anthropic) -> CompetitorAnalysis:
    system_prompt = """You are a competitive intelligence analyst.
Given a company profile, identify its top 5 direct and indirect competitors.

For each competitor assess:
1. Why they are a competitor
2. Threat level (1-5, where 5 is highest threat)
3. Market overlap (1-5, where 5 is highest overlap)
4. Confidence in this assessment (high/medium/low)

Return ONLY valid JSON matching this schema:
{
    "company_name": "string",
    "competitors": [
        {
            "name": "string",
            "why_competitor": "string",
            "threat_level": 1,
            "market_overlap": 1,
            "confidence": "high"
        }
    ]
}"""

    prompt = f"""Analyze competitors for this company:

Company: {company_name}
Industry: {company_data.get('industry', 'N/A')}
Business Model: {company_data.get('business_model', 'N/A')}
Key Products: {', '.join(company_data.get('key_products', []))}

Identify the top 5 competitors."""

    print(f"\n[ Agent 2 ] Identifying competitors for {company_name}...")

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]

        analysis_data = json.loads(result_text.strip())
        return CompetitorAnalysis(**analysis_data)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse competitor analysis: {e}")
        print(f"Raw response: {result_text}")
        raise


def display_competitors(analysis: CompetitorAnalysis) -> None:
    print(f"\n{'='*60}")
    print(f"TOP 5 COMPETITORS: {analysis.company_name}")
    print(f"{'='*60}")

    for i, comp in enumerate(analysis.competitors, 1):
        print(f"\n  {i}. {comp.name}")
        print(f"     Why Competitor:  {comp.why_competitor}")
        print(f"     Threat Level:    {comp.threat_level}/5")
        print(f"     Market Overlap:  {comp.market_overlap}/5")
        print(f"     Confidence:      {comp.confidence.upper()}")


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

    analysis = find_competitors("Anthropic", profile_data, client)
    display_competitors(analysis)

    os.makedirs("output", exist_ok=True)
    with open("output/Anthropic_competitors.json", "w") as f:
        json.dump(analysis.model_dump(), f, indent=2)
    print(f"\nDone. Competitor analysis saved to output/Anthropic_competitors.json")
