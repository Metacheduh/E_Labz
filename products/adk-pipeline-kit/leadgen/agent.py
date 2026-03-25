"""
LeadGen System — Multi-Agent Lead Generation Pipeline
Uses ALL 4 ADK multi-agent patterns:
  - ParallelAgent  → 3 research agents run simultaneously
  - SequentialAgent → full pipeline: find → enrich → outreach → score
  - LlmAgent       → smart sub-agents with tools
  - LoopAgent ready → can add retry logic later

Architecture:
  LeadGenPipeline (SequentialAgent)
    ├── ProspectFinder (ParallelAgent)
    │     ├── GoogleSearcher    — searches Google
    │     ├── WebScraper        — scrapes company pages
    │     └── CompanyAnalyzer   — deep company analysis
    ├── LeadEnricher (LlmAgent) — combines + enriches
    ├── OutreachWriter (LlmAgent) — writes personalized emails
    └── LeadScorer (LlmAgent) — scores + ranks + exports CSV
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from leadgen.tools.search_tools import search_google, scrape_website, analyze_company_website
from leadgen.tools.output_tools import save_leads_csv, save_report, read_file

# ═══════════════════════════════════════════════════════════════
# STEP 1: PARALLEL PROSPECT FINDING
# 3 agents search simultaneously from different angles
# ═══════════════════════════════════════════════════════════════

google_searcher = LlmAgent(
    name="GoogleSearcher",
    model="gemini-2.5-flash",
    description="Searches Google to find prospect companies matching the target criteria.",
    instruction="""You are a prospect researcher. When given a target market or industry:

1. Use search_google with specific queries to find companies. Try multiple queries:
   - "[industry] companies [location]"
   - "top [industry] startups"
   - "[industry] companies hiring"
   - "[industry] [service] providers"
   
2. Run at least 3 different search queries to get diverse results.

3. Store your findings in state by setting output_key. Format as JSON list:
   [{"company": "...", "url": "...", "source": "google_search"}]

Focus on finding REAL companies with working URLs. Skip aggregator sites.""",
    tools=[search_google],
    output_key="google_prospects",
)

web_scraper = LlmAgent(
    name="WebScraper",
    model="gemini-2.5-flash",
    description="Scrapes discovered company websites to extract contact details and business info.",
    instruction="""You are a web intelligence agent. When given prospect URLs:

1. Use scrape_website on each company URL found
2. Extract: company name, emails, phone numbers, social links, description
3. Focus on finding CONTACT INFORMATION — emails and phones are gold

4. Store findings in state. Format as JSON list:
   [{"company": "...", "url": "...", "emails": [...], "phones": [...], "description": "..."}]

Prioritize pages likely to have contacts: /about, /contact, /team.""",
    tools=[scrape_website],
    output_key="scraped_data",
)

company_analyzer = LlmAgent(
    name="CompanyAnalyzer",
    model="gemini-2.5-flash",
    description="Deep-analyzes company websites for industry, size, and qualification signals.",
    instruction="""You are a business intelligence analyst. For each prospect:

1. Use analyze_company_website to detect:
   - Industry classification
   - Team size signals (hiring? employee count?)
   - Key pages (pricing, blog, careers)
   - Business model indicators

2. Store analysis in state. Format as JSON list:
   [{"company": "...", "url": "...", "industry": "...", "signals": {...}}]

Focus on signals that indicate the company is a GOOD FIT for outreach.""",
    tools=[analyze_company_website],
    output_key="company_analysis",
)

# PARALLEL: All 3 run at the same time
prospect_finder = ParallelAgent(
    name="ProspectFinder",
    description="Finds prospects from multiple sources simultaneously.",
    sub_agents=[google_searcher, web_scraper, company_analyzer],
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: LEAD ENRICHMENT
# Combines parallel results into unified lead profiles
# ═══════════════════════════════════════════════════════════════

lead_enricher = LlmAgent(
    name="LeadEnricher",
    model="gemini-2.5-flash",
    description="Combines data from all research agents into enriched lead profiles.",
    instruction="""You are a data fusion specialist. Your job is to combine the research 
from the 3 parallel agents into clean, enriched lead profiles.

INPUT (from state):
- google_prospects: URLs and companies from Google search
- scraped_data: Contact info scraped from websites
- company_analysis: Industry and business intelligence

YOUR JOB:
1. Merge data from all 3 sources by matching company URLs/names
2. Create a unified profile for each lead with:
   - company_name
   - website_url
   - industry
   - contact_emails (list)
   - contact_phones (list)
   - social_links
   - description (what they do)
   - team_size_signal
   - key_pages_found
   
3. Remove duplicates. Prioritize leads with contact info.
4. Output as JSON list of enriched leads.

Be thorough — every piece of data matters for personalization.""",
    output_key="enriched_leads",
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: PERSONALIZED OUTREACH
# Writes custom emails for each enriched lead
# ═══════════════════════════════════════════════════════════════

outreach_writer = LlmAgent(
    name="OutreachWriter",
    model="gemini-2.5-flash",
    description="Writes personalized cold outreach emails for each qualified lead.",
    instruction="""You are an expert cold email copywriter. For each enriched lead:

1. Read the enriched_leads from state
2. Write a PERSONALIZED cold email for each lead. Each email must:
   - Reference something specific about THEIR company (from description/industry)
   - Be under 150 words
   - Have a compelling subject line
   - Use the AIDA framework (Attention, Interest, Desire, Action)
   - End with a clear, low-friction CTA
   - Sound human, NOT like a template
   
3. Personalization signals to use:
   - Their industry → mention relevant pain points
   - Their team size → scale-appropriate solutions  
   - Their tech stack → integration possibilities
   - Their recent activity → timely outreach

4. Output as JSON list with:
   [{"company": "...", "email_to": "...", "subject": "...", "body": "..."}]

NEVER use generic templates. Every email must feel custom-written.
Use save_report to save all outreach emails to /tmp/leadgen-outreach.md""",
    tools=[save_report],
    output_key="outreach_emails",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: LEAD SCORING
# Scores and ranks leads, exports final CSV
# ═══════════════════════════════════════════════════════════════

lead_scorer = LlmAgent(
    name="LeadScorer",
    model="gemini-2.5-flash",
    description="Scores, ranks, and exports the final lead list.",
    instruction="""You are a lead scoring expert. Analyze all enriched leads and score them.

SCORING CRITERIA (0-100):
- Has direct email contact: +30 points
- Has phone number: +10 points
- Industry match quality: +20 points
- Company has pricing page (buying signals): +10 points
- Company is hiring (growth signal): +15 points
- Has social media presence: +5 points
- Website quality/completeness: +10 points

1. Read enriched_leads from state
2. Score each lead using the criteria above
3. Rank leads from highest to lowest score
4. Create a final CSV with columns:
   rank, company, url, industry, score, email, phone, outreach_subject
   
5. Use save_leads_csv to export to /tmp/leadgen-results.csv
6. Use save_report to write an executive summary to /tmp/leadgen-summary.md

The summary should include:
- Total leads found
- Score distribution
- Top 5 leads with reasoning
- Recommended next actions

This is the FINAL step — make the output actionable.""",
    tools=[save_leads_csv, save_report],
    output_key="final_scores",
)

# ═══════════════════════════════════════════════════════════════
# ROOT: SEQUENTIAL PIPELINE
# Chains all 4 steps in order
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="LeadGenPipeline",
    description="Full lead generation pipeline: parallel prospecting → enrichment → outreach → scoring.",
    sub_agents=[
        prospect_finder,    # Step 1: ParallelAgent (3 concurrent)
        lead_enricher,      # Step 2: Combines parallel results
        outreach_writer,    # Step 3: Personalized emails
        lead_scorer,        # Step 4: Score + export CSV
    ],
)
