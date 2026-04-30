#!/usr/bin/env python3
"""
Competitive Analysis Agent
Orchestrates a 5-agent pipeline to generate consulting-grade competitive analysis.

Usage:
    python3 main.py --company "Anthropic"
    python3 main.py --company "Tesla" --output-format markdown
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

from company_profiler import profile_company, display_profile
from competitor_finder import find_competitors, display_competitors
from strategic_analyst import analyze_strategy, display_strategic_analysis
from recommender import generate_recommendations, display_recommendations
from summary_writer import generate_summaries, display_summaries


def generate_markdown_report(
    company_name: str,
    profile: dict,
    competitors: dict,
    strategic: dict,
    recommendations: dict,
    summary: dict,
    output_dir: str
) -> str:

    forces = strategic.get('porters', {})
    boundaries = strategic.get('boundaries', {})
    swot = strategic.get('swot', {})
    recs = recommendations.get('recommendations', [])
    horizon_label = {"short": "0-6 months", "medium": "6-18 months", "long": "18+ months"}

    lines = []

    # Header
    lines.append(f"# Competitive Analysis: {company_name}")
    lines.append(f"*Generated: {datetime.now().strftime('%B %d, %Y')}*")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"> {summary.get('one_sentence', '')}")
    lines.append("")
    lines.append(summary.get('one_paragraph', ''))
    lines.append("")

    # Company Overview
    lines.append("## Company Overview")
    lines.append("")
    lines.append("| Field | Detail |")
    lines.append("|-------|--------|")
    lines.append(f"| Industry | {profile.get('industry', 'N/A')} |")
    lines.append(f"| Business Model | {profile.get('business_model', 'N/A')} |")
    lines.append(f"| Headquarters | {profile.get('headquarters', 'N/A')} |")
    lines.append(f"| Founded | {profile.get('founded', 'N/A')} |")
    lines.append(f"| Status | {profile.get('public_or_private', 'N/A')} |")
    lines.append(f"| Employees | {profile.get('employees', 'N/A')} |")
    lines.append(f"| Revenue Estimate | {profile.get('revenue_estimate', 'N/A')} |")
    lines.append("")
    lines.append("**Key Products & Services**")
    for product in profile.get('key_products', []):
        lines.append(f"- {product}")
    lines.append("")

    # Competitive Landscape
    lines.append("## Competitive Landscape")
    lines.append("")
    lines.append("| Competitor | Threat Level | Market Overlap | Confidence |")
    lines.append("|------------|-------------|----------------|------------|")
    for comp in competitors.get('competitors', []):
        lines.append(f"| {comp['name']} | {comp['threat_level']}/5 | {comp['market_overlap']}/5 | {comp['confidence'].upper()} |")
    lines.append("")
    for comp in competitors.get('competitors', []):
        lines.append(f"**{comp['name']}** — {comp['why_competitor']}")
        lines.append("")

    # Porter's Five Forces
    lines.append("## Porter's Five Forces Analysis")
    lines.append("")
    lines.append("| Force | Score | Confidence |")
    lines.append("|-------|-------|------------|")

    force_keys = [
        ("threat_of_new_entrants", "Threat of New Entrants"),
        ("bargaining_power_of_suppliers", "Bargaining Power of Suppliers"),
        ("bargaining_power_of_buyers", "Bargaining Power of Buyers"),
        ("threat_of_substitutes", "Threat of Substitutes"),
        ("competitive_rivalry", "Competitive Rivalry"),
    ]

    for key, label in force_keys:
        force = forces.get(key, {})
        lines.append(f"| {label} | {force.get('score', 'N/A')}/5 | {force.get('confidence', 'N/A').upper()} |")
    lines.append("")

    for key, label in force_keys:
        force = forces.get(key, {})
        lines.append(f"**{label} ({force.get('score', 'N/A')}/5)**")
        lines.append(force.get('explanation', ''))
        lines.append("")

    # Boundaries of the Firm
    lines.append("## Boundaries of the Firm")
    lines.append(f"*Confidence: {boundaries.get('confidence', 'N/A').upper()}*")
    lines.append("")
    lines.append("| Dimension | Assessment |")
    lines.append("|-----------|------------|")
    lines.append(f"| Vertical Integration | {boundaries.get('vertical_integration', 'N/A')} |")
    lines.append(f"| Make vs. Buy | {boundaries.get('make_vs_buy', 'N/A')} |")
    lines.append(f"| Core vs. Context | {boundaries.get('core_vs_context', 'N/A')} |")
    lines.append(f"| Outsourcing Risks | {boundaries.get('outsourcing_risks', 'N/A')} |")
    lines.append(f"| Expansion Opportunities | {boundaries.get('expansion_opportunities', 'N/A')} |")
    lines.append("")

    # SWOT
    lines.append("## SWOT Analysis")
    lines.append("")
    for category, label in [
        ("strengths", "Strengths"),
        ("weaknesses", "Weaknesses"),
        ("opportunities", "Opportunities"),
        ("threats", "Threats"),
    ]:
        cat_data = swot.get(category, {})
        lines.append(f"### {label} [{cat_data.get('confidence', 'N/A').upper()}]")
        for item in cat_data.get('items', []):
            lines.append(f"- {item}")
        lines.append("")

    # Competitive Advantages
    lines.append("## Sustainable Competitive Advantages")
    lines.append("")
    for i, adv in enumerate(strategic.get('sustainable_advantages', []), 1):
        lines.append(f"{i}. {adv}")
    lines.append("")

    # Strategic Recommendations
    lines.append("## Strategic Recommendations")
    lines.append("")
    lines.append("| # | Recommendation | Priority | Timeline | Difficulty |")
    lines.append("|---|---------------|----------|----------|------------|")
    for i, rec in enumerate(recs, 1):
        lines.append(f"| {i} | {rec['title']} | {rec['priority'].upper()} | {horizon_label.get(rec['time_horizon'])} | {rec['implementation_difficulty']}/5 |")
    lines.append("")

    for i, rec in enumerate(recs, 1):
        lines.append(f"### {i}. {rec['title']}")
        lines.append(f"**Priority:** {rec['priority'].upper()} | **Timeline:** {horizon_label.get(rec['time_horizon'])} | **Difficulty:** {rec['implementation_difficulty']}/5 | **Confidence:** {rec['confidence'].upper()}")
        lines.append("")
        lines.append(f"**Expected Impact:** {rec['expected_impact']}")
        lines.append("")
        lines.append(rec['rationale'])
        lines.append("")

    # Full Executive Summary
    lines.append("## Full Executive Summary")
    lines.append("")
    lines.append(summary.get('one_page', ''))
    lines.append("")

    # Sources Appendix
    lines.append("## Sources & Confidence Appendix")
    lines.append("")
    lines.append("| Source | Note | Confidence |")
    lines.append("|--------|------|------------|")
    for source in profile.get('sources', []):
        lines.append(f"| {source['url']} | {source['note']} | {source['confidence'].upper()} |")
    lines.append("")
    lines.append("*Confidence flags: HIGH = primary sources (official sites, SEC filings, major press). MEDIUM = secondary sources. LOW = unverified.*")
    lines.append("")
    lines.append("---")
    lines.append(f"*Generated by Competitive Analysis Agent*")

    report = "\n".join(lines)
    report_path = os.path.join(output_dir, "analysis_report.md")
    with open(report_path, "w") as f:
        f.write(report)

    return report_path


def main():
    parser = argparse.ArgumentParser(
        description="Competitive Analysis Agent — consulting-grade analysis in minutes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py --company "Anthropic"
  python3 main.py --company "Tesla" --output-format markdown
  python3 main.py --company "Stripe"
        """
    )
    parser.add_argument("--company", required=True, help="Company name to analyze")
    parser.add_argument("--output-format", default="both", choices=["json", "markdown", "both"],
                        help="Output format (default: both)")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not found in .env")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    company_name = args.company
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"output/{company_name.replace(' ', '_')}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"COMPETITIVE ANALYSIS AGENT")
    print(f"{'='*60}")
    print(f"Company:  {company_name}")
    print(f"Output:   {output_dir}/")
    print(f"{'='*60}")

    # Agent 1: Company Profile
    print(f"\n[ 1/5 ] Profiling company...")
    profile = profile_company(company_name, client)
    display_profile(profile)
    with open(f"{output_dir}/profile.json", "w") as f:
        json.dump(profile.model_dump(), f, indent=2)

    # Agent 2: Competitor Finder
    print(f"\n[ 2/5 ] Identifying competitors...")
    competitors = find_competitors(company_name, profile.model_dump(), client)
    display_competitors(competitors)
    with open(f"{output_dir}/competitors.json", "w") as f:
        json.dump(competitors.model_dump(), f, indent=2)

    # Agent 3: Strategic Analysis
    print(f"\n[ 3/5 ] Running strategic analysis...")
    strategic = analyze_strategy(company_name, profile.model_dump(), competitors.model_dump(), client)
    display_strategic_analysis(strategic)
    with open(f"{output_dir}/strategic_analysis.json", "w") as f:
        json.dump(strategic.model_dump(), f, indent=2)

    # Agent 4: Recommendations
    print(f"\n[ 4/5 ] Generating recommendations...")
    recs = generate_recommendations(company_name, profile.model_dump(), competitors.model_dump(), strategic.model_dump(), client)
    display_recommendations(recs)
    with open(f"{output_dir}/recommendations.json", "w") as f:
        json.dump(recs.model_dump(), f, indent=2)

    # Agent 5: Executive Summaries
    print(f"\n[ 5/5 ] Writing executive summaries...")
    summary = generate_summaries(company_name, profile.model_dump(), competitors.model_dump(), strategic.model_dump(), recs.model_dump(), client)
    display_summaries(summary)
    with open(f"{output_dir}/executive_summary.json", "w") as f:
        json.dump(summary.model_dump(), f, indent=2)

    # Generate markdown report
    if args.output_format in ("markdown", "both"):
        report_path = generate_markdown_report(
            company_name,
            profile.model_dump(),
            competitors.model_dump(),
            strategic.model_dump(),
            recs.model_dump(),
            summary.model_dump(),
            output_dir
        )
        print(f"\nMarkdown report: {report_path}")

    # Save combined JSON
    if args.output_format in ("json", "both"):
        combined = {
            "company": company_name,
            "generated_at": datetime.now().isoformat(),
            "profile": profile.model_dump(),
            "competitors": competitors.model_dump(),
            "strategic_analysis": strategic.model_dump(),
            "recommendations": recs.model_dump(),
            "executive_summary": summary.model_dump()
        }
        combined_path = f"{output_dir}/analysis_data.json"
        with open(combined_path, "w") as f:
            json.dump(combined, f, indent=2)
        print(f"JSON data:       {combined_path}")

    print(f"\n{'='*60}")
    print(f"ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Company:  {company_name}")
    print(f"Output:   {output_dir}/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
