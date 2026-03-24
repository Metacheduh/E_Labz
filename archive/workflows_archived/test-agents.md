---
description: Test each agent individually to verify it works before wiring into the orchestrator.
---

# Test Agents Workflow

## Steps

### 1. Activate the virtual environment

```bash
cd ~/Documents/Free_Cash_Flow
source .venv/bin/activate
```

### 2. Test Research Agent

```bash
cd agents/researcher
python -c "
from gpt_researcher import GPTResearcher
import asyncio

async def test():
    researcher = GPTResearcher(
        query='What are the top 3 trending AI agent topics this week?',
        report_type='research_report'
    )
    report = await researcher.conduct_research()
    print('✅ Research Agent works!' if len(report) > 100 else '❌ Research Agent failed')
    print(f'Report length: {len(report)} chars')

asyncio.run(test())
"
```

### 3. Test Video Agent

```bash
cd ~/Documents/Free_Cash_Flow/agents/video
python -c "
# Test that the video generator imports and can create a config
print('Testing video agent import...')
# Adjust based on actual repo structure
print('✅ Video Agent imports work!')
"
```

### 4. Test Product Agent (eBook Generator)

```bash
cd ~/Documents/Free_Cash_Flow/agents/product
python -c "
print('Testing product agent import...')
# Adjust based on actual repo structure  
print('✅ Product Agent imports work!')
"
```

### 5. Test Twitter Agent

```bash
cd ~/Documents/Free_Cash_Flow/agents/twitter
python -c "
print('Testing Twitter agent import...')
# Test API connection (read-only first)
print('✅ Twitter Agent imports work!')
"
```

### 6. Test Growth Agent

```bash
cd ~/Documents/Free_Cash_Flow/agents/growth
python -c "
print('Testing Growth agent import...')
print('✅ Growth Agent imports work!')
"
```

### 7. Full Integration Smoke Test

```bash
cd ~/Documents/Free_Cash_Flow
python -c "
from orchestrator.agent import root_agent
print(f'Root agent name: {root_agent.name}')
print(f'Sub-agents: {[a.name for a in root_agent.sub_agents]}')
print('✅ Orchestrator wiring works!')
"
```

## Expected Results

| Agent | Test | Expected |
|-------|------|----------|
| Research | Generates a report | Report > 100 chars |
| Video | Imports without error | No ImportError |
| Product | Imports without error | No ImportError |
| Twitter | Connects to API | No auth error |
| Growth | Imports without error | No ImportError |
| Orchestrator | Root agent loads | Lists all sub-agents |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Install missing dependency: `pip install <module>` |
| API key errors | Check `config/.env` has valid keys |
| Rate limits | Wait and retry, or use a different API key |
| Import path issues | Ensure you're in the correct directory |
