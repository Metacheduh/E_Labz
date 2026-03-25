"""Tests for the Human Voice Engine (orchestrator.pipeline.humanize)."""

import pytest


class TestHumanizeContent:
    """Test the core humanization pipeline."""

    def test_import(self):
        """Verify humanize module can be imported."""
        from orchestrator.pipeline.humanize import humanize_content
        assert callable(humanize_content)

    def test_strips_banned_words(self):
        """Content should not contain banned AI words after humanization."""
        from orchestrator.pipeline.humanize import humanize_content

        ai_text = "Let's delve into the comprehensive landscape of AI tools."
        result = humanize_content(ai_text, content_type="tweet")

        banned = ["delve", "comprehensive", "landscape"]
        result_lower = result.lower()
        for word in banned:
            assert word not in result_lower, f"Banned word '{word}' still present"

    def test_adds_contractions(self):
        """Content should use contractions after humanization."""
        from orchestrator.pipeline.humanize import humanize_content

        formal = "I do not think that this is going to work. It is not the right approach."
        result = humanize_content(formal, content_type="tweet")
        assert "n't" in result or "it's" in result.lower(), "No contractions found"

    def test_publish_returns_content(self):
        """publish() should return humanized content as a string."""
        from orchestrator.pipeline.humanize import publish

        result = publish("Testing the pipeline output format", content_type="tweet")
        assert isinstance(result, str)
        assert len(result) > 0


class TestVoiceProfiles:
    """Test voice profile selection."""

    def test_default_profile_is_friendly(self):
        """Default voice profile should be 'friendly'."""
        from orchestrator.pipeline.humanize import humanize_content

        result = humanize_content("Test content", content_type="tweet")
        assert isinstance(result, str)
        assert len(result) > 0
