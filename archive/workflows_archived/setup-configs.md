---
description: Create all configuration YAML files for the swarm — niche targeting, posting schedule, agent settings, and MCP server configs.
---

# Setup Configs Workflow

## Steps

### 1. Create niche.yaml

```bash
cat > ~/Documents/Free_Cash_Flow/config/niche.yaml << 'EOF'
research:
  primary_niche: "AI agents and automation"
  secondary_niches:
    - "no-code AI tools"
    - "AI side hustles"
    - "prompt engineering"
    - "AI productivity hacks"
    - "autonomous AI systems"
  topic_weights:
    ai_agents: 1.0
    automation: 0.9
    side_hustles: 0.8
    prompt_engineering: 0.7
    productivity: 0.6
  banned_topics:
    - "crypto scams"
    - "get-rich-quick schemes"
    - "MLM"
    - "gambling"
  min_trend_score: 7
  max_topics_per_day: 3

content:
  voice: "friendly"
  tone: "direct, numbers-driven, no-fluff"
  target_audience:
    - "solopreneurs"
    - "AI builders"
    - "tech-savvy side hustlers"
  content_pillars:
    - "AI automation tutorials"
    - "Money-making with AI"
    - "Tool reviews and comparisons"
    - "Behind-the-scenes of the swarm"
EOF
```

### 2. Create schedule.yaml

```bash
cat > ~/Documents/Free_Cash_Flow/config/schedule.yaml << 'EOF'
daily:
  research:
    time: "09:00"
    timezone: "US/Eastern"
    agents: ["gpt_researcher", "brave_search_agent", "marvin_agent"]

  video_generation:
    - time: "10:00"
      type: "primary_video"
    - time: "16:00"
      type: "secondary_video"

  humanization:
    time: "11:00"
    agent: "human_voice_engine"
    stages: ["detox", "personality", "chaos", "voice_lock", "verify"]

  posting:
    - time: "12:00"
      type: "video"
      source: "primary_video"
    - time: "14:00"
      type: "thread"
      source: "research_data"
    - time: "18:00"
      type: "video"
      source: "secondary_video"

  engagement:
    frequency_hours: 2
    start_time: "09:00"
    end_time: "22:00"
    max_replies_per_session: 5
    agents: ["growth_agent", "beeai_agent"]

  self_learning:
    time: "23:30"
    agents: ["self_learning", "mindsdb_agent", "langgraph_agent"]
    actions: ["collect_metrics", "analyze", "micro_adjust", "save_report"]

  newsletter:
    time: "23:45"
    recipient: "hernandezeslyn@gmail.com"
    style: "friendly"
    agents: ["self_learning", "slack_agent"]

  notifications:
    time: "23:50"
    agent: "slack_agent"
    type: "daily_summary"

weekly:
  product_creation:
    day: "monday"
    time: "10:00"
    agents: ["product_agent", "llamaindex_agent", "notion_agent"]

  deep_review:
    day: "sunday"
    time: "00:00"
    agents: ["self_learning", "mindsdb_agent", "langgraph_agent", "slack_agent"]
    actions: ["macro_adjust", "strategy_shift", "voice_calibration"]

  product_promotion:
    day: "wednesday"
    time: "14:00"
    type: "product_promo_thread"
EOF
```

### 3. Create agents.yaml

```bash
cat > ~/Documents/Free_Cash_Flow/config/agents.yaml << 'EOF'
# === Tier 1: Content Pipeline Agents ===
content_agents:
  researcher:
    repo: "agents/researcher"
    type: "gpt-researcher"
    enabled: true
    config:
      model: "gpt-4"
      max_search_results: 10
      report_type: "research_report"

  video:
    repo: "agents/video"
    type: "faceless-video-generator"
    enabled: true
    config:
      resolution: "1080x1920"
      duration_target: 60
      voice_provider: "elevenlabs"
      voice_id: "adam"

  product:
    repo: "agents/product"
    type: "ebook-generator"
    enabled: true
    config:
      model: "gemini-pro"
      default_chapters: 8
      default_format: "pdf"

  twitter:
    repo: "agents/twitter"
    type: "dot-automation"
    enabled: true
    config:
      posts_per_day: 3
      max_thread_length: 8

  growth:
    repo: "agents/growth"
    type: "xgrow"
    enabled: true
    config:
      max_replies_per_hour: 5
      news_posts_per_day: 2

# === Tier 2: MCP Agents ===
mcp_agents:
  slack:
    package: "@modelcontextprotocol/server-slack"
    requires: ["SLACK_BOT_TOKEN", "SLACK_TEAM_ID"]
    enabled: true
    
  brave_search:
    package: "@modelcontextprotocol/server-brave-search"
    requires: ["BRAVE_API_KEY"]
    enabled: true

  notion:
    package: "@notionhq/notion-mcp-server"
    requires: ["NOTION_API_KEY"]
    enabled: true

  github:
    package: "@modelcontextprotocol/server-github"
    requires: ["GITHUB_PERSONAL_ACCESS_TOKEN"]
    enabled: true

  postgres:
    package: "@modelcontextprotocol/server-postgres"
    requires: ["DATABASE_URL"]
    enabled: false  # Enable when DB is set up

  puppeteer:
    package: "@modelcontextprotocol/server-puppeteer"
    requires: []
    enabled: true

  filesystem:
    package: "@modelcontextprotocol/server-filesystem"
    requires: []
    enabled: true

  sqlite:
    package: "@modelcontextprotocol/server-sqlite"
    requires: []
    enabled: true

  memory:
    package: "@modelcontextprotocol/server-memory"
    requires: []
    enabled: true

# === Tier 3: A2A Agents ===
a2a_agents:
  langgraph:
    type: "langgraph"
    enabled: true
    tools: ["langgraph_workflow", "langgraph_conditional"]

  llamaindex:
    type: "llamaindex"
    enabled: true
    tools: ["llamaindex_parse_and_chat", "llamaindex_summarize", "llamaindex_multi_doc_query"]

  ag2:
    type: "ag2"
    enabled: true
    tools: ["ag2_debate", "ag2_code_review"]

  semantic_kernel:
    type: "semantic_kernel"
    enabled: true
    tools: ["semantic_kernel_plan", "semantic_kernel_transform"]

  marvin:
    type: "marvin"
    enabled: true
    tools: ["marvin_extract", "marvin_classify", "marvin_extract_from_file"]

  mindsdb:
    type: "mindsdb"
    enabled: true
    tools: ["mindsdb_query_natural", "mindsdb_explain_data"]

  beeai:
    type: "beeai"
    enabled: true
    tools: ["beeai_chat", "beeai_roleplay"]

# === Tier 4: Core Agents ===
core_agents:
  agent_zero:
    url: "http://localhost:50001"
    type: "agent-zero"
    enabled: true

  crew_ai:
    type: "crewai"
    enabled: true

# === System ===
system:
  human_voice_engine:
    enabled: true
    max_ai_detection_score: 0.05  # < 5% AI probability. Non-negotiable.
    aggressiveness: 0.9

  newsletter:
    enabled: true
    recipient: "hernandezeslyn@gmail.com"
    time: "23:45"
    style: "friendly"
    
orchestrator:
  swarm_enabled: true
  kill_switch: false
  log_level: "INFO"
  metrics_retention_days: 90
EOF
```

### 4. Create .env.example

```bash
cat > ~/Documents/Free_Cash_Flow/config/.env.example << 'EOF'
# === Required API Keys ===
OPENAI_API_KEY=
GOOGLE_API_KEY=
TAVILY_API_KEY=

# === Twitter/X API ===
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_BEARER_TOKEN=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=

# === Monetization ===
GUMROAD_ACCESS_TOKEN=

# === MCP Services ===
SLACK_BOT_TOKEN=
SLACK_TEAM_ID=
BRAVE_API_KEY=
NOTION_API_KEY=
GITHUB_PERSONAL_ACCESS_TOKEN=
DATABASE_URL=

# === Optional ===
ELEVENLABS_API_KEY=
PEXELS_API_KEY=

# === Email Newsletter ===
SMTP_FROM=swarm@freecashflow.ai
GMAIL_USER=hernandezeslyn@gmail.com
GMAIL_APP_PASSWORD=
SENDGRID_API_KEY=
NEWSLETTER_RECIPIENT=hernandezeslyn@gmail.com

# === System ===
SWARM_ENABLED=true
TWITTER_ENABLED=true
LOG_LEVEL=INFO
EOF
```

### 5. Create MCP config (mcp_config.json)

```bash
cat > ~/Documents/Free_Cash_Flow/config/mcp_config.json << 'EOF'
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      }
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    },
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer ${NOTION_API_KEY}\", \"Notion-Version\": \"2022-06-28\"}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "~/Documents/Free_Cash_Flow"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "~/Documents/Free_Cash_Flow/data/metrics.db"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
EOF
```

## Verification

- [ ] `config/niche.yaml` exists and is valid YAML
- [ ] `config/schedule.yaml` exists and references all agent tiers
- [ ] `config/agents.yaml` lists all 24 agents across 4 tiers
- [ ] `config/.env.example` includes all MCP service keys
- [ ] `config/.env` exists with real keys filled in
- [ ] `config/mcp_config.json` has all 9 MCP server configs
