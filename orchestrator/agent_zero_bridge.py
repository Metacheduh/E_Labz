"""
E-Labz Agent Zero Bridge — Specialist Agent for Complex Tasks
Calls Agent Zero's API for heavy-lift tasks: deep research, code gen, analysis.

Agent Zero runs in its own container on port 50001.
The coordinator calls this bridge when a task is too complex for the standard agents.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

try:
    from orchestrator.swarm_logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("agent_zero_bridge")

try:
    from orchestrator.memory_service import get_memory
except ImportError:
    def get_memory(): return None

# ============================================================
# CONFIG
# ============================================================

AGENT_ZERO_URL = os.getenv("AGENT_ZERO_URL", "http://localhost:50001")
TIMEOUT = int(os.getenv("AGENT_ZERO_TIMEOUT", "120"))


class AgentZeroBridge:
    """
    Bridge to Agent Zero for complex autonomous tasks.
    
    Use cases:
    - Deep research on a topic (multi-source synthesis)
    - Code generation for new agent features
    - Complex data analysis
    - Document/report writing
    - Multi-step reasoning tasks
    """

    def __init__(self, base_url: str = AGENT_ZERO_URL):
        self.base_url = base_url.rstrip("/")
        self._available = None

    @property
    def is_available(self) -> bool:
        """Check if Agent Zero is running."""
        if self._available is not None:
            return self._available
        try:
            resp = requests.get(f"{self.base_url}/", timeout=5)
            self._available = resp.status_code == 200
        except:
            self._available = False
        return self._available

    def send_task(self, task: str, context: str = "") -> dict:
        """
        Send a task to Agent Zero and get the result.
        
        Args:
            task: The task description
            context: Optional context to help Agent Zero
            
        Returns:
            dict with 'result', 'status', and 'duration'
        """
        if not self.is_available:
            logger.info("Agent Zero not available — skipping task")
            return {"result": None, "status": "unavailable", "duration": 0}

        start = datetime.now()
        full_prompt = task
        if context:
            full_prompt = f"Context: {context}\n\nTask: {task}"

        try:
            resp = requests.post(
                f"{self.base_url}/msg",
                json={"text": full_prompt},
                timeout=TIMEOUT
            )

            if resp.status_code == 200:
                data = resp.json()
                result = data.get("response", data.get("text", str(data)))
                duration = (datetime.now() - start).total_seconds()

                # Log to memory
                memory = get_memory()
                if memory:
                    memory.remember_strategy(
                        "agent_zero_task",
                        task[:100],
                        min(1.0, 0.5 + (0.5 if len(result) > 100 else 0)),
                        f"AZ completed in {duration:.1f}s: {result[:200]}"
                    )

                logger.info(f"🤖 Agent Zero completed task in {duration:.1f}s")
                return {"result": result, "status": "complete", "duration": duration}
            else:
                logger.warning(f"Agent Zero returned {resp.status_code}")
                return {"result": None, "status": f"error_{resp.status_code}", "duration": 0}

        except requests.Timeout:
            logger.warning(f"Agent Zero timed out after {TIMEOUT}s")
            return {"result": None, "status": "timeout", "duration": TIMEOUT}
        except Exception as e:
            logger.warning(f"Agent Zero error: {e}")
            return {"result": None, "status": "error", "duration": 0}

    def deep_research(self, topic: str) -> str:
        """Use Agent Zero for deep multi-source research."""
        task = (
            f"Research the following topic thoroughly. Find specific data points, "
            f"recent developments, expert opinions, and practical insights. "
            f"Format as a concise brief with bullet points.\n\n"
            f"Topic: {topic}"
        )
        result = self.send_task(task)
        return result.get("result", f"Research unavailable for: {topic}")

    def generate_code(self, description: str, language: str = "python") -> str:
        """Use Agent Zero for code generation."""
        task = (
            f"Write {language} code for the following requirement. "
            f"Include comments, error handling, and make it production-ready.\n\n"
            f"Requirement: {description}"
        )
        result = self.send_task(task)
        return result.get("result", "")

    def analyze_data(self, data_description: str, question: str) -> str:
        """Use Agent Zero for complex data analysis."""
        task = (
            f"Analyze this data and answer the question.\n\n"
            f"Data: {data_description}\n\n"
            f"Question: {question}"
        )
        result = self.send_task(task)
        return result.get("result", "Analysis unavailable")

    def write_content(self, brief: str, format_type: str = "article") -> str:
        """Use Agent Zero for long-form content writing."""
        task = (
            f"Write a {format_type} based on this brief. "
            f"Use a casual, expert tone. No AI buzzwords. "
            f"Be specific with examples and data.\n\n"
            f"Brief: {brief}"
        )
        result = self.send_task(task)
        return result.get("result", "")


# ============================================================
# SINGLETON
# ============================================================

_bridge = None

def get_agent_zero() -> AgentZeroBridge:
    """Get the Agent Zero bridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = AgentZeroBridge()
    return _bridge


if __name__ == "__main__":
    az = get_agent_zero()
    print(f"Agent Zero available: {az.is_available}")

    if az.is_available:
        result = az.deep_research("Latest developments in AI agent memory systems")
        print(f"Research result: {result[:300]}...")
    else:
        print("Start Agent Zero: docker-compose up agent-zero")

    print("✅ Agent Zero bridge ready")
