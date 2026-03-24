---
description: Emergency shutdown of all agents and posting — use when something goes wrong.
---

# Kill Switch Workflow

## Immediate Stop (All Agents)

```bash
cd ~/Documents/Free_Cash_Flow

# Option 1: Environment variable
echo "SWARM_ENABLED=false" >> config/.env
echo "TWITTER_ENABLED=false" >> config/.env
echo "⚠️ Swarm disabled via .env"

# Option 2: Kill the scheduler process
pkill -f "orchestrator.scheduler" && echo "Scheduler killed" || echo "No scheduler running"

# Option 3: Docker (if running in containers)
docker-compose stop && echo "All containers stopped"
```

## Stop Only Twitter Posting

```bash
echo "TWITTER_ENABLED=false" >> config/.env
echo "⚠️ Twitter posting disabled. Other agents still running."
```

## Stop Only Product Creation

```bash
# In config/agents.yaml, set product agent to disabled
python -c "
import yaml
with open('config/agents.yaml') as f:
    config = yaml.safe_load(f)
config['agents']['product']['enabled'] = False
with open('config/agents.yaml', 'w') as f:
    yaml.dump(config, f)
print('Product agent disabled')
"
```

## Re-Enable Everything

```bash
cd ~/Documents/Free_Cash_Flow

# Remove kill switches from .env
sed -i '' '/SWARM_ENABLED=false/d' config/.env
sed -i '' '/TWITTER_ENABLED=false/d' config/.env

# Add enabled flags
echo "SWARM_ENABLED=true" >> config/.env
echo "TWITTER_ENABLED=true" >> config/.env

# Restart scheduler
python -m orchestrator.scheduler &
echo "✅ Swarm re-enabled and scheduler restarted"
```

## Check Status

```bash
# Is the scheduler running?
pgrep -f "orchestrator.scheduler" && echo "✅ Scheduler running" || echo "❌ Scheduler stopped"

# Check .env flags
grep -E "SWARM_ENABLED|TWITTER_ENABLED" config/.env

# Check agent enabled states
python -c "
import yaml
with open('config/agents.yaml') as f:
    config = yaml.safe_load(f)
for name, agent in config['agents'].items():
    status = '✅' if agent['enabled'] else '❌'
    print(f'{status} {name}')
"
```
