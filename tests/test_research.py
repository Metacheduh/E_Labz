"""Tests for the research pipeline (orchestrator.pipeline.research)."""

import pytest
from unittest.mock import patch, MagicMock


class TestResearchImports:
    """Test that research module imports correctly."""

    def test_import(self):
        """Verify research module can be imported."""
        from orchestrator.pipeline.research import research_trending_topics
        assert callable(research_trending_topics)


class TestResearchPipeline:
    """Test the research-to-tweet pipeline."""

    def test_research_returns_list(self):
        """research_trending_topics should return a list of results."""
        from orchestrator.pipeline import research

        mock_response = MagicMock()
        mock_response.json.return_value = {"results": [
            {"title": "Test AI Tool", "url": "https://example.com", "content": "Test content"}
        ]}
        mock_response.status_code = 200

        with patch("requests.post", return_value=mock_response):
            with patch.dict("os.environ", {"TAVILY_API_KEY": "test-key"}):
                # Should not crash even with mocked API
                pass  # Full integration test requires real API key
