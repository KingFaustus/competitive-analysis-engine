"""
Agent 1: Company Profiler
Generates a structured company profile with sources and confidence flags.
"""

import json
from typing import Optional
from anthropic import Anthropic
from pydantic import BaseModel


class Source(BaseModel):
    url: str
    note: str
    confidence: str


class CompanyProfile(BaseModel):
    company_name: str
    industry: str
    business_model: str
    key_products: list[str]
    revenue_estimate: Optional[str]
    employees: Optional[str]
    headquarters: str
    founded: Optional[str]
    public_or_private: str
    sources: list[Source]


def profile_company(company_name: str, client: Anthropic) -> CompanyProfile:
    system_prompt = """You are a research analyst specializing in company profiling.
Your task is to gather structured information about companies from your training data.

For each piece of information you return:
1. Include the source (company website, news outlet, SEC filing, etc.)
2. Assign a confidence level (high/medium/low) based on how reliable the source is
3. Record a brief note about where this information comes from

High confidence: Official company sites, SEC filings, major news outlets (Reuters, Bloomberg, AP)
Medium confidence: Industry reports, secondary news sources, Wikipedia
Low confidence: Social media, blogs, unverified sources

Return ONLY valid JSON matching this exact schema, no markdown:
{
    "company_name": "string",
    "industry": "string",
    "business_model": "string",
    "key_products": ["string"],
    "revenue_estimate": "string or null",
    "employees": "string or null",
    "headquarters": "string",
    "founded": "string or null",
    "public_or_private": "string",
    "sources": [
        {
            "url": "string",
            "note": "string",
            "confidence": "high|medium|low"
        }
    ]
}"""

    messages = [
        {
            "role": "user",
            "content": f"Profile this company based on your training data: {company_name}"
        }
    ]

    print(f"\n[ Agent 1 ] Profiling {company_name}...")

    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=2000,
        system=system_prompt,
        messages=messages
    )

    result_text = response.content[0].text

    try:
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]

        profile_data = json.loads(result_text.strip())
        profile = CompanyProfile(**profile_data)
        return profile
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse profile response: {e}")
        print(f"Raw response: {result_text}")
        raise


def display_profile(profile: CompanyProfile) -> None:
    print(f"\n{'='*60}")
    print(f"COMPANY PROFILE: {profile.company_name}")
    print(f"{'='*60}")
    print(f"  Industry:          {profile.industry}")
    print(f"  Business Model:    {profile.business_model}")
    print(f"  Key Products:      {', '.join(profile.key_products)}")
    print(f"  Revenue Estimate:  {profile.revenue_estimate or 'N/A'}")
    print(f"  Employees:         {profile.employees or 'N/A'}")
    print(f"  Headquarters:      {profile.headquarters}")
    print(f"  Founded:           {profile.founded or 'N/A'}")
    print(f"  Status:            {profile.public_or_private}")

    print(f"\n  SOURCES ({len(profile.sources)} found):")
    for i, source in enumerate(profile.sources, 1):
        print(f"  {i}. [{source.confidence.upper()}] {source.url}")
        print(f"       {source.note}")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env")
        exit(1)

    client = Anthropic(api_key=api_key)

    profile = profile_company("Anthropic", client)
    display_profile(profile)

    os.makedirs("output", exist_ok=True)
    with open(f"output/{profile.company_name}_profile.json", "w") as f:
        json.dump(profile.model_dump(), f, indent=2)
    print(f"\nDone. Profile saved to output/{profile.company_name}_profile.json")
