"""Tests for the metrics tracker (orchestrator.intelligence.metrics)."""

import sqlite3
import pytest
from pathlib import Path
from unittest.mock import patch


class TestMetricsDB:
    """Test SQLite metrics database operations."""

    def test_import(self):
        """Verify metrics module can be imported."""
        from orchestrator.intelligence.metrics import log_daily_metrics, get_daily_metrics
        assert callable(log_daily_metrics)
        assert callable(get_daily_metrics)

    def test_log_and_retrieve_daily_metrics(self, tmp_path):
        """Should be able to log and retrieve daily metrics."""
        from orchestrator.intelligence import metrics

        test_db = tmp_path / "test_metrics.db"
        with patch.object(metrics, 'DB_PATH', test_db):
            metrics.log_daily_metrics({
                "posts_published": 5,
                "impressions": 1200,
                "follower_total": 167,
                "revenue": 19.00,
            })

            result = metrics.get_daily_metrics()
            assert result["posts_published"] == 5
            assert result["follower_total"] == 167

    def test_monthly_revenue_aggregation(self, tmp_path):
        """Monthly revenue should aggregate correctly."""
        from orchestrator.intelligence import metrics

        test_db = tmp_path / "test_metrics.db"
        with patch.object(metrics, 'DB_PATH', test_db):
            metrics.log_daily_metrics({"revenue": 50.00, "sales": 3})
            result = metrics.get_monthly_revenue()
            assert result["total_revenue"] == 50.00
            assert result["target"] == 3000


class TestDailyReport:
    """Test daily report generation."""

    def test_save_daily_report(self, tmp_path):
        """Should save a JSON report to the performance directory."""
        from orchestrator.intelligence import metrics

        with patch.object(metrics, 'PERFORMANCE_DIR', tmp_path):
            path = metrics.save_daily_report({"test": True})
            assert path.exists()
            assert path.suffix == ".json"
