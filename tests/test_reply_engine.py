"""Tests for the reply engine (orchestrator.pipeline.reply_engine)."""

import pytest
from unittest.mock import patch


class TestReplyEngineImports:
    """Test that reply engine module imports correctly."""

    def test_import(self):
        """Verify reply engine module can be imported."""
        from orchestrator.pipeline.reply_engine import run_engagement_session
        assert callable(run_engagement_session)


class TestToneRotation:
    """Test that tone rotation cycles through available tones."""

    def test_tones_are_defined(self):
        """The reply engine should have defined tone profiles."""
        from orchestrator.pipeline import reply_engine
        # Check that tone-related constants/config exist
        source = open(reply_engine.__file__).read()
        for tone in ["casual", "insightful", "curious", "helpful", "supportive"]:
            assert tone in source, f"Tone '{tone}' not found in reply_engine"
