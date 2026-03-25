"""
Site Audit Pipeline — Full QA for Any Website
Uses ParallelAgent + SequentialAgent

Architecture:
  SiteAuditPipeline (Sequential)
    ├── PageDiscoverer      → auto-discovers all pages from URL or sitemap
    ├── AuditSwarm (Parallel) → 5 audit angles run simultaneously
    │     ├── SEOAuditor      — meta tags, headings, schema, keywords
    │     ├── LinkChecker     — broken links, redirects, external links
    │     ├── FormatAuditor   — CSS, inline styles, HTML structure
    │     ├── ScriptAuditor   — JS errors, performance, console issues
    │     └── ContentAuditor  — word count, readability, CTAs
    ├── ResultsMerger       → combines all audit results per page
    └── ReportGenerator     → scores, ranks, exports CSV + report

Auto-discovers pages — works on ANY site, any number of pages.

Example prompts:
  - "Audit sirmiumcapital.com"
  - "Check https://nyc-honor.netlify.app for SEO issues"
  - "Full QA on autostack.dev"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from siteaudit.tools.audit_tools import (
    discover_pages, audit_seo, check_links, audit_format, audit_content
)
from siteaudit.tools.output_tools import save_audit_csv, save_report

# ═══════════════════════════════════════════════════════════════
# STEP 1: AUTO-DISCOVER PAGES
# ═══════════════════════════════════════════════════════════════

page_discoverer = LlmAgent(
    name="PageDiscoverer",
    model="gemini-2.5-flash",
    description="Auto-discovers all pages on a website from sitemap or crawling.",
    instruction="""You discover all pages on a website.

1. Use discover_pages with the URL the user provided
2. The tool will check sitemap.xml first, then crawl internal links
3. Store the full list of discovered pages in state

Output the complete list of page URLs found.
This is critical — all other agents depend on this list.""",
    tools=[discover_pages],
    output_key="discovered_pages",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL AUDIT (5 angles simultaneously)
# ═══════════════════════════════════════════════════════════════

seo_auditor = LlmAgent(
    name="SEOAuditor",
    model="gemini-2.5-flash",
    description="Audits every discovered page for SEO quality.",
    instruction="""You are an SEO specialist. Read the discovered_pages from state.

For each page URL:
1. Use audit_seo to check title, meta description, headings, images, schema
2. Record the SEO score and all issues found

Output a JSON list of SEO audit results for every page.
Include the score and issues for each URL.""",
    tools=[audit_seo],
    output_key="seo_results",
)

link_checker = LlmAgent(
    name="LinkChecker",
    model="gemini-2.5-flash",
    description="Checks all links on every discovered page.",
    instruction="""You are a link validation specialist. Read the discovered_pages from state.

For each page URL:
1. Use check_links to find broken links, external links, and mail links
2. Flag any broken links as critical issues

Output a JSON list of link check results for every page.
Broken links are HIGH PRIORITY issues.""",
    tools=[check_links],
    output_key="link_results",
)

format_auditor = LlmAgent(
    name="FormatAuditor",
    model="gemini-2.5-flash",
    description="Audits HTML structure, inline styles, heading hierarchy, and accessibility.",
    instruction="""You are a frontend quality specialist. Read the discovered_pages from state.

For each page URL:
1. Use audit_format to check inline styles, heading hierarchy, viewport, lang, forms
2. Flag inline styles and accessibility issues

Output a JSON list of format audit results for every page.""",
    tools=[audit_format],
    output_key="format_results",
)

script_auditor = LlmAgent(
    name="ScriptAuditor",
    model="gemini-2.5-flash",
    description="Analyzes page performance, script loading, and potential JS issues.",
    instruction="""You are a performance analyst. Read the discovered_pages from state.

For each page URL, analyze the SEO and format data already collected by
your sibling agents. Since we can't execute JavaScript in our tools,
focus on:
1. Identifying pages with excessive inline styles (from format_results)
2. Cross-referencing SEO and format issues to find systemic problems
3. Noting pages that are missing critical meta tags AND have format issues

Output a summary of cross-cutting quality concerns across all pages.""",
    output_key="script_results",
)

content_auditor = LlmAgent(
    name="ContentAuditor",
    model="gemini-2.5-flash",
    description="Audits content quality: word count, readability, CTAs, structure.",
    instruction="""You are a content quality specialist. Read the discovered_pages from state.

For each page URL:
1. Use audit_content to check word count, readability, paragraphs, CTAs
2. Flag thin content and missing calls-to-action

Output a JSON list of content audit results for every page.""",
    tools=[audit_content],
    output_key="content_results",
)

# PARALLEL: All 5 auditors run at the same time
audit_swarm = ParallelAgent(
    name="AuditSwarm",
    description="Runs 5 audit agents simultaneously on all discovered pages.",
    sub_agents=[seo_auditor, link_checker, format_auditor, script_auditor, content_auditor],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: MERGE RESULTS
# ═══════════════════════════════════════════════════════════════

results_merger = LlmAgent(
    name="ResultsMerger",
    model="gemini-2.5-flash",
    description="Combines all audit results into a unified per-page report.",
    instruction="""You combine results from all 5 audit agents into a unified view.

INPUT (from state):
- seo_results: SEO scores and issues per page
- link_results: broken/external links per page
- format_results: inline styles, heading issues per page
- script_results: cross-cutting quality concerns
- content_results: word count, readability per page

YOUR JOB:
1. Merge all results by URL into a unified per-page profile
2. Calculate an OVERALL SCORE per page (0-100):
   - SEO: 30% weight
   - Links: 20% weight
   - Format: 20% weight
   - Content: 20% weight
   - Cross-cutting: 10% weight
3. Determine PASS/FAIL per page (70+ = PASS)
4. Rank pages from worst to best

Output a JSON list of unified page results with overall scores.""",
    output_key="merged_results",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: GENERATE REPORT
# ═══════════════════════════════════════════════════════════════

report_generator = LlmAgent(
    name="ReportGenerator",
    model="gemini-2.5-flash",
    description="Generates the final audit report and exports CSV.",
    instruction="""You generate the final audit report.

1. Read merged_results from state
2. Use save_audit_csv to export per-page scores to /tmp/siteaudit-results.csv
   Columns: url, overall_score, seo_score, link_issues, format_issues, content_score, pass_fail
3. Use save_report to write a full markdown report to /tmp/siteaudit-report.md

The report must include:
- Executive summary (total pages, pass rate, overall grade)
- Top issues across the site (ranked by frequency/severity)
- Per-page breakdown with scores
- Recommended priority fixes (top 10 action items)
- Pass/fail deployment gate (if >20% pages fail → FAIL site)

Make the report actionable. Every issue should have a clear fix.""",
    tools=[save_audit_csv, save_report],
    output_key="final_report",
)

# ═══════════════════════════════════════════════════════════════
# ROOT: SEQUENTIAL PIPELINE
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="SiteAuditPipeline",
    description="Full site QA pipeline: auto-discover pages → parallel 5-angle audit → merge → report.",
    sub_agents=[
        page_discoverer,    # Step 1: Find all pages
        audit_swarm,        # Step 2: 5 auditors in parallel
        results_merger,     # Step 3: Combine results
        report_generator,   # Step 4: Export CSV + report
    ],
)
