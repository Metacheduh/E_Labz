"""Shared test fixtures for the Free Cash Flow test suite."""

import os
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def test_config(tmp_path):
    """Create a temporary config directory with test .env file."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    env_file = config_dir / ".env"
    env_file.write_text(
        "OPENAI_API_KEY=test-key\n"
        "TWITTER_ENABLED=false\n"
        "SWARM_ENABLED=false\n"
    )
    return config_dir


@pytest.fixture
def test_data_dir(tmp_path):
    """Create a temporary data directory for test outputs."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "performance").mkdir()
    return data_dir
