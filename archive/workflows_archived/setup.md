---
description: Set up the complete Free Cash Flow swarm from scratch — clone agents, install dependencies, configure API keys, connect MCP + A2A agents, and verify everything works.
---

# Initial Setup Workflow

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed (for MCP servers)
- Git installed
- Docker installed (for Agent Zero)
- API keys for: OpenAI, Google Gemini, Twitter/X, Gumroad, Brave Search, Slack, Notion, GitHub

## Steps

### 1. Create project structure

```bash
cd ~/Documents/Free_Cash_Flow
mkdir -p agents orchestrator output/{videos,products,research,tweets,metrics} config data/{performance,templates,knowledge} tests
```

### 2. Clone all 5 content pipeline agent repos

```bash
cd ~/Documents/Free_Cash_Flow/agents
git clone --depth 1 https://github.com/assafelovic/gpt-researcher.git researcher
git clone --depth 1 https://github.com/jacky-xbb/faceless-video-generator.git video
git clone --depth 1 https://github.com/UltronTheAI/eBook-Generator-AI-Agent.git product
git clone --depth 1 https://github.com/pippinlovesdot/dot-automation.git twitter
git clone --depth 1 https://github.com/wassim249/xgrow.git growth
```

### 3. Create Python virtual environment

```bash
cd ~/Documents/Free_Cash_Flow
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 4. Install core dependencies

```bash
pip install google-adk google-genai structlog pyyaml schedule python-dotenv requests
```

### 5. Install each content agent's dependencies

```bash
cd agents/researcher && pip install -r requirements.txt && cd ../..
cd agents/video && pip install -r requirements.txt && cd ../..
cd agents/product && pip install -r requirements.txt && cd ../..
cd agents/twitter && pip install -r requirements.txt && cd ../..
cd agents/growth && pip install -r requirements.txt && cd ../..
```

### 6. Install A2A SDK + A2A agent dependencies

```bash
pip install a2a-sdk crewai langgraph llama-index ag2 semantic-kernel marvin mindsdb-sdk beeai
```

### 7. Install MCP servers (Node.js)

```bash
npm install -g @modelcontextprotocol/server-slack
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @notionhq/notion-mcp-server
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-postgres
npm install -g @modelcontextprotocol/server-puppeteer
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-sqlite
npm install -g @modelcontextprotocol/server-memory
```

### 8. Create .env file

```bash
cp config/.env.example config/.env
# Edit config/.env and fill in ALL API keys
```

### 9. Create configuration files

Run `/setup-configs` workflow to create `agents.yaml`, `schedule.yaml`, `niche.yaml`, and `mcp_config.json`.

### 10. Start Agent Zero (Docker)

```bash
docker pull frdel/agent-zero
docker run -d --name agent-zero -p 50001:50001 frdel/agent-zero
```

### 11. Test each agent individually

Run the `/test-agents` workflow.

### 12. Wire into orchestrator

Create orchestrator files — see the Orchestrator skill for code templates.

### 13. Run the swarm

```bash
cd ~/Documents/Free_Cash_Flow
python -m orchestrator.scheduler
```

## Verification

- [ ] All 5 content repos cloned in `agents/`
- [ ] Virtual environment active
- [ ] All Python dependencies installed
- [ ] All 9 MCP servers installed via npm
- [ ] A2A SDK + agent frameworks installed
- [ ] `.env` file populated with real API keys
- [ ] Config YAML files created
- [ ] Agent Zero running in Docker
- [ ] Each agent passes smoke test
- [ ] MCP agents connect to external services
- [ ] Human Voice Engine passes test content
- [ ] Orchestrator scheduler starts without errors
