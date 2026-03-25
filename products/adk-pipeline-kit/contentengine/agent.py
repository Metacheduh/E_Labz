"""
Content Marketing Engine — Write Multiple Blog Posts in Parallel
Uses ParallelAgent + SequentialAgent

Architecture:
  ContentPipeline (Sequential)
    ├── TopicResearcher     → discovers trending topics in the niche
    ├── ContentSwarm (Parallel) → 5 writers produce 5 posts simultaneously
    │     ├── Writer_1
    │     ├── Writer_2
    │     ├── Writer_3
    │     ├── Writer_4
    │     └── Writer_5
    ├── SEOOptimizer        → audits all posts for SEO quality
    └── Publisher            → saves all posts to disk + summary

Auto-discovers topics — works for ANY niche.

Example prompts:
  - "Write 5 blog posts about VCF claims for 9/11 families"
  - "Create content about AI automation for small businesses"
  - "Write articles about retirement planning for veterans"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from contentengine.tools.content_tools import (
    search_trending_topics, analyze_competitor_content, save_article, save_report
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: RESEARCH TOPICS
# ═══════════════════════════════════════════════════════════════

topic_researcher = LlmAgent(
    name="TopicResearcher",
    model="gemini-2.5-flash",
    description="Researches trending topics and content gaps in the target niche.",
    instruction="""You are a content strategist. When given a niche or topic area:

1. Use search_trending_topics with multiple queries:
   - "[niche] blog topics 2026"
   - "[niche] frequently asked questions"
   - "[niche] guides and tutorials"
   - "best [niche] articles"

2. Use analyze_competitor_content on the top 3-5 results to see what's already published

3. Based on your research, generate EXACTLY 5 unique blog post topics that:
   - Fill content gaps (topics competitors haven't covered well)
   - Answer real questions people are searching for
   - Have strong SEO potential
   - Are specific enough to be actionable

Output a JSON list of 5 topics, each with:
  {"topic_number": 1, "title": "...", "target_keyword": "...", "outline": ["H2 sections..."], "word_target": 1200}""",
    tools=[search_trending_topics, analyze_competitor_content],
    output_key="topics",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL WRITING (5 writers at once)
# ═══════════════════════════════════════════════════════════════

def _make_writer(n):
    return LlmAgent(
        name=f"Writer_{n}",
        model="gemini-2.5-flash",
        description=f"Writes blog post #{n} from the researched topics.",
        instruction=f"""You are an expert blog writer. Read the topics from state.

Find topic #{n} from the topics list and write a complete blog post.

REQUIREMENTS:
- Title: use the exact title from the topic
- Length: match the word_target (usually 1000-1500 words)
- Structure: use the outline headings as H2 sections
- SEO: naturally include the target_keyword 3-5 times
- Tone: professional but approachable, not salesy
- Format: clean markdown with proper headings
- Include: an introduction, body sections, and conclusion
- Add: a compelling meta description (150 chars max)
- End with: a clear call-to-action

Output the FULL blog post in markdown format.
Start with the meta description on line 1 as a comment.
Use save_article to save to /tmp/contentengine-post-{n}.md""",
        tools=[save_article],
        output_key=f"post_{n}",
    )

writer_1 = _make_writer(1)
writer_2 = _make_writer(2)
writer_3 = _make_writer(3)
writer_4 = _make_writer(4)
writer_5 = _make_writer(5)

# PARALLEL: All 5 writers work at the same time
content_swarm = ParallelAgent(
    name="ContentSwarm",
    description="5 writers produce 5 blog posts simultaneously.",
    sub_agents=[writer_1, writer_2, writer_3, writer_4, writer_5],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: SEO OPTIMIZATION
# ═══════════════════════════════════════════════════════════════

seo_optimizer = LlmAgent(
    name="SEOOptimizer",
    model="gemini-2.5-flash",
    description="Reviews all 5 posts for SEO quality and suggests improvements.",
    instruction="""You are an SEO editor. Read all 5 posts from state (post_1 through post_5).

For each post, evaluate:
1. Title tag quality (compelling, keyword-rich, 50-60 chars)
2. Meta description quality (actionable, 120-155 chars)
3. Keyword usage (natural, 3-5 mentions, in H2s)
4. Heading structure (H1 → H2 → H3, logical flow)
5. Internal linking opportunities (suggest where to link between the 5 posts)
6. Readability (short paragraphs, bullet points, scannable)

Output a JSON list with SEO scores and recommendations for each post.
Score each post 0-100 on SEO readiness.""",
    output_key="seo_review",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: PUBLISH + SUMMARY
# ═══════════════════════════════════════════════════════════════

publisher = LlmAgent(
    name="Publisher",
    model="gemini-2.5-flash",
    description="Generates the final content calendar and summary report.",
    instruction="""You are a content manager. Your job is to finalize the content package.

1. Read all posts and SEO reviews from state
2. Use save_report to write a content calendar to /tmp/contentengine-calendar.md:
   - List all 5 posts with suggested publish dates (weekly schedule)
   - Include SEO scores
   - Note any posts that need revision based on SEO review
   - Suggest social media captions for each post

3. Use save_report to write an executive summary to /tmp/contentengine-summary.md:
   - Topics covered
   - Total word count across all posts
   - Average SEO score
   - Publishing schedule
   - Recommended next steps

This is the final step — make everything actionable and ready to publish.""",
    tools=[save_report],
    output_key="publish_summary",
)

# ═══════════════════════════════════════════════════════════════
# ROOT: SEQUENTIAL PIPELINE
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="ContentPipeline",
    description="Content marketing pipeline: research topics → write 5 posts in parallel → SEO audit → publish.",
    sub_agents=[
        topic_researcher,   # Step 1: Discover topics
        content_swarm,      # Step 2: 5 writers in parallel
        seo_optimizer,      # Step 3: SEO review
        publisher,          # Step 4: Calendar + summary
    ],
)
