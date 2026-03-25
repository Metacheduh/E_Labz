"""
Email Campaign Engine — Write 3 Nurture Sequences in Parallel
Uses ParallelAgent + SequentialAgent

Architecture:
  EmailPipeline (Sequential)
    ├── AudienceResearcher     → discovers audience segments from the prompt
    ├── SequenceSwarm (Parallel) → 3 writers produce 3 email sequences
    │     ├── SequenceWriter_1   — warm intro / awareness sequence
    │     ├── SequenceWriter_2   — value / education sequence
    │     └── SequenceWriter_3   — conversion / close sequence
    ├── ComplianceChecker      → SEC/FINRA/CAN-SPAM review of all emails
    └── CampaignPublisher      → saves sequences + compliance report

Auto-discovers audience segments — works for ANY business.

Example prompts:
  - "Write email sequences for 9/11 families about VCF claims"
  - "Create nurture emails for AI automation prospects"
  - "Build an email campaign for veterans retirement planning"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from emailcampaign.tools.email_tools import (
    save_email_sequence, check_compliance, save_report
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: AUDIENCE RESEARCH
# ═══════════════════════════════════════════════════════════════

audience_researcher = LlmAgent(
    name="AudienceResearcher",
    model="gemini-2.5-flash",
    description="Discovers audience segments and defines the email campaign strategy.",
    instruction="""You are an email marketing strategist. Based on the user's prompt:

1. Identify the target audience and their pain points
2. Define 3 email sequences that form a complete nurture funnel:
   - Sequence 1: AWARENESS (3-4 emails) — introduce the problem, establish trust
   - Sequence 2: EDUCATION (3-4 emails) — provide value, teach, share expertise
   - Sequence 3: CONVERSION (3-4 emails) — case studies, urgency, call to action

3. For each sequence, define:
   - Target persona
   - Goal of the sequence
   - Subject line themes
   - Sending cadence (e.g., every 3 days)

Output a JSON strategy document that the writers will follow.""",
    output_key="campaign_strategy",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL WRITING (3 sequences at once)
# ═══════════════════════════════════════════════════════════════

def _make_sequence_writer(n, stage, description):
    return LlmAgent(
        name=f"SequenceWriter_{n}",
        model="gemini-2.5-flash",
        description=f"Writes the {stage} email sequence.",
        instruction=f"""You write the {stage} email sequence (Sequence #{n}).

Read the campaign_strategy from state and follow the strategy for sequence {n}.

Write 3-4 emails for this sequence. Each email must include:
- Subject line (compelling, under 50 chars)
- Preview text (40-90 chars)
- Body (conversational, 150-300 words)
- Call-to-action (clear, single action)
- P.S. line (optional but recommended)

RULES:
- Never make performance guarantees (SEC compliance)
- Every email needs an [Unsubscribe] placeholder
- Include [Company Address] placeholder
- Tone: {description}
- Include personalization tokens: [First Name], [Company]

Use save_email_sequence to save to /tmp/emailcampaign-sequence-{n}.md""",
        tools=[save_email_sequence],
        output_key=f"sequence_{n}",
    )

writer_1 = _make_sequence_writer(1, "AWARENESS", "warm, empathetic, educational — build trust")
writer_2 = _make_sequence_writer(2, "EDUCATION", "authoritative, helpful, data-driven — provide value")
writer_3 = _make_sequence_writer(3, "CONVERSION", "confident, social-proof-heavy, clear CTA — close the deal")

sequence_swarm = ParallelAgent(
    name="SequenceSwarm",
    description="3 writers produce 3 email sequences simultaneously.",
    sub_agents=[writer_1, writer_2, writer_3],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: COMPLIANCE CHECK
# ═══════════════════════════════════════════════════════════════

compliance_checker = LlmAgent(
    name="ComplianceChecker",
    model="gemini-2.5-flash",
    description="Reviews all email sequences for SEC/FINRA/CAN-SPAM compliance.",
    instruction="""You are a compliance reviewer. Read all 3 sequences from state.

For each email in each sequence:
1. Use check_compliance to scan for regulatory issues
2. Flag any SEC/FINRA violations (performance guarantees, misleading claims)
3. Check CAN-SPAM (unsubscribe link, physical address)
4. Review for spam trigger words

Output a compliance report with:
- PASS/FAIL for each email
- Specific issues found
- Recommended fixes
- Overall campaign compliance score""",
    tools=[check_compliance],
    output_key="compliance_results",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: PUBLISH
# ═══════════════════════════════════════════════════════════════

campaign_publisher = LlmAgent(
    name="CampaignPublisher",
    model="gemini-2.5-flash",
    description="Generates the final campaign package.",
    instruction="""You finalize the email campaign package.

1. Read all sequences and compliance results from state
2. Use save_report to write:
   - /tmp/emailcampaign-report.md — full campaign plan with sending schedule,
     compliance status, and all email copies
   - /tmp/emailcampaign-summary.md — executive summary of the campaign

The report must include:
- Campaign overview (audience, goal, timeline)
- Sending calendar (which emails go out when)
- Compliance status per email
- Recommended A/B test variations for subject lines""",
    tools=[save_report],
    output_key="campaign_final",
)

# ═══════════════════════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="EmailPipeline",
    description="Email campaign: audience research → write 3 sequences in parallel → compliance check → publish.",
    sub_agents=[
        audience_researcher,
        sequence_swarm,
        compliance_checker,
        campaign_publisher,
    ],
)
