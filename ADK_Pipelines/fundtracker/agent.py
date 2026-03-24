"""
Fund/Litigation Tracker — Monitor Court Dockets → Write to Fund_Dash DB
Uses ParallelAgent + SequentialAgent

Architecture:
  FundPipeline (Sequential)
    ├── CaseDiscoverer         → discovers relevant cases from the topic
    ├── DocketSwarm (Parallel) → scrapes multiple docket sources simultaneously
    │     ├── CourtScanner       — federal court filings
    │     ├── NewsScanner        — legal news and updates
    │     └── GovScanner         — government fund status pages
    ├── ChangeDetector          → identifies new filings, deadlines, status changes
    └── DBWriter                → writes discoveries to Fund_Dash SQLite database

Auto-discovers cases — works for ANY fund or litigation.
Writes directly to Fund_Dash DB so the dashboard updates automatically.

Example prompts:
  - "Track USVSST September 11th Victim Compensation Fund updates"
  - "Monitor Camp Lejeune Justice Act litigation"
  - "Check for new filings in the Purdue Pharma settlement"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from fundtracker.tools.fund_tools import (
    search_court_dockets, scrape_legal_page, save_tracker_report,
    ingest_article, ingest_case, create_alert, link_case_to_article,
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: DISCOVER CASES
# ═══════════════════════════════════════════════════════════════

case_discoverer = LlmAgent(
    name="CaseDiscoverer",
    model="gemini-2.5-flash",
    description="Discovers relevant court cases and dockets from the user's topic.",
    instruction="""You discover court cases and legal proceedings.

Based on the user's topic:
1. Identify the key legal entities, fund names, and case identifiers
2. Generate search queries for court dockets, legal news, and gov status pages
3. Define what types of updates matter (new filings, deadlines, status changes)

Output a strategy JSON with:
- case_names: list of case/fund names to search
- court_queries: search terms for court dockets
- news_queries: search terms for legal news
- gov_queries: search terms for government fund status""",
    output_key="case_strategy",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL SCANNING
# ═══════════════════════════════════════════════════════════════

court_scanner = LlmAgent(
    name="CourtScanner",
    model="gemini-2.5-flash",
    description="Scans court docket sources for new filings.",
    instruction="""You scan court dockets for new filings and updates.

Read case_strategy from state, use the court_queries.
1. Use search_court_dockets for each query
2. Use scrape_legal_page on the most relevant results
3. Extract: filing dates, case numbers, motions, orders, deadlines

Output a structured list of court findings.""",
    tools=[search_court_dockets, scrape_legal_page],
    output_key="court_findings",
)

news_scanner = LlmAgent(
    name="NewsScanner",
    model="gemini-2.5-flash",
    description="Scans legal news for case updates.",
    instruction="""You scan legal news sources for case updates.

Read case_strategy from state, use the news_queries.
1. Use search_court_dockets (which also searches general legal news)
2. Use scrape_legal_page on relevant news articles
3. Extract: what happened, when, impact on claimants/beneficiaries

Output a structured list of news findings.""",
    tools=[search_court_dockets, scrape_legal_page],
    output_key="news_findings",
)

gov_scanner = LlmAgent(
    name="GovScanner",
    model="gemini-2.5-flash",
    description="Scans government fund status pages.",
    instruction="""You scan government pages for fund status updates.

Read case_strategy from state, use the gov_queries.
1. Use search_court_dockets to find official government status pages
2. Use scrape_legal_page to get current fund status
3. Extract: fund balance, claims processed, deadlines, policy changes

Output a structured list of government source findings.""",
    tools=[search_court_dockets, scrape_legal_page],
    output_key="gov_findings",
)

docket_swarm = ParallelAgent(
    name="DocketSwarm",
    description="Scans court, news, and gov sources simultaneously.",
    sub_agents=[court_scanner, news_scanner, gov_scanner],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: DETECT CHANGES
# ═══════════════════════════════════════════════════════════════

change_detector = LlmAgent(
    name="ChangeDetector",
    model="gemini-2.5-flash",
    description="Identifies what's new and what it means for stakeholders.",
    instruction="""You analyze all findings to identify what's changed.

Read: court_findings, news_findings, gov_findings from state.

Produce:
1. NEW DEVELOPMENTS — what just happened (filings, rulings, announcements)
2. UPCOMING DEADLINES — dates claimants need to know about
3. STATUS CHANGES — fund balance, processing times, policy updates
4. IMPACT ANALYSIS — what this means for claimants/beneficiaries
5. ACTION ITEMS — what stakeholders should do now

Rate each item: 🔴 URGENT / 🟡 IMPORTANT / 🟢 FYI""",
    output_key="changes",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: WRITE TO FUND_DASH DB + GENERATE REPORT
# ═══════════════════════════════════════════════════════════════

db_writer = LlmAgent(
    name="DBWriter",
    model="gemini-2.5-flash",
    description="Writes discoveries to the Fund_Dash database and generates reports.",
    instruction="""You persist all discoveries to the Fund_Dash dashboard database.

Read: court_findings, news_findings, gov_findings, changes from state.

For EVERY article/filing/document found:
1. Use ingest_article to save it (source: 'doj', 'ofac', 'treasury', 'federal_register', 'court', 'news')
   - Include keyword_hits as a JSON list like '["iran","forfeiture","IEEPA"]'

For EVERY case/fund identified:
2. Use ingest_case to add/update it in the watchlist
   - category: 'crypto', 'iran', 'syria', 'dprk', 'al_qaeda', 'hezbollah', or 'general'
   - stage: 'filed', 'seized', 'litigation', 'forfeited', 'liquidation', 'transfer', 'deposit', 'paid'
   - Include est_amount (estimated dollar value, use 0 if unknown)

3. Use link_case_to_article to connect cases to their source articles

For 🔴 URGENT or 🟡 IMPORTANT items from the changes analysis:
4. Use create_alert with appropriate severity and evidence JSON

Finally:
5. Use save_tracker_report to write:
   - /tmp/fundtracker-report.md — full update with all findings
   - /tmp/fundtracker-alerts.md — urgent items only

After writing to the DB, the Fund_Dash dashboard at localhost:8000 will
automatically display the new data on its next page refresh.""",
    tools=[ingest_article, ingest_case, create_alert, link_case_to_article, save_tracker_report],
    output_key="tracker_report",
)

# ═══════════════════════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="FundPipeline",
    description="Litigation tracker: discover cases → parallel scan court/news/gov → detect changes → write to Fund_Dash DB.",
    sub_agents=[case_discoverer, docket_swarm, change_detector, db_writer],
)
