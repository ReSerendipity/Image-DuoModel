"""tests/test_downloads_bootstrap.py — 瘦包引导态（无 torch）下的下载管理链路

回归目标（三条硬约束，见 docs/桌面分发分层定案 与 SLIM 移植规范）：
1. 下载页链路**禁止顶层 import torch**：引导解释器没有 torch，一旦链路上出现
   torch，`/downloads` 直接 500，用户永远装不上环境；
2. `app_server` 必须能在无 torch 下起后端（模型注册表导入失败要降级而非崩溃）；
3. 「是否已装环境」只看 `RUNTIME.json`，不看 `site-packages/torch`
   （WinPython 完整版自带 CPU 版 torch，会把未装环境误判成已装）。
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.integrated_app import download_service as ds
from app.integrated_app.app_server import create_app
from app.integrated_app.routes import downloads as dl_routes

APP_DIR = Path(__file__).resolve().parent.parent / "app" / "integrated_app"


@pytest.fixture(scope="module")
def client():
    """引导态应用（不依赖 torch；lifespan 会在无 torch 下正常起来）"""
    with TestClient(create_app(enable_rate_limit=False)) as c:
        yield c


# ---------------------------------------------------------------- 硬约束 ----
def _top_level_imports(path: Path) -> set[str]:
    """收集模块**顶层**（含 try/except 包裹）的 import 模块名。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()

    def walk(nodes) -> None:
        for node in nodes:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        names.add(alias.name.split(".")[0])
                elif node.module:
                    names.add(node.module.split(".")[0])
            elif isinstance(node, ast.Try):
                walk(node.body)

    walk(tree.body)
    return names


@pytest.mark.parametrize(
    "rel",
    ["download_service.py", "routes/downloads.py"],
)
def test_download_chain_has_no_top_level_torch(rel: str) -> None:
    """下载页链路模块禁止在顶层 import torch（引导态必 500）。"""
    imports = _top_level_imports(APP_DIR / rel)
    assert "torch" not in imports, f"{rel} 顶层 import 了 torch，引导态下载页会 500"


def test_download_route_avoids_dependency_injection() -> None:
    """路由不得用 Depends(...)：依赖注入链可能顺带拉起 ModelManager/引擎/torch。"""
    path = APP_DIR / "routes" / "downloads.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    used = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == "Depends"]
    assert not used, "下载路由出现了 Depends(...)：引导态可能因依赖链缺 torch 而 500"
    # 配置必须从 lifespan 放在 app.state 的实例取
    assert "app.state.config" in path.read_text(encoding="utf-8")


# ------------------------------------------------------------ 页面与接口 ----
def test_downloads_page_ok(client: TestClient) -> None:
    resp = client.get("/downloads")
    assert resp.status_code == 200
    body = resp.text
    assert "downloads.js" in body
    # 文案走服务端渲染 + data 属性（CSP 收紧后不允许内联脚本）
    assert "data-i18n=" in body


def test_status_api_ok(client: TestClient) -> None:
    resp = client.get("/api/downloads/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] in ("full", "bootstrap", "system")
    assert "present" in data["runtime"] and "installed" in data["runtime"]
    assert isinstance(data["models"], list)


def test_catalog_api_ok(client: TestClient) -> None:
    resp = client.get("/api/downloads/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert "runtime" in data and "models" in data


def test_progress_api_ok(client: TestClient) -> None:
    resp = client.get("/api/downloads/progress")
    assert resp.status_code == 200
    assert isinstance(resp.json()["tasks"], list)


def test_heavy_endpoints_are_loopback_only(client: TestClient) -> None:
    """TestClient 的 client.host 是 testclient（非回环）→ 重操作必须 403。"""
    resp = client.post("/api/downloads/start", json={"kind": "runtime", "target": ""})
    assert resp.status_code == 403
    resp = client.post("/api/downloads/uninstall", json={"kind": "runtime", "target": ""})
    assert resp.status_code == 403


def test_deny_remote_allows_loopback_variants() -> None:
    class _C:
        def __init__(self, host: str) -> None:
            self.host = host

    class _R:
        def __init__(self, host: str) -> None:
            self.client = _C(host)

    for host in ("127.0.0.1", "::1", "localhost", "::ffff:127.0.0.1"):
        assert dl_routes._deny_remote(_R(host)) is None
    with pytest.raises(HTTPException) as exc:
        dl_routes._deny_remote(_R("192.168.1.20"))
    assert exc.value.status_code == 403


# ------------------------------------------------- 运行时就位判定（RUNTIME.json）----
def _make_runtime(tmp_path: Path, meta: bool, torch: bool = False) -> Path:
    root = tmp_path / "app"
    runtime = tmp_path / "bootstrap"
    (root).mkdir(parents=True, exist_ok=True)
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / "python.exe").write_bytes(b"")
    if torch:
        site = runtime / "Lib" / "site-packages" / "torch"
        site.mkdir(parents=True, exist_ok=True)
    if meta:
        (runtime / "RUNTIME.json").write_text('{"torch": "2.10.0+cu128"}', encoding="utf-8")
    return runtime


def test_status_separates_present_and_installed(tmp_path, monkeypatch) -> None:
    runtime = _make_runtime(tmp_path, meta=False, torch=True)
    monkeypatch.setattr(ds, "PROJECT_ROOT", str(tmp_path / "app"))
    status = ds.build_runtime_status()
    assert status["path"] == str(runtime)
    # 有解释器、自带 CPU torch，但没有 RUNTIME.json → 仍是「未装环境」
    assert status["present"] is True
    assert status["installed"] is False


def test_status_installed_when_meta_present(tmp_path, monkeypatch) -> None:
    runtime = _make_runtime(tmp_path, meta=True)
    monkeypatch.setattr(ds, "PROJECT_ROOT", str(tmp_path / "app"))
    status = ds.build_runtime_status()
    assert status["installed"] is True
    assert status["torch_version"] == "2.10.0+cu128"


def test_uninstall_keeps_interpreter_when_in_use(tmp_path, monkeypatch) -> None:
    """后端正跑在 bootstrap 里时不能删目录，只删 torch 家族与 RUNTIME.json。"""
    runtime = _make_runtime(tmp_path, meta=True, torch=True)
    monkeypatch.setattr(ds, "PROJECT_ROOT", str(tmp_path / "app"))
    monkeypatch.setattr(ds.sys, "executable", str(runtime / "python.exe"), raising=False)
    result = ds.uninstall_runtime()
    assert result["in_use"] is True
    assert (runtime / "python.exe").exists(), "正在使用的解释器不能被删掉"
    assert not (runtime / "RUNTIME.json").exists()
    assert not (runtime / "Lib" / "site-packages" / "torch").exists()


def test_runtime_dir_prefers_runtime_over_bootstrap(tmp_path, monkeypatch) -> None:
    root = tmp_path / "app"
    root.mkdir()
    (tmp_path / "runtime").mkdir()
    (tmp_path / "runtime" / "python.exe").write_bytes(b"")
    _make_runtime(tmp_path, meta=False)
    monkeypatch.setattr(ds, "PROJECT_ROOT", str(root))
    assert Path(ds._runtime_dir()) == tmp_path / "runtime"
