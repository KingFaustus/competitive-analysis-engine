# Competitive Analysis Agent

**Consulting-grade competitive analysis. Five agents. Five minutes.**

This tool generates structured competitive analyses for any company — complete with Porter's Five Forces, Boundaries of the Firm, SWOT, competitor profiling, strategic recommendations, and three executive summary variants. Output is delivered as a professional markdown report and structured JSON, ready for refinement by a strategist or direct use in a presentation.

| Traditional Consulting Research | This Tool |
|----------------------------------|-----------|
| 20-40 hours of analyst time | 5 minutes |
| Variable quality across analysts | Consistent structured output |
| No confidence flagging | Every claim confidence-rated |
| No audit trail | Full sources appendix |

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Anthropic](https://img.shields.io/badge/Powered%20by-Claude-orange)

---

## The Problem

Competitive analysis is one of the highest-value, highest-effort deliverables in strategy work. A credible competitive landscape review — covering market positioning, competitive forces, and strategic options — typically requires 20 to 40 hours of junior analyst time: scraping websites, reading earnings calls, synthesizing industry reports, and structuring findings into a coherent narrative. Under deadline pressure, quality suffers. Across analysts, consistency suffers.

The bottleneck is not insight — it is the mechanical labor of research assembly. Junior analysts spend the majority of their time gathering and formatting information that could be structured automatically, leaving less time for the higher-order synthesis that actually drives strategy decisions.

This tool addresses that bottleneck directly. It produces a structured first-draft competitive analysis in under five minutes — with sourced claims, confidence flags, and consulting-standard frameworks — so that strategists can spend their time refining and pressure-testing conclusions rather than assembling raw inputs. It is designed as an accelerator for human judgment, not a replacement for it.

---

## What It Does

Given a company name, the pipeline runs five specialized agents in sequence and produces a complete competitive analysis package.

**Deliverables per analysis:**

| # | Deliverable | Description |
|---|-------------|-------------|
| 1 | Company Overview | Industry, business model, key products, funding status |
| 2 | Market Position | Revenue estimate, employee count, founding context |
| 3 | Top 5 Competitors | Identified and profiled with threat and overlap scores |
| 4 | Porter's Five Forces | Each force scored 1-5 with explanation and confidence flag |
| 5 | Boundaries of the Firm | Vertical integration, make vs. buy, core vs. context, outsourcing risks |
| 6 | SWOT Analysis | Four categories, evidence-backed, with confidence rating |
| 7 | Competitive Advantages | Identified and assessed for sustainability |
| 8 | Strategic Risks | Derived from forces, threats, and boundary analysis |
| 9 | Strategic Recommendations | 3-5 prioritized recommendations with timeline and difficulty |
| 10 | Executive Summary | Three variants: one sentence, one paragraph, one page |

**Sample CLI output:**
---

## Why This Matters

The ROI case is straightforward. A mid-market strategy team running 50 competitive analyses per year at 20 hours each represents 1,000 hours of analyst labor — roughly $150,000 in fully-loaded cost at a typical consulting billing rate. This tool reduces that first-draft assembly time to near zero, compressing the timeline for each engagement and freeing analysts for higher-value synthesis work.

Beyond individual productivity, this project reflects a broader shift in how strategy work gets done. McKinsey QuantumBlack, BCG X, and Bain Vector are each building internal AI tooling that automates exactly this kind of structured research and analysis. The firms that systematize this layer of work will outpace those that continue relying on manual research processes — not because AI produces better strategy, but because it produces faster, more consistent inputs for the humans who do.

This tool is a practical demonstration of that direction: multi-agent AI architecture applied to a real consulting workflow, with the rigor (confidence flags, source tracking, structured schemas) that separates production tooling from prompt engineering experiments.

---

## Architecture
**Agent responsibilities:**

| Agent | File | Input | Output |
|-------|------|-------|--------|
| Company Profiler | `company_profiler.py` | Company name | Structured profile + sources |
| Competitor Finder | `competitor_finder.py` | Company profile | Top 5 competitors with scores |
| Strategic Analyst | `strategic_analyst.py` | Profile + competitors | Porter's, Boundaries, SWOT |
| Recommendation Engine | `recommender.py` | All prior outputs | Prioritized recommendations |
| Summary Writer | `summary_writer.py` | All prior outputs | Three executive summary variants |

---

## Sample Output

The following analysis was generated against Anthropic. Full report: [`samples/Anthropic_analysis_report.md`](samples/Anthropic_analysis_report.md)

**One-sentence summary:**

> Anthropic must leverage its AI safety leadership to capture enterprise markets through strategic partnerships and specialized offerings, or risk being overwhelmed by better-resourced competitors despite technical excellence.

**Competitor landscape:**

| Competitor | Threat Level | Market Overlap | Confidence |
|------------|-------------|----------------|------------|
| OpenAI | 5/5 | 5/5 | HIGH |
| Google DeepMind | 5/5 | 4/5 | HIGH |
| Microsoft / Azure AI | 4/5 | 4/5 | HIGH |
| Cohere | 3/5 | 4/5 | HIGH |
| Meta AI (FAIR) | 3/5 | 3/5 | HIGH |

**Porter's Five Forces summary:**

| Force | Score | Confidence |
|-------|-------|------------|
| Threat of New Entrants | 3/5 | HIGH |
| Bargaining Power of Suppliers | 4/5 | HIGH |
| Bargaining Power of Buyers | 3/5 | HIGH |
| Threat of Substitutes | 2/5 | MEDIUM |
| Competitive Rivalry | 5/5 | HIGH |

**Top recommendation:**

> Establish Strategic Enterprise Partnerships — Priority: HIGH | Timeline: 0-6 months | Difficulty: 2/5
> Leverage Anthropic's safety-first reputation to secure distribution through enterprise software leaders in regulated industries, directly addressing the scale disadvantage while capturing growing demand for trustworthy AI.

---

## Engineering Decisions

**Multi-agent design over a single prompt.** A single prompt producing all outputs simultaneously creates fragility: one malformed section corrupts the entire response. Specialized agents produce isolated, validated outputs that feed forward into subsequent agents. Failures are localized and debuggable.

**Structured JSON schemas.** Every agent returns a validated Pydantic model. This eliminates string parsing, enables reliable downstream consumption, and makes outputs composable. The schemas also enforce consistency — every claim carries a confidence flag by design, not by convention.

**Confidence flags on every claim.** Consulting work lives and dies by credibility. Flagging claims as HIGH, MEDIUM, or LOW confidence — based on source quality — mirrors the practice of senior analysts who distinguish between verified data and informed estimates. It gives the reader the information they need to decide what to pressure-test.

**Boundaries of the Firm analysis.** Most competitive analysis tools stop at Porter's and SWOT. The Boundaries of the Firm framework — vertical integration, make vs. buy, core vs. context — surfaces the structural strategic questions that determine a company's competitive trajectory. It is a standard McKinsey and BCG framework that is rarely included in automated tools.

**Source appendix.** Every profile includes a sources table with URLs, notes, and confidence ratings. This is non-negotiable for consulting-grade output. Without it, the analysis is an opinion. With it, it is an auditable first draft.

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Language Model | Anthropic Claude (`claude-opus-4-1`) |
| Agent Orchestration | Python — custom pipeline in `main.py` |
| Data Validation | Pydantic v2 — typed schemas per agent |
| Environment Config | python-dotenv |
| Output Formatting | Native Python — markdown + JSON |
| Runtime | Python 3.9+ |

---

## Getting Started

**Quick start (3 commands):**

```bash
git clone https://github.com/KingFaustus/competitive-analysis-engine
cd competitive-analysis-agent
pip install -r requirements.txt
```

**Configuration:**

```bash
cp .env.example .env
# Add your Anthropic API key to .env:
# ANTHROPIC_API_KEY=sk-ant-...
```

**Run an analysis:**

```bash
python3 main.py --company "Anthropic"
python3 main.py --company "Tesla" --output-format markdown
python3 main.py --company "Stripe" --output-format json
```

**Output location:**
**Run individual agents for testing:**

```bash
python3 company_profiler.py       # Agent 1 standalone
python3 competitor_finder.py      # Agent 2 standalone
python3 strategic_analyst.py      # Agent 3 standalone
python3 recommender.py            # Agent 4 standalone
python3 summary_writer.py         # Agent 5 standalone
```

---

## Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | Complete | 5-agent pipeline — profiling, competitors, Porter's, Boundaries of the Firm, SWOT, recommendations, executive summaries |
| Phase 2 | Planned | Visual outputs — competitive positioning map, strategic roadmap timeline, benchmark comparison table |
| Phase 3 | Vision | Financial dashboard — P&L analysis for public companies, scenario modeling, auto-generated slide deck |
| Phase 4 | Long-term | Interactive web dashboard, PDF export, industry-wide analysis mode |

---

## Limitations

This tool is designed as a first-draft accelerator, not a replacement for analyst judgment. Users should be aware of the following constraints:

**Data recency.** The underlying model's training data has a knowledge cutoff. For fast-moving industries, recent funding rounds, executive changes, or product launches may not be reflected. Outputs should be verified against current sources before use in client-facing work.

**Hallucination risk.** Large language models can generate plausible-sounding but inaccurate claims. Confidence flags indicate source quality, not factual certainty. All HIGH-confidence claims should still be spot-checked against primary sources.

**Confidence flags are estimates.** The HIGH/MEDIUM/LOW ratings reflect the agent's assessment of source credibility, not independent verification. They are a starting point for due diligence, not a substitute for it.

**Framework application is generalized.** Porter's Five Forces, Boundaries of the Firm, and SWOT are applied through reasoning about publicly available information. Industry-specific nuances, proprietary data, and qualitative factors known to domain experts will not be captured.

**Not a substitute for primary research.** Customer interviews, expert calls, and internal data remain irreplaceable inputs for strategic decisions. This tool accelerates the secondary research layer only.

---

## About

Built by an MBA candidate at Johns Hopkins Carey Business School, studying Competitive Strategy and applying AI engineering to consulting workflows. This project demonstrates the intersection of multi-agent systems design and structured business analysis — the kind of tooling that strategy teams at top firms are building internally.

[LinkedIn](https://linkedin.com/in/your-profile) — open to conversations about AI in consulting, strategy, and product.

---

*Generated analyses are first-draft outputs intended for refinement by qualified strategists. Not intended for direct use in client deliverables without human review.*
