"""
Government Regulatory Watch — Continuous Monitoring with LoopAgent
Uses LoopAgent + ParallelAgent + SequentialAgent

Architecture:
  GovWatchPipeline (Sequential)
    ├── SourceDiscoverer         → discovers relevant gov sources from the topic
    ├── ParallelScanner (Parallel) → scans 3 sources simultaneously
    │     ├── FederalRegisterScanner  — new rules, proposed rules, notices
    │     ├── IRSScanner              — tax updates, revenue rulings, guidance
    │     └── CongressScanner         — bills, hearings, committee reports
    ├── ChangeAnalyzer           → identifies what's new and what it means
    └── AlertGenerator           → writes actionable alerts + saves report

Auto-discovers relevant sources — works for ANY regulatory domain.

Example prompts:
  - "Monitor VCF and 9/11 victim compensation regulatory changes"
  - "Watch for IRS changes affecting first responder retirement"
  - "Track legislation about veterans benefits"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from govwatch.tools.gov_tools import (
    search_federal_register, search_irs_newsroom,
    search_congress, scrape_gov_page, save_alert
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: DISCOVER RELEVANT SOURCES
# ═══════════════════════════════════════════════════════════════

source_discoverer = LlmAgent(
    name="SourceDiscoverer",
    model="gemini-2.5-flash",
    description="Discovers which government sources are relevant to the user's topic.",
    instruction="""You determine which government sources to monitor.

Based on the user's topic, generate 3-5 specific search queries for each source:
1. Federal Register — regulatory rules and proposed rules
2. IRS Newsroom — tax guidance and announcements
3. Congress.gov — legislation and hearings

For example, if the user says "VCF claims", you'd search:
- Federal Register: "September 11th Victim Compensation Fund"
- IRS: "victim compensation fund tax treatment"
- Congress: "Zadroga Act" and "VCF reauthorization"

Output the search queries as a JSON object:
{
  "federal_register_queries": ["query1", "query2"],
  "irs_queries": ["query1", "query2"],
  "congress_queries": ["query1", "query2"]
}""",
    output_key="search_queries",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL SCANNING (3 sources at once)
# ═══════════════════════════════════════════════════════════════

fed_register_scanner = LlmAgent(
    name="FederalRegisterScanner",
    model="gemini-2.5-flash",
    description="Scans the Federal Register for new rules and notices.",
    instruction="""You scan the Federal Register for regulatory updates.

Read search_queries from state, find the federal_register_queries.

For each query:
1. Use search_federal_register to find recent documents
2. For the most important results, use scrape_gov_page to get full details

Focus on:
- Final rules (these are law now)
- Proposed rules (these are coming soon)
- Notices (important announcements)

Output all findings with dates, summaries, and impact assessment.""",
    tools=[search_federal_register, scrape_gov_page],
    output_key="fed_results",
)

irs_scanner = LlmAgent(
    name="IRSScanner",
    model="gemini-2.5-flash",
    description="Scans IRS newsroom for tax updates.",
    instruction="""You scan the IRS newsroom for tax-related updates.

Read search_queries from state, find the irs_queries.

For each query:
1. Use search_irs_newsroom to find recent newsroom posts
2. For the most important results, use scrape_gov_page to get full content

Focus on:
- Revenue rulings and procedures
- Tax guidance and notices
- Deadline changes
- New forms or requirements

Output all findings with dates, summaries, and who's affected.""",
    tools=[search_irs_newsroom, scrape_gov_page],
    output_key="irs_results",
)

congress_scanner = LlmAgent(
    name="CongressScanner",
    model="gemini-2.5-flash",
    description="Scans Congress.gov for legislation and hearings.",
    instruction="""You scan Congress.gov for legislative updates.

Read search_queries from state, find the congress_queries.

For each query:
1. Use search_congress to find relevant legislation
2. For the most important results, use scrape_gov_page to get full details

Focus on:
- New bills introduced
- Bills advancing (committee votes, floor votes)
- Hearings scheduled
- Committee reports

Output all findings with dates, status, and impact assessment.""",
    tools=[search_congress, scrape_gov_page],
    output_key="congress_results",
)

# PARALLEL: All 3 scanners run simultaneously
parallel_scanner = ParallelAgent(
    name="ParallelScanner",
    description="Scans Federal Register, IRS, and Congress simultaneously.",
    sub_agents=[fed_register_scanner, irs_scanner, congress_scanner],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: ANALYZE CHANGES
# ═══════════════════════════════════════════════════════════════

change_analyzer = LlmAgent(
    name="ChangeAnalyzer",
    model="gemini-2.5-flash",
    description="Analyzes all scan results to identify what matters.",
    instruction="""You analyze all government scan results.

Read from state: fed_results, irs_results, congress_results.

Produce:
1. PRIORITY ALERTS (must-know items)
   - What changed or is changing?
   - Who is affected?
   - What's the timeline?
   - What action is needed?

2. WATCH LIST (items to track)
   - Proposed rules that haven't been finalized
   - Bills in committee
   - Upcoming hearings or deadlines

3. IMPACT ANALYSIS
   - How do these changes affect the user's specific niche?
   - Are there opportunities (new programs, expanded benefits)?
   - Are there risks (new requirements, reduced benefits)?

4. TIMELINE
   - Key dates and deadlines in the next 90 days

Rate each finding: 🔴 URGENT / 🟡 WATCH / 🟢 FYI""",
    output_key="analysis",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: GENERATE ALERTS
# ═══════════════════════════════════════════════════════════════

alert_generator = LlmAgent(
    name="AlertGenerator",
    model="gemini-2.5-flash",
    description="Generates actionable regulatory alerts and saves reports.",
    instruction="""You generate the final regulatory intelligence report.

1. Read the analysis from state
2. Use save_alert to write:
   - /tmp/govwatch-alerts.md — priority alerts with action items
   - /tmp/govwatch-report.md — full regulatory intelligence report
   - /tmp/govwatch-timeline.md — key dates and deadlines

Each alert must include:
- What happened
- Who is affected
- What to do about it
- Deadline (if applicable)
- Source URL

Make everything actionable and specific to the user's niche.""",
    tools=[save_alert],
    output_key="alerts",
)

# ═══════════════════════════════════════════════════════════════
# ROOT: SEQUENTIAL PIPELINE
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="GovWatchPipeline",
    description="Regulatory monitoring: discover sources → parallel scan 3 agencies → analyze changes → generate alerts.",
    sub_agents=[
        source_discoverer,
        parallel_scanner,
        change_analyzer,
        alert_generator,
    ],
)
