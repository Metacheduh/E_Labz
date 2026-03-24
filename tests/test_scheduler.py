"""Tests for the scheduler (orchestrator.core.scheduler)."""

import pytest
from unittest.mock import patch


class TestSchedulerImports:
    """Test that scheduler module imports correctly."""

    def test_import(self):
        """Verify scheduler module can be imported."""
        from orchestrator.core.scheduler import SCHEDULE_PATH
        assert SCHEDULE_PATH.name == "schedule.yaml"

    def test_project_root_resolves(self):
        """PROJECT_ROOT should point to the actual project directory."""
        from orchestrator import PROJECT_ROOT
        assert PROJECT_ROOT.exists()
        assert (PROJECT_ROOT / "config").is_dir()
        assert (PROJECT_ROOT / "orchestrator").is_dir()
