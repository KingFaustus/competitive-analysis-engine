"""
Agent 4: Recommendation Engine
Generates strategic recommendations based on all previous analysis.
"""

import json
from anthropic import Anthropic
from pydantic import BaseModel


class Recommendation(BaseModel):
    title: str
    rationale: str
    priority: str
    time_horizon: str
    implementation_difficulty: int
    expected_impact: str
    confidence: str


class RecommendationSet(BaseModel):
    company_name: str
    recommendations: list[Recommendation]


def generate_recommendations(company_name: str, profile_data: dict, competitors_data: dict, strategic_data: dict, client: Anthropic) -> RecommendationSet:
    system_prompt = """You are a strategy consultant generating actionable recommendations.
Based on company profile, competitive landscape, and strategic analysis, generate 4 recommendations.

Return ONLY valid JSON, no markdown:
{
    "company_name": "string",
    "recommendations": [
        {
            "title": "string",
            "rationale": "string",
            "priority": "high|medium|low",
            "time_horizon": "short|medium|long",
            "implementation_difficulty": 3,
            "expected_impact": "string",
            "confidence": "high|medium|low"
        }
    ]
}

time_horizon: short = 0-6 months, medium = 6-18 months, long = 18+ months"""

    swot = strategic_data.get('swot', {})
    porters = strategic_data.get('porters', {})

    prompt = f"""Generate strategic recommendations for {company_name}:

Industry: {profile_data.get('industry')}
Business Model: {profile_data.get('business_model')}
Competitive Rivalry Score: {porters.get('competitive_rivalry', {}).get('score', 'N/A')}/5
Threat of Substitutes: {porters.get('threat_of_substitutes', {}).get('score', 'N/A')}/5
Key Weaknesses: {json.dumps(swot.get('weaknesses', {}).get('items', [])[:3])}
Key Opportunities: {json.dumps(swot.get('opportunities', {}).get('items', [])[:3])}
Sustainable Advantages: {json.dumps(strategic_data.get('sustainable_advantages', [])[:3])}
Top Competitors: {', '.join([c['name'] for c in competitors_data.get('competitors', [])[:3]])}"""

    print(f"\n[ Agent 4 ] Generating recommendations for {company_name}...")

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=2500,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]

        return RecommendationSet(**json.loads(result_text.strip()))
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse recommendations: {e}")
        print(f"Raw response: {result_text}")
        raise


def display_recommendations(recs: RecommendationSet) -> None:
    print(f"\n{'='*60}")
    print(f"STRATEGIC RECOMMENDATIONS: {recs.company_name}")
    print(f"{'='*60}")

    horizon_label = {"short": "0-6 months", "medium": "6-18 months", "long": "18+ months"}

    for i, rec in enumerate(recs.recommendations, 1):
        print(f"\n  {i}. {rec.title}")
        print(f"     Priority: {rec.priority.upper()}  |  Timeline: {horizon_label.get(rec.time_horizon, rec.time_horizon)}  |  Difficulty: {rec.implementation_difficulty}/5  |  Confidence: {rec.confidence.upper()}")
        print(f"     Impact:    {rec.expected_impact}")
        print(f"     Rationale: {rec.rationale}")


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

    recs = generate_recommendations("Anthropic", profile_data, competitors_data, strategic_data, client)
    display_recommendations(recs)

    os.makedirs("output", exist_ok=True)
    with open("output/Anthropic_recommendations.json", "w") as f:
        json.dump(recs.model_dump(), f, indent=2)
    print(f"\nDone. Recommendations saved to output/Anthropic_recommendations.json")
