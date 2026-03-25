"""
Code Auditor — Parallel Security + Performance + Quality Review
Uses ParallelAgent + SequentialAgent

Architecture:
  CodePipeline (Sequential)
    ├── CodeDiscoverer          → auto-discovers all code files in the project
    ├── AuditSwarm (Parallel)   → 3 reviewers analyze simultaneously
    │     ├── SecurityReviewer    — injection, secrets, auth, input validation
    │     ├── PerformanceReviewer — complexity, memory, queries, caching
    │     └── QualityReviewer     — naming, structure, duplication, docs
    ├── PriorityRanker          → ranks all findings by severity
    └── ReportGenerator         → generates actionable audit report

Auto-discovers code files — works on ANY codebase.

Example prompts:
  - "Audit ~/Documents/Fund_Dash for code quality"
  - "Review the security of ~/Documents/AutoStack/products/"
  - "Check ~/Documents/ADK Pipelines/leadgen for issues"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from codeauditor.tools.code_tools import (
    discover_codebase, read_code_file, save_audit_report
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: DISCOVER CODE
# ═══════════════════════════════════════════════════════════════

code_discoverer = LlmAgent(
    name="CodeDiscoverer",
    model="gemini-2.5-flash",
    description="Auto-discovers all code files in the target codebase.",
    instruction="""You discover all code files to audit.

1. Use discover_codebase with the directory the user specified
2. Review the file list — identify the largest/most complex files
3. Prioritize files for review (focus on the top 10-15 most important files)

Output the prioritized file list with paths and line counts.
The reviewers will use this list to read and audit the code.""",
    tools=[discover_codebase],
    output_key="codebase_map",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL REVIEW
# ═══════════════════════════════════════════════════════════════

security_reviewer = LlmAgent(
    name="SecurityReviewer",
    model="gemini-2.5-flash",
    description="Reviews code for security vulnerabilities.",
    instruction="""You are a security auditor. Read codebase_map from state.

For the top priority files:
1. Use read_code_file to read each file
2. Check for security issues:
   - Hardcoded secrets, API keys, passwords
   - SQL injection vulnerabilities
   - Command injection (os.system, subprocess with shell=True)
   - Path traversal (unsanitized file paths)
   - Missing input validation
   - Insecure HTTP requests (no SSL verification)
   - Cross-site scripting (XSS) in HTML
   - Missing authentication/authorization checks
   - Exposed debug endpoints

Rate each finding: CRITICAL / HIGH / MEDIUM / LOW
Output a structured security audit.""",
    tools=[read_code_file],
    output_key="security_findings",
)

performance_reviewer = LlmAgent(
    name="PerformanceReviewer",
    model="gemini-2.5-flash",
    description="Reviews code for performance issues.",
    instruction="""You are a performance engineer. Read codebase_map from state.

For the top priority files:
1. Use read_code_file to read each file
2. Check for performance issues:
   - O(n²) or worse algorithms (nested loops on large data)
   - N+1 query patterns (database queries in loops)
   - Missing caching opportunities
   - Large memory allocations
   - Synchronous operations that should be async
   - Redundant computations
   - Unbounded data loading (no pagination)
   - Missing connection pooling

Rate each finding: CRITICAL / HIGH / MEDIUM / LOW
Output a structured performance audit.""",
    tools=[read_code_file],
    output_key="performance_findings",
)

quality_reviewer = LlmAgent(
    name="QualityReviewer",
    model="gemini-2.5-flash",
    description="Reviews code for quality, maintainability, and best practices.",
    instruction="""You are a senior code reviewer. Read codebase_map from state.

For the top priority files:
1. Use read_code_file to read each file
2. Check for quality issues:
   - Poor naming (unclear variables, functions)
   - Long functions (>50 lines)
   - Code duplication
   - Missing error handling (bare except, missing try/catch)
   - Missing docstrings/comments on complex logic
   - Dead code or unused imports
   - Inconsistent coding style
   - Missing type hints (Python)
   - Complex conditionals (>3 nested levels)

Rate each finding: CRITICAL / HIGH / MEDIUM / LOW
Output a structured quality audit.""",
    tools=[read_code_file],
    output_key="quality_findings",
)

audit_swarm = ParallelAgent(
    name="AuditSwarm",
    description="Security, performance, and quality reviewers work simultaneously.",
    sub_agents=[security_reviewer, performance_reviewer, quality_reviewer],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: PRIORITY RANKING
# ═══════════════════════════════════════════════════════════════

priority_ranker = LlmAgent(
    name="PriorityRanker",
    model="gemini-2.5-flash",
    description="Ranks all findings by severity and impact.",
    instruction="""You rank all audit findings by priority.

Read: security_findings, performance_findings, quality_findings from state.

1. Merge all findings into a single ranked list
2. Priority order: Security CRITICAL > Performance CRITICAL > Quality CRITICAL > ...
3. Group by file so fixes can be batched
4. Estimate effort for each fix (quick/medium/complex)

Output a prioritized fix list with:
- Rank, category, severity, file, description, suggested fix, effort""",
    output_key="priority_list",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: GENERATE REPORT
# ═══════════════════════════════════════════════════════════════

report_generator = LlmAgent(
    name="AuditReportGenerator",
    model="gemini-2.5-flash",
    description="Generates the final code audit report.",
    instruction="""You generate the final code audit report.

Use save_audit_report to write:
- /tmp/codeauditor-report.md — full audit report:
  - Executive summary (total issues, scores per category)
  - Security score (0-100)
  - Performance score (0-100)
  - Quality score (0-100)
  - Overall score (weighted average)
  - Top 10 priority fixes
  - Full findings by category
  - Recommended action plan

- /tmp/codeauditor-fixes.md — just the prioritized fix list for devs

Every finding must have a concrete fix suggestion with code examples.""",
    tools=[save_audit_report],
    output_key="audit_report",
)

# ═══════════════════════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="CodePipeline",
    description="Code audit: discover files → parallel review (security + performance + quality) → rank → report.",
    sub_agents=[code_discoverer, audit_swarm, priority_ranker, report_generator],
)
