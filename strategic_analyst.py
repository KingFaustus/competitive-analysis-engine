"""
Agent 3: Strategic Analyst
Generates Porter's Five Forces, Boundaries of the Firm, and SWOT analysis with confidence flags.
"""

import json
from anthropic import Anthropic
from pydantic import BaseModel


class Force(BaseModel):
    name: str
    score: int
    explanation: str
    confidence: str


class PortersAnalysis(BaseModel):
    threat_of_new_entrants: Force
    bargaining_power_of_suppliers: Force
    bargaining_power_of_buyers: Force
    threat_of_substitutes: Force
    competitive_rivalry: Force


class BoundariesAnalysis(BaseModel):
    vertical_integration: str
    make_vs_buy: str
    core_vs_context: str
    outsourcing_risks: str
    expansion_opportunities: str
    confidence: str


class SWOTCategory(BaseModel):
    items: list[str]
    confidence: str


class SWOTAnalysis(BaseModel):
    strengths: SWOTCategory
    weaknesses: SWOTCategory
    opportunities: SWOTCategory
    threats: SWOTCategory


class StrategicAnalysis(BaseModel):
    company_name: str
    porters: PortersAnalysis
    boundaries: BoundariesAnalysis
    swot: SWOTAnalysis
    competitive_advantages: list[str]
    sustainable_advantages: list[str]


def analyze_strategy(company_name: str, company_data: dict, competitors_data: dict, client: Anthropic) -> StrategicAnalysis:
    system_prompt = """You are a strategic business analyst trained in MBA-level frameworks.
Given company and competitor data, perform three analyses:
1. Porter's Five Forces (score each 1-5, where 5 = highest threat/intensity)
2. Boundaries of the Firm (vertical integration, make vs buy, core vs context, outsourcing risks, expansion opportunities)
3. SWOT analysis

Return ONLY valid JSON, no markdown:
{
    "company_name": "string",
    "porters": {
        "threat_of_new_entrants": {"name": "Threat of New Entrants", "score": 3, "explanation": "string", "confidence": "high"},
        "bargaining_power_of_suppliers": {"name": "Bargaining Power of Suppliers", "score": 2, "explanation": "string", "confidence": "high"},
        "bargaining_power_of_buyers": {"name": "Bargaining Power of Buyers", "score": 3, "explanation": "string", "confidence": "high"},
        "threat_of_substitutes": {"name": "Threat of Substitutes", "score": 4, "explanation": "string", "confidence": "medium"},
        "competitive_rivalry": {"name": "Competitive Rivalry", "score": 5, "explanation": "string", "confidence": "high"}
    },
    "boundaries": {
        "vertical_integration": "string — assess how much of the value chain the company controls",
        "make_vs_buy": "string — where does it build internally vs partner vs outsource, and why",
        "core_vs_context": "string — which activities are core to competitive advantage vs commodity overhead",
        "outsourcing_risks": "string — what strategic vulnerabilities exist from current dependencies",
        "expansion_opportunities": "string — where should the firm extend its boundaries for strategic gain",
        "confidence": "high|medium|low"
    },
    "swot": {
        "strengths": {"items": ["string"], "confidence": "high"},
        "weaknesses": {"items": ["string"], "confidence": "medium"},
        "opportunities": {"items": ["string"], "confidence": "medium"},
        "threats": {"items": ["string"], "confidence": "high"}
    },
    "competitive_advantages": ["string"],
    "sustainable_advantages": ["string"]
}"""

    prompt = f"""Analyze strategically:

Company: {company_name}
Industry: {company_data.get('industry')}
Business Model: {company_data.get('business_model')}
Products: {', '.join(company_data.get('key_products', []))}
Competitors: {', '.join([c['name'] for c in competitors_data.get('competitors', [])])}

Perform Porter's Five Forces, Boundaries of the Firm, and SWOT analysis."""

    print(f"\n[ Agent 3 ] Running strategic analysis for {company_name}...")

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=4000,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}]
    )

    result_text = response.content[0].text

    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]

        return StrategicAnalysis(**json.loads(result_text.strip()))
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse strategic analysis: {e}")
        print(f"Raw response: {result_text}")
        raise


def display_strategic_analysis(analysis: StrategicAnalysis) -> None:

    # Porter's Five Forces
    print(f"\n{'='*60}")
    print(f"PORTER'S FIVE FORCES: {analysis.company_name}")
    print(f"{'='*60}")

    forces = [
        ("Threat of New Entrants", analysis.porters.threat_of_new_entrants),
        ("Bargaining Power of Suppliers", analysis.porters.bargaining_power_of_suppliers),
        ("Bargaining Power of Buyers", analysis.porters.bargaining_power_of_buyers),
        ("Threat of Substitutes", analysis.porters.threat_of_substitutes),
        ("Competitive Rivalry", analysis.porters.competitive_rivalry),
    ]

    for name, force in forces:
        bar = "[" + "|" * force.score + " " * (5 - force.score) + "]"
        print(f"\n  {name}: {bar} {force.score}/5  [{force.confidence.upper()}]")
        print(f"  {force.explanation}")

    # Boundaries of the Firm
    print(f"\n{'='*60}")
    print(f"BOUNDARIES OF THE FIRM: {analysis.company_name}")
    print(f"{'='*60}")

    b = analysis.boundaries
    print(f"\n  Vertical Integration:")
    print(f"  {b.vertical_integration}")
    print(f"\n  Make vs. Buy:")
    print(f"  {b.make_vs_buy}")
    print(f"\n  Core vs. Context:")
    print(f"  {b.core_vs_context}")
    print(f"\n  Outsourcing Risks:")
    print(f"  {b.outsourcing_risks}")
    print(f"\n  Expansion Opportunities:")
    print(f"  {b.expansion_opportunities}")
    print(f"\n  Confidence: [{b.confidence.upper()}]")

    # SWOT
    print(f"\n{'='*60}")
    print(f"SWOT ANALYSIS: {analysis.company_name}")
    print(f"{'='*60}")

    for label, category in [
        ("STRENGTHS", analysis.swot.strengths),
        ("WEAKNESSES", analysis.swot.weaknesses),
        ("OPPORTUNITIES", analysis.swot.opportunities),
        ("THREATS", analysis.swot.threats),
    ]:
        print(f"\n  {label}  [{category.confidence.upper()}]:")
        for item in category.items:
            print(f"    - {item}")

    # Sustainable Advantages
    print(f"\n{'='*60}")
    print(f"SUSTAINABLE COMPETITIVE ADVANTAGES")
    print(f"{'='*60}")
    for i, adv in enumerate(analysis.sustainable_advantages, 1):
        print(f"  {i}. {adv}")


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

    analysis = analyze_strategy("Anthropic", profile_data, competitors_data, client)
    display_strategic_analysis(analysis)

    os.makedirs("output", exist_ok=True)
    with open("output/Anthropic_strategic_analysis.json", "w") as f:
        json.dump(analysis.model_dump(), f, indent=2)
    print(f"\nDone. Strategic analysis saved to output/Anthropic_strategic_analysis.json")
