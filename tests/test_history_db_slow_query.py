"""tests/test_history_db_slow_query.py — 慢查询观测（v2.9 评估·后端服务设计 P1-1）"""

from __future__ import annotations

import logging

import pytest

import integrated_app.history_db as hdb
from integrated_app.history_db import HistoryDB


@pytest.fixture()
def db(tmp_path):
    d = HistoryDB(tmp_path / "slow_query.db")
    yield d
    d.close()


def test_slow_query_logged_when_over_threshold(db, caplog, monkeypatch):
    monkeypatch.setattr(hdb, "SLOW_QUERY_THRESHOLD_MS", 0.0)
    before = int(hdb.slow_query_stats["count"])
    with caplog.at_level(logging.WARNING, logger="integrated_app.history_db"):
        db.conn.execute("SELECT 1")
    assert int(hdb.slow_query_stats["count"]) == before + 1
    assert "[SLOW-QUERY]" in caplog.text
    assert "SELECT 1" in caplog.text
    assert hdb.slow_query_stats["last_sql"] == "SELECT 1"


def test_no_warning_below_threshold(db, caplog, monkeypatch):
    monkeypatch.setattr(hdb, "SLOW_QUERY_THRESHOLD_MS", 3_600_000.0)
    with caplog.at_level(logging.WARNING, logger="integrated_app.history_db"):
        db.conn.execute("SELECT 2")
    assert "[SLOW-QUERY]" not in caplog.text


def test_disabled_when_threshold_negative(db, caplog, monkeypatch):
    monkeypatch.setattr(hdb, "SLOW_QUERY_THRESHOLD_MS", -1.0)
    with caplog.at_level(logging.WARNING, logger="integrated_app.history_db"):
        db.conn.execute("SELECT 3")
    assert "[SLOW-QUERY]" not in caplog.text


def test_executescript_also_observed(db, caplog, monkeypatch, tmp_path):
    monkeypatch.setattr(hdb, "SLOW_QUERY_THRESHOLD_MS", 0.0)
    with caplog.at_level(logging.WARNING, logger="integrated_app.history_db"):
        db.conn.executescript("CREATE TABLE t_probe(x INTEGER);")
    assert any("[SLOW-QUERY]" in m and "CREATE TABLE t_probe" in m for m in caplog.messages)
