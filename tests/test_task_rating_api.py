"""
tests/test_task_rating_api.py — /api/tasks/{id}/rating + /api/tasks/rating-summary（NEXT P1-3）

验收：
- POST rating 写读 roundtrip（闭环入口接通：此前 set_rating 仅 DB 层 + 单测，无 API）；
- rating 越界由 API 层 Query 校验拒绝（422）；
- 不存在任务评分返回 404；
- GET rating-summary 按引擎聚合（消费端数据源）；
- 静态路由 /rating-summary 不被 /{task_id} 动态路由吞掉。
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration

from fastapi import FastAPI
from fastapi.testclient import TestClient

from integrated_app.history_db import HistoryDB


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = HistoryDB(tmp_path / "test_rating_api.db")
    db.create_task(task_id="t1", engine="z_image_turbo_native", prompt="a cat")
    db.create_task(task_id="t2", engine="flux2_klein_native", prompt="a dog")
    db.create_task(task_id="t3", engine="z_image_turbo_native", prompt="a bird")
    db.set_rating("t2", 1)

    from integrated_app.routes.task_routes import router

    app = FastAPI()
    app.include_router(router)
    app.state.history_db = db
    yield TestClient(app), db
    db.close()


class TestRatingApi:
    def test_set_rating_roundtrip(self, client):
        c, db = client
        resp = c.post("/api/tasks/t1/rating", params={"rating": 1})
        assert resp.status_code == 200
        assert resp.json() == {"task_id": "t1", "rating": 1}
        assert db.get_task("t1")["rating"] == 1

        resp = c.post("/api/tasks/t1/rating", params={"rating": -1})
        assert resp.status_code == 200
        assert db.get_task("t1")["rating"] == -1

        resp = c.post("/api/tasks/t1/rating", params={"rating": 0})
        assert resp.status_code == 200
        assert db.get_task("t1")["rating"] == 0

    def test_set_rating_rejects_out_of_range(self, client):
        c, _ = client
        resp = c.post("/api/tasks/t1/rating", params={"rating": 5})
        assert resp.status_code == 422
        resp = c.post("/api/tasks/t1/rating", params={"rating": -2})
        assert resp.status_code == 422

    def test_set_rating_missing_task_404(self, client):
        c, _ = client
        resp = c.post("/api/tasks/nope/rating", params={"rating": 1})
        assert resp.status_code == 404

    def test_rating_summary_aggregates_by_engine(self, client):
        c, _ = client
        resp = c.get("/api/tasks/rating-summary")
        assert resp.status_code == 200
        body = resp.json()
        by_engine = {e["engine"]: e for e in body["by_engine"]}
        assert by_engine["z_image_turbo_native"]["total"] == 2
        assert by_engine["z_image_turbo_native"]["rating_1"] == 0
        assert by_engine["z_image_turbo_native"]["rated"] == 0
        assert by_engine["flux2_klein_native"]["rating_1"] == 1
        assert by_engine["flux2_klein_native"]["rated"] == 1
        assert body["overall"]["total"] == 3
        assert body["overall"]["rated"] == 1
        assert body["overall"]["rating_1"] == 1

    def test_rating_summary_not_swallowed_by_task_id(self, client):
        """静态路由优先级：/rating-summary 必须命中汇总而非被 {task_id} 当 404。"""
        c, _ = client
        resp = c.get("/api/tasks/rating-summary")
        assert resp.status_code == 200
        assert "overall" in resp.json()
