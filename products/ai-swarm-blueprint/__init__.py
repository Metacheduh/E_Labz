# Free Cash Flow Orchestrator
# The only custom code in the swarm — everything else is cloned.

from pathlib import Path

# Single source of truth for the project root directory.
# All modules should use this instead of Path(__file__).parent.parent chains.
PROJECT_ROOT = Path(__file__).parent.parent
