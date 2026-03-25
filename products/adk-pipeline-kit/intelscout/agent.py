"""
Competitive Intelligence Scout — Parallel Competitor Analysis
Uses ParallelAgent + SequentialAgent

Architecture:
  IntelPipeline (Sequential)
    ├── CompetitorDiscoverer    → auto-discovers competitors from the market
    ├── IntelSwarm (Parallel)   → scrapes all competitors simultaneously
    │     ├── Scraper_1
    │     ├── Scraper_2
    │     └── Scraper_3 (up to 5)
    ├── StrategyAnalyst         → compares positioning, pricing, gaps
    └── ReportGenerator         → SWOT, battle cards, opportunity map

Auto-discovers competitors — works for ANY market or niche.

Example prompts:
  - "Analyze competitors in financial advisory for 9/11 families"
  - "Research the AI automation tools market"
  - "Find competitors to my retirement planning service for first responders"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from intelscout.tools.intel_tools import (
    discover_competitors, scrape_competitor, save_intel_report
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: AUTO-DISCOVER COMPETITORS
# ═══════════════════════════════════════════════════════════════

competitor_discoverer = LlmAgent(
    name="CompetitorDiscoverer",
    model="gemini-2.5-flash",
    description="Auto-discovers competitors in the target market.",
    instruction="""You discover competitors in a market.

1. Use discover_competitors with the user's market/niche description
2. The tool searches Google with multiple queries to find companies
3. Review the results and identify the top 5 most relevant competitors
   (actual businesses, not directories or review sites)

Output a JSON list of the top 5 competitor URLs and domains.
These will be scraped in parallel by the next step.""",
    tools=[discover_competitors],
    output_key="competitor_list",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL SCRAPING
# ═══════════════════════════════════════════════════════════════

def _make_scraper(n):
    return LlmAgent(
        name=f"Scraper_{n}",
        model="gemini-2.5-flash",
        description=f"Scrapes competitor #{n} for business intelligence.",
        instruction=f"""You scrape one competitor for business intelligence.

Read the competitor_list from state and find competitor #{n}.
If competitor #{n} doesn't exist (fewer than {n} competitors), output "SKIP".

1. Use scrape_competitor on the competitor's URL
2. Analyze what you find:
   - What's their value proposition? (from H1/H2)
   - What services do they offer? (from content)
   - Do they have pricing? What tier?
   - What tech stack are they using?
   - What CTAs do they use? (booking, contact, free consult?)
   - What's their content quality? (word count, depth)

Output a structured analysis of this competitor.""",
        tools=[scrape_competitor],
        output_key=f"intel_{n}",
    )

scraper_1 = _make_scraper(1)
scraper_2 = _make_scraper(2)
scraper_3 = _make_scraper(3)
scraper_4 = _make_scraper(4)
scraper_5 = _make_scraper(5)

intel_swarm = ParallelAgent(
    name="IntelSwarm",
    description="Scrapes up to 5 competitors simultaneously.",
    sub_agents=[scraper_1, scraper_2, scraper_3, scraper_4, scraper_5],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: STRATEGIC ANALYSIS
# ═══════════════════════════════════════════════════════════════

strategy_analyst = LlmAgent(
    name="StrategyAnalyst",
    model="gemini-2.5-flash",
    description="Analyzes all competitor data to identify strategic opportunities.",
    instruction="""You are a competitive strategy analyst. Read all intel from state
(intel_1 through intel_5, skipping any that say "SKIP").

Produce a comprehensive analysis:

1. MARKET LANDSCAPE
   - How many active competitors did we find?
   - What's the overall market positioning?
   - Common value propositions across competitors

2. COMPETITIVE MATRIX
   - Compare: services, pricing, tech, content quality, CTAs
   - Identify the strongest and weakest competitors
   - Note any unique differentiators

3. GAP ANALYSIS
   - What services are underserved?
   - What audiences are being ignored?
   - Where is content thin or missing?

4. SWOT ANALYSIS
   - Strengths (across the market)
   - Weaknesses (common failures)
   - Opportunities (gaps to exploit)
   - Threats (strong incumbents)

5. BATTLE CARDS
   - For each competitor: 3 bullet "how to beat them" insights

Output the full strategic analysis.""",
    output_key="strategy",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: GENERATE REPORT
# ═══════════════════════════════════════════════════════════════

report_generator = LlmAgent(
    name="IntelReportGenerator",
    model="gemini-2.5-flash",
    description="Generates the final intelligence report.",
    instruction="""You generate the final competitive intelligence report.

1. Read the strategy analysis from state
2. Use save_intel_report to write:
   - /tmp/intelscout-report.md — full strategic report with SWOT, battle cards,
     competitive matrix, and recommended actions
   - /tmp/intelscout-summary.md — executive summary (1 page, key findings only)

The report must be actionable. Every insight should connect to a
specific action the user can take to gain competitive advantage.""",
    tools=[save_intel_report],
    output_key="final_report",
)

# ═══════════════════════════════════════════════════════════════
# ROOT: SEQUENTIAL PIPELINE
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="IntelPipeline",
    description="Competitive intelligence: auto-discover competitors → parallel scrape → strategic analysis → report.",
    sub_agents=[
        competitor_discoverer,
        intel_swarm,
        strategy_analyst,
        report_generator,
    ],
)
