"""
Product Launch Engine — Build Products with Parallel Workstreams
Uses ParallelAgent + SequentialAgent

Architecture:
  ProductPipeline (Sequential)
    ├── ProductPlanner         → discovers product scope, features, audience
    ├── BuildSwarm (Parallel)  → 3 builders work simultaneously
    │     ├── CodeBuilder        — builds the product code/templates
    │     ├── CopyWriter         — writes sales page, README, marketing copy
    │     └── DocsBuilder        — writes user docs, setup guide, FAQ
    ├── QualityReviewer        → reviews all outputs for quality
    └── PackagePublisher       → packages everything for Gumroad/delivery

Auto-discovers product scope — works for ANY digital product.

Example prompts:
  - "Build an AI chatbot starter kit for small businesses"
  - "Create a financial literacy course package for veterans"
  - "Build an SEO audit template kit"
"""

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent

from productlaunch.tools.product_tools import (
    save_product_file, list_product_files, read_file
)

# ═══════════════════════════════════════════════════════════════
# STEP 1: PRODUCT PLANNING
# ═══════════════════════════════════════════════════════════════

product_planner = LlmAgent(
    name="ProductPlanner",
    model="gemini-2.5-flash",
    description="Plans the product scope, features, and structure.",
    instruction="""You are a product manager. Based on the user's prompt:

1. Define the product:
   - Name and tagline
   - Target audience
   - Problem it solves
   - Key features (3-5)
   - Pricing suggestion

2. Define the deliverables:
   - Code/template files needed
   - Sales copy needed
   - Documentation needed
   - Bonus materials (if applicable)

3. Set the output directory: /tmp/productlaunch-[product-slug]/

Output a JSON product plan that the builders will follow.""",
    output_key="product_plan",
)

# ═══════════════════════════════════════════════════════════════
# STEP 2: PARALLEL BUILDING
# ═══════════════════════════════════════════════════════════════

code_builder = LlmAgent(
    name="CodeBuilder",
    model="gemini-2.5-flash",
    description="Builds the product code, templates, or tools.",
    instruction="""You build the core product deliverables.

Read product_plan from state. Based on the product type, create:
- Scripts, templates, or tools (the actual product)
- Configuration files
- Example files showing how to use the product

Use save_product_file to save each file to the product directory.
Make the code production-quality — this is what customers pay for.""",
    tools=[save_product_file],
    output_key="code_output",
)

copy_writer = LlmAgent(
    name="CopyWriter",
    model="gemini-2.5-flash",
    description="Writes the sales page, README, and marketing copy.",
    instruction="""You write all marketing and sales materials.

Read product_plan from state. Create:
- SALES_PAGE.md — Gumroad product description with benefits, features,
  social proof placeholders, pricing, and call-to-action
- README.md — product overview for buyers (what's included, how it works)

Use save_product_file to save to the product directory.
Write copy that converts — focus on benefits, not features.""",
    tools=[save_product_file],
    output_key="copy_output",
)

docs_builder = LlmAgent(
    name="DocsBuilder",
    model="gemini-2.5-flash",
    description="Writes user documentation, setup guide, and FAQ.",
    instruction="""You write all user-facing documentation.

Read product_plan from state. Create:
- SETUP.md — step-by-step setup guide (assume non-technical user)
- FAQ.md — 10 common questions and answers
- CHANGELOG.md — version 1.0 release notes

Use save_product_file to save to the product directory.
Keep docs clear, concise, and jargon-free.""",
    tools=[save_product_file],
    output_key="docs_output",
)

build_swarm = ParallelAgent(
    name="BuildSwarm",
    description="Code, copy, and docs built simultaneously.",
    sub_agents=[code_builder, copy_writer, docs_builder],
)

# ═══════════════════════════════════════════════════════════════
# STEP 3: QUALITY REVIEW
# ═══════════════════════════════════════════════════════════════

quality_reviewer = LlmAgent(
    name="QualityReviewer",
    model="gemini-2.5-flash",
    description="Reviews all product outputs for quality and completeness.",
    instruction="""You review the entire product package.

Read code_output, copy_output, docs_output from state.

Check:
1. Code quality — is it production-ready? Any bugs or missing features?
2. Sales copy — is it compelling? Does it clearly state the value prop?
3. Documentation — is it complete? Could a non-tech user follow it?
4. Consistency — do all files reference each other correctly?
5. Completeness — is anything missing from the product plan?

Use list_product_files to verify all planned files were created.

Output a quality report with scores and recommended fixes.""",
    tools=[list_product_files, read_file],
    output_key="quality_review",
)

# ═══════════════════════════════════════════════════════════════
# STEP 4: PACKAGE
# ═══════════════════════════════════════════════════════════════

package_publisher = LlmAgent(
    name="PackagePublisher",
    model="gemini-2.5-flash",
    description="Finalizes the product package and generates launch report.",
    instruction="""You finalize the product for launch.

Use save_product_file to write:
- /tmp/productlaunch-summary.md — launch checklist:
  - All files created (with paths)
  - Quality review status
  - Gumroad listing instructions
  - Pricing recommendation
  - Marketing plan (social posts, email announcement)

This is the final step — make the launch actionable.""",
    tools=[save_product_file],
    output_key="launch_summary",
)

# ═══════════════════════════════════════════════════════════════
# ROOT
# ═══════════════════════════════════════════════════════════════

root_agent = SequentialAgent(
    name="ProductPipeline",
    description="Product launch: plan → parallel build (code + copy + docs) → quality review → package.",
    sub_agents=[product_planner, build_swarm, quality_reviewer, package_publisher],
)
