#!/usr/bin/env python3
"""download_service.py — 环境包与模型权重的安装 / 进度 / 取消 / 卸载。

瘦包（安装包不再携带 torch 与权重）里，用户装完软件后必须在「下载管理」页完成
两件事才能推理：① 安装 torch 环境包；② 下载模型权重。本模块是那条链路的执行层，
`routes/downloads.py` 与 `templates/downloads.html` 都建立在它之上。

硬约束（改动前务必读完，踩过这个坑）：

    **本模块及其 import 链禁止顶层 import torch。**

首次启动时后端跑在**引导解释器**上（WinPython，只装非 torch 依赖）。若本模块因
缺 torch 而导入失败，「下载管理」页就打不开，用户会陷入「装了软件却没法装环境」
的死局——而这条链路恰恰是瘦包唯一的自救通道。因此：

    - 「是否已装环境」只看解释器目录下的 ``RUNTIME.json``（安装流程自己写），
      不看 ``site-packages/torch``：WinPython 完整版自带 CPU 版 torch，会把未装
      环境误判成已装，用户直接进首页、永远看不到下载管理页；
    - torch 版本 / CUDA 标签一律从元信息文件读，不 import torch、不起子进程探测。

目录约定（**三处必须一致**：本模块 ``_runtime_dir()``、壳
``python_process.rs::resolve_runtime_dir``、打包脚本 ``scripts/build_desktop_bundle.ps1``）：

    <安装根>/
      ImageMultiModel.exe
      app/                 ← PROJECT_ROOT（config.yaml 在此）
        integrated_app/...
        downloads_catalog.json
      runtime/python.exe   ← 完整运行时（含 torch）；老布局或开发态可能不存在
      bootstrap/python.exe ← 瘦包自带的引导解释器（无 torch）

本仓既有约定把运行时放在**安装根**（与 ``app/`` 平级），故 ``runtime/`` 与
``bootstrap/`` 都在 ``PROJECT_ROOT`` 的上一级；同时兼容历史嵌套布局
（``app/runtime``、``app/bootstrap``），四个位置按「先 runtime 后 bootstrap」探测。

两条下载链路：
    1. 环境包：预构建成 zip 分卷，自己托管（torch cu128 从 PyPI/HF 取既慢又常失败）。
       下载 → 逐卷 SHA256 → 合并 → 解压 wheels → ``pip install --no-index`` 装进
       **当前解释器自身**的 site-packages（不另起一份解释器），装完写 ``RUNTIME.json``。
    2. 模型：不自己托管（省带宽与 Release 配额）。清单里给每个权重文件一个下载地址
       （直链 ``url`` 或 ``hf_repo`` + ``hf_file``），逐文件断点续传写入
       ``pretrained_models/<sub_dir>/<sub_path>``。
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from typing import Any

from .config import get_project_root
from .config_models import resolve_engine_model_paths

# ---------------------------------------------------------------- 常量 ----
RUNTIME_DIRNAME = "runtime"
# 瘦包内置引导解释器目录名（无 torch）。环境装进去后目录名**不变**，只多出 torch。
BOOTSTRAP_DIRNAME = "bootstrap"
CATALOG_FILENAME = "downloads_catalog.json"
RUNTIME_META_NAME = "RUNTIME.json"

# 环境包 Release 的兜底位置（清单缺失 base_url 时使用；发布环境包时须同步清单）
DEFAULT_RELEASE_BASE = "https://github.com/ReSerendipity/Image-DuoModel/releases/download"

ProgressCb = Callable[[str, float, str], None]  # (stage, ratio 0..1, message)

PROJECT_ROOT = str(get_project_root())


def _exe_name() -> str:
    return "python.exe" if os.name == "nt" else "python"


def _install_root() -> str:
    """安装根 = PROJECT_ROOT 的上一级（打包态 PROJECT_ROOT 是 ``<安装根>/app``）。"""
    return os.path.dirname(os.path.abspath(PROJECT_ROOT))


def _runtime_candidates() -> list[str]:
    """解释器候选目录，按优先级排列（先 runtime 后 bootstrap，先安装根后 app 内）。"""
    install_root = _install_root()
    return [
        os.path.join(install_root, RUNTIME_DIRNAME),
        os.path.join(PROJECT_ROOT, RUNTIME_DIRNAME),
        os.path.join(install_root, BOOTSTRAP_DIRNAME),
        os.path.join(PROJECT_ROOT, BOOTSTRAP_DIRNAME),
    ]


def _has_python(path: str) -> bool:
    return os.path.isfile(os.path.join(path, _exe_name()))


def _runtime_dir() -> str:
    """当前生效的运行时目录。

    瘦包里解释器叫 ``bootstrap/``，环境装进去后目录名不变（只多了 torch），
    所以不能只看 ``runtime/``；两个都可能有 python.exe，优先 ``runtime/``。
    """
    for candidate in _runtime_candidates():
        if _has_python(candidate):
            return candidate
    return os.path.join(_install_root(), RUNTIME_DIRNAME)


def _python_dir() -> str:
    """当前进程的解释器所在目录（环境就装进这里，不另起一份解释器）。"""
    return os.path.dirname(os.path.abspath(sys.executable or "")) or _runtime_dir()


def _catalog_path() -> str:
    return os.path.join(PROJECT_ROOT, CATALOG_FILENAME)


def app_version() -> str:
    """应用版本：优先配置单例（config.yaml ``version``），回退 ``version.txt``。"""
    try:
        from .config import get_config

        version = str(getattr(get_config(), "version", "") or "")
        if version:
            return version
    except Exception:  # noqa: BLE001 - 版本探测失败不能阻断下载页
        pass
    for rel in ("version.txt", os.path.join("app", "version.json")):
        path = os.path.join(PROJECT_ROOT, rel)
        if not os.path.isfile(path):
            continue
        try:
            if rel.endswith(".json"):
                with open(path, encoding="utf-8") as handle:
                    return str(json.load(handle).get("version") or "")
            with open(path, encoding="utf-8") as handle:
                return handle.read().strip()
        except (OSError, ValueError):
            continue
    return "0.0.0"


# ------------------------------------------------------------ 组件清单 ----
def load_catalog() -> dict:
    """读取随包分发的清单 ``app/downloads_catalog.json``（离线也可展示组件）。"""
    path = _catalog_path()
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
    return {}


def runtime_catalog() -> dict | None:
    entry = load_catalog().get("runtime")
    return entry if isinstance(entry, dict) else None


# ------------------------------------------------------------ HTTP 下载 ----
def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_file(
    url: str,
    target: str,
    on_progress: ProgressCb | None = None,
    stage: str = "download",
    should_cancel: Callable[[], bool] | None = None,
) -> None:
    """带断点续传的下载：已有 ``.part`` 时用 Range 续传；服务端不支持则整文件重下。"""
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    part = target + ".part"
    resume = os.path.getsize(part) if os.path.exists(part) else 0
    headers = {"User-Agent": "ImageMultiModel-Desktop"}
    if resume > 0:
        headers["Range"] = f"bytes={resume}-"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        if resume > 0 and response.status != 206:
            resume = 0  # 服务端不支持续传，从头开始
        total = int(response.headers.get("Content-Length") or 0) + resume
        mode = "ab" if resume > 0 else "wb"
        written = resume
        with open(part, mode) as handle:
            while True:
                if should_cancel and should_cancel():
                    raise InterruptedError("已取消")
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                handle.write(chunk)
                written += len(chunk)
                if on_progress and total > 0:
                    on_progress(stage, min(written / total, 1.0), "")
    os.replace(part, target)


# ------------------------------------------------------------ 环境包安装 ----
def install_runtime(
    on_progress: ProgressCb | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> dict:
    """下载环境包并离线装入**当前解释器**，返回写入的元信息 dict。"""
    catalog = runtime_catalog()
    if not catalog:
        raise RuntimeError(
            "未找到环境包清单 downloads_catalog.json，无法确定下载地址"
            "（请更新到含清单的版本，或用 -Mode runtime 重新构建发布资产）"
        )
    volumes = [v for v in catalog.get("volumes", []) if isinstance(v, dict)]
    if not volumes:
        raise RuntimeError("环境包清单缺少 volumes，无法下载")

    base = str(catalog.get("base_url") or f"{DEFAULT_RELEASE_BASE}/{catalog.get('tag', 'runtime-v1')}")
    work = os.path.join(PROJECT_ROOT, ".downloads", "runtime")
    os.makedirs(work, exist_ok=True)

    def report(stage: str, ratio: float, message: str) -> None:
        if on_progress:
            on_progress(stage, ratio, message)

    # 1) 逐卷下载 + SHA256 校验
    parts: list[str] = []
    total_vols = len(volumes)
    for index, vol in enumerate(volumes):
        name = str(vol.get("name"))
        url = f"{base.rstrip('/')}/{name}"
        dest = os.path.join(work, name)
        expected = str(vol.get("sha256") or "").lower()

        if os.path.exists(dest) and expected and _sha256(dest) == expected:
            parts.append(dest)
            report("download", (index + 1) / total_vols, f"{name} 已存在，跳过")
            continue

        report("download", index / total_vols, f"下载 {name}")
        _download_file(
            url,
            dest,
            on_progress=lambda _s, r, _m, i=index, n=name: report(  # type: ignore[misc]
                "download", (i + r) / total_vols, f"下载 {n}"
            ),
            should_cancel=should_cancel,
        )
        if expected:
            actual = _sha256(dest)
            if actual != expected:
                raise RuntimeError(f"{name} 校验失败（期望 {expected[:12]}…，实际 {actual[:12]}…）")
        parts.append(dest)

    # 2) 合并分卷（顺序字节拼接；单卷时直接复用）
    report("verify", 0.0, "合并分卷")
    archive = os.path.join(work, "runtime.zip")
    if len(parts) == 1:
        archive = parts[0]
    else:
        with open(archive, "wb") as out:
            for part in parts:
                with open(part, "rb") as handle:
                    shutil.copyfileobj(handle, out, 1024 * 1024)

    # 3) 解压 wheels（环境包内容就是一堆 .whl）
    report("extract", 0.0, "解压环境包")
    wheels = os.path.join(work, "wheels")
    if os.path.isdir(wheels):
        shutil.rmtree(wheels, ignore_errors=True)
    os.makedirs(wheels, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(wheels)

    # 4) 离线装入当前解释器（--no-index + --find-links，全程不联网）
    report("swap", 0.5, "安装 torch（离线）")
    target = _python_dir()
    packages = [str(p) for p in (catalog.get("packages") or []) if p] or [
        "torch",
        "torchvision",
    ]
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-index",
        "--find-links",
        wheels,
        "--no-warn-script-location",
        *packages,
    ]
    # PIP_CONFIG_FILE=NUL：屏蔽用户 pip 配置里的 extra-index-url（国内镜像常见会
    # 悄悄顶包成 +cpu 轮子，装出来 cuda_available=False）。
    env = dict(os.environ, PIP_CONFIG_FILE="NUL")
    result = subprocess.run(command, capture_output=True, text=True, cwd=PROJECT_ROOT, env=env)
    if result.returncode != 0:
        tail = (result.stderr or result.stdout or "")[-400:]
        raise RuntimeError(f"torch 离线安装失败（退出码 {result.returncode}）：{tail}")

    # 5) 落地元信息（status API 读它判断 torch/CUDA 版本，避免启动时 import torch）。
    #    壳也靠这个文件把运行形态从 Bootstrap 切成 Full——见 python_process.rs。
    meta = {
        "runtime_version": str(catalog.get("version", "1")),
        "python": catalog.get("python"),
        "torch": catalog.get("torch"),
        "cuda": catalog.get("cuda"),
        "built_at": catalog.get("built_at"),
        "min_app_version": catalog.get("min_app_version"),
        "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "installed_by_app_version": app_version(),
    }
    with open(os.path.join(target, RUNTIME_META_NAME), "w", encoding="utf-8") as meta_handle:
        json.dump(meta, meta_handle, ensure_ascii=False, indent=2)

    shutil.rmtree(work, ignore_errors=True)
    report("done", 1.0, "环境安装完成，请重启应用")
    return meta


# -------------------------------------------------------------- 模型安装 ----
def _catalog_model(name: str) -> dict | None:
    for item in load_catalog().get("models", []) or []:
        if isinstance(item, dict) and str(item.get("name")) == name:
            return item
    return None


def _model_files(item: dict) -> list[dict]:
    out: list[dict] = []
    for entry in item.get("files", []) or []:
        if isinstance(entry, dict) and entry.get("path"):
            out.append(entry)
    return out


def _hf_download(repo: str, filename: str, target: str) -> None:
    """按 HuggingFace 仓库取单文件（可选链路，缺 huggingface_hub 时明确报错）。"""
    try:
        from huggingface_hub import hf_hub_download  # 局部 import：可选依赖
    except ImportError as exc:  # pragma: no cover - 引导解释器通常未装该包
        raise RuntimeError(
            "该权重只声明了 HuggingFace 来源，但当前解释器未安装 huggingface_hub，"
            "无法下载（请改用 url 直链，或先 pip install huggingface_hub）"
        ) from exc
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    cached = hf_hub_download(repo_id=repo, filename=filename)
    shutil.copy2(cached, target)


def install_model(
    name: str,
    on_progress: ProgressCb | None = None,
    should_cancel: Callable[[], bool] | None = None,
) -> dict:
    """按清单下载某个引擎的权重文件，写入 ``pretrained_models/<sub_dir>/<sub_path>``。"""
    item = _catalog_model(name)
    if item is None:
        raise KeyError(f"清单中没有模型 {name}（请检查 downloads_catalog.json）")
    files = _model_files(item)
    if not files:
        raise RuntimeError(f"清单中 {name} 未提供任何权重文件条目")

    def report(stage: str, ratio: float, message: str) -> None:
        if on_progress:
            on_progress(stage, ratio, message)

    total = len(files)
    for index, entry in enumerate(files):
        if should_cancel and should_cancel():
            raise InterruptedError("已取消")
        rel = str(entry["path"]).replace("\\", "/")
        target = os.path.join(PROJECT_ROOT, rel)
        label = os.path.basename(rel)
        report("download", index / total, f"下载 {label}")

        expected = str(entry.get("sha256") or "").lower()
        if os.path.isfile(target) and expected and _sha256(target) == expected:
            report("download", (index + 1) / total, f"{label} 已存在，跳过")
            continue

        url = str(entry.get("url") or "")
        repo = str(entry.get("hf_repo") or "")
        if url:
            _download_file(
                url,
                target,
                on_progress=lambda _s, r, _m, i=index, n=label: report(  # type: ignore[misc]
                    "download", (i + r) / total, f"下载 {n}"
                ),
                should_cancel=should_cancel,
            )
        elif repo:
            _hf_download(repo, str(entry.get("hf_file") or os.path.basename(rel)), target)
        else:
            raise RuntimeError(
                f"清单中 {name} 的 {rel} 既没有 url 也没有 hf_repo，无法下载（社区权重需自行放置到该路径）"
            )

        if expected:
            actual = _sha256(target)
            if actual != expected:
                raise RuntimeError(f"{label} 校验失败（期望 {expected[:12]}…，实际 {actual[:12]}…）")

    report("done", 1.0, f"{name} 下载完成")
    return {"name": name, "files": [str(f["path"]) for f in files]}


# ---------------------------------------------------------------- 卸载 ----
def uninstall_runtime() -> dict:
    """卸载环境：当前解释器就是目标时**不能删目录**（后端正跑在里面）。

    这种情况下只删 torch 家族包与 ``RUNTIME.json``：删掉元信息，壳与状态接口就
    回到 Bootstrap 态，用户可以重新安装；删掉 torch 目录才真正腾出空间。
    """
    target = _runtime_dir()
    in_use = os.path.abspath(_python_dir()) == os.path.abspath(target)
    removed: list[str] = []
    if not os.path.isdir(target):
        return {"target": target, "in_use": in_use, "removed": removed}

    if in_use:
        site_packages = os.path.join(target, "Lib", "site-packages")
        families = ("torch", "torchvision", "torchaudio", "torchgen")
        for base in (site_packages, target):
            if not os.path.isdir(base):
                continue
            for name in os.listdir(base):
                low = name.lower()
                hit = any(
                    low == fam
                    or low.startswith(fam + "-")
                    or low.startswith(fam + ".")
                    or low.startswith("nvidia_")
                    or low.startswith("nvidia-")
                    for fam in families
                )
                if not hit:
                    continue
                path = os.path.join(base, name)
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    try:
                        os.remove(path)
                    except OSError:
                        continue
                removed.append(path)
        for meta in (RUNTIME_META_NAME, "runtime_meta.json"):
            path = os.path.join(target, meta)
            if os.path.isfile(path):
                os.remove(path)
                removed.append(path)
    else:
        shutil.rmtree(target, ignore_errors=True)
        removed.append(target)
    return {"target": target, "in_use": in_use, "removed": removed}


def uninstall_model(name: str, config: Any) -> dict:
    """删除某引擎权重的落盘文件（只删自己的，共享的 clip / vae 不动）。"""
    paths = _engine_weight_paths(config, name)
    removed: list[str] = []
    for path in paths:
        if os.path.isfile(path):
            try:
                os.remove(path)
                removed.append(path)
            except OSError:
                continue
    return {"name": name, "removed": removed}


# ------------------------------------------------------------ 就位扫描 ----
def _dir_stats(path: str) -> tuple[int, int]:
    """返回（文件数，总字节）。目录不存在或不可读时返回 (0, 0)。"""
    files = 0
    total = 0
    if not os.path.isdir(path):
        return 0, 0
    for root, _dirs, names in os.walk(path):
        for name in names:
            try:
                total += os.path.getsize(os.path.join(root, name))
                files += 1
            except OSError:
                continue
    return files, total


def _engine_weight_paths(config: Any, name: str) -> list[str]:
    """解析某引擎声明的主权重绝对路径（不加载权重、不 import torch）。"""
    models_cfg = getattr(config, "models", None)
    if models_cfg is None:
        return []
    engines = getattr(models_cfg, "engines", {}) or {}
    engine = engines.get(name) if hasattr(engines, "get") else None
    if engine is None:
        return []
    project_root = str(getattr(config, "project_root", PROJECT_ROOT) or PROJECT_ROOT)
    try:
        resolved = resolve_engine_model_paths(engine, models_cfg, project_root)
    except Exception:  # noqa: BLE001 - 路径解析失败不应打断状态接口
        return []
    return [str(p) for p in resolved.values() if p]


def _models_root(config: Any) -> str:
    models_cfg = getattr(config, "models", None)
    portable = getattr(models_cfg, "portable", None)
    rel = str(getattr(portable, "internal_models_dir", "") or "pretrained_models")
    if os.path.isabs(rel):
        return rel
    project_root = str(getattr(config, "project_root", PROJECT_ROOT) or PROJECT_ROOT)
    return os.path.join(project_root, rel)


def scan_models(config: Any) -> list[dict]:
    """扫描各引擎声明的权重，返回就位情况（只看文件是否存在，不加载）。"""
    models_cfg = getattr(config, "models", None)
    engines = getattr(models_cfg, "engines", {}) or {}
    default = str(getattr(models_cfg, "default_engine", "") or "")
    catalog_models = {
        str(item.get("name")): item for item in (load_catalog().get("models", []) or []) if isinstance(item, dict)
    }
    out: list[dict] = []
    for key in engines:
        spec = engines[key]
        paths = _engine_weight_paths(config, key)
        present = bool(paths) and all(os.path.isfile(p) for p in paths)
        size = 0
        for path in paths:
            try:
                if os.path.isfile(path):
                    size += os.path.getsize(path)
            except OSError:
                continue
        catalog_item = catalog_models.get(key) or {}
        download_bytes = 0
        for entry in _model_files(catalog_item):
            try:
                download_bytes += int(entry.get("size_bytes") or 0)
            except (TypeError, ValueError):
                continue
        out.append(
            {
                "name": key,
                "display_name": str(getattr(spec, "display_name", "") or key),
                "backend": str(getattr(spec, "backend", "") or ""),
                "min_vram_gb": float(getattr(spec, "vram_gb", 0) or 0),
                "present": present,
                "path": _models_root(config),
                "files": paths,
                "file_count": len(paths),
                "size_bytes": size,
                "download_bytes": download_bytes,
                "downloadable": bool(_model_files(catalog_item)),
                "is_default": key == default,
            }
        )
    out.sort(key=lambda item: (not item["is_default"], item["name"]))
    return out


def build_runtime_status() -> dict:
    """环境包状态：``present``（有 python.exe）与 ``installed``（有 RUNTIME.json）分开报。

    两者分离是本方案的关键判据：WinPython 自带 python.exe 但没有 RUNTIME.json，
    即「有解释器但未装 torch 环境」的引导态。
    """
    runtime_dir = _runtime_dir()
    exe = os.path.join(runtime_dir, _exe_name())
    meta = _read_runtime_meta(runtime_dir) or {}
    present = os.path.isfile(exe)
    installed = os.path.isfile(os.path.join(runtime_dir, RUNTIME_META_NAME))
    files, size = _dir_stats(runtime_dir)
    current = app_version()
    min_app = meta.get("min_app_version")
    return {
        "present": present,
        "installed": installed,
        "path": runtime_dir,
        "executable": exe if present else None,
        "in_use": os.path.abspath(_python_dir()) == os.path.abspath(runtime_dir),
        "python_version": meta.get("python"),
        "torch_version": meta.get("torch"),
        "cuda": meta.get("cuda"),
        "runtime_version": meta.get("runtime_version"),
        "built_at": meta.get("built_at"),
        "installed_at": meta.get("installed_at"),
        "file_count": files,
        "size_bytes": size,
        "compatible": _version_ge(current, min_app),
        "min_app_version": min_app,
    }


def _read_runtime_meta(runtime_dir: str) -> dict | None:
    meta_path = os.path.join(runtime_dir, RUNTIME_META_NAME)
    if not os.path.isfile(meta_path):
        return None
    try:
        with open(meta_path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _version_ge(actual: str | None, required: str | None) -> bool:
    """比较 x.y.z：actual >= required 返回 True。缺值一律视为兼容（不阻断）。"""
    if not actual or not required:
        return True

    def parts(text: str) -> tuple[int, ...]:
        out: list[int] = []
        for chunk in str(text).split(".")[:3]:
            digits = "".join(ch for ch in chunk if ch.isdigit())
            out.append(int(digits) if digits else 0)
        return tuple(out)

    return parts(actual) >= parts(required)


def current_mode() -> str:
    """当前后端跑在哪个解释器上：``full`` / ``bootstrap`` / ``system``。"""
    exe = os.path.abspath(sys.executable or "")
    if not exe:
        return "system"
    runtime = os.path.abspath(os.path.join(_install_root(), RUNTIME_DIRNAME))
    bootstrap = os.path.abspath(os.path.join(_install_root(), BOOTSTRAP_DIRNAME))
    for base, mode in ((runtime, "full"), (bootstrap, "bootstrap")):
        if exe == base or exe.startswith(base + os.sep):
            # 装在 bootstrap 里的环境同样算 full（目录名不变，靠 RUNTIME.json 判定）
            if mode == "bootstrap" and os.path.isfile(os.path.join(base, RUNTIME_META_NAME)):
                return "full"
            return mode
    return "system"


def build_status(config: Any) -> dict:
    """下载管理页的整体状态：运行形态、环境就位、各模型就位。"""
    runtime = build_runtime_status()
    models = scan_models(config)
    ready = bool(runtime["installed"] and runtime["compatible"] and any(m["present"] for m in models))
    return {
        "app_version": app_version(),
        "mode": current_mode(),
        "ready": ready,
        "runtime": runtime,
        "models": models,
        "model_root": _models_root(config),
        "catalog_present": bool(load_catalog()),
    }


def catalog_view(config: Any) -> dict:
    """给页面用的可下载清单：环境包 + 各模型（含是否已就位）。"""
    catalog = load_catalog()
    runtime = catalog.get("runtime") if isinstance(catalog.get("runtime"), dict) else None
    models = []
    for item in scan_models(config):
        models.append(
            {
                "name": item["name"],
                "display_name": item["display_name"],
                "present": item["present"],
                "size_bytes": item["size_bytes"],
                "download_bytes": item["download_bytes"],
                "downloadable": item["downloadable"],
                "min_vram_gb": item["min_vram_gb"],
                "is_default": item["is_default"],
                "source": "direct / huggingface",
            }
        )
    return {
        "runtime": runtime,
        "models": models,
        "catalog_present": bool(catalog),
    }


# ------------------------------------------------------------ 任务管理 ----
class DownloadTask:
    """单个下载任务的状态（后台线程执行，前端轮询进度）。"""

    def __init__(self, component: str, kind: str, target: str) -> None:
        self.component = component
        self.kind = kind  # runtime | model
        self.target = target
        self.stage = "queued"
        self.ratio = 0.0
        self.message = ""
        self.error: str | None = None
        self.finished = False
        self.started_at = time.time()
        self._cancel = threading.Event()
        self._thread: threading.Thread | None = None

    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "kind": self.kind,
            "target": self.target,
            "stage": self.stage,
            "ratio": round(self.ratio, 4),
            "message": self.message,
            "error": self.error,
            "finished": self.finished,
            "elapsed_seconds": round(time.time() - self.started_at, 1),
        }

    def request_cancel(self) -> None:
        self._cancel.set()

    def _progress(self, stage: str, ratio: float, message: str) -> None:
        self.stage = stage
        self.ratio = ratio
        self.message = message

    def run(self) -> None:
        try:
            if self.kind == "runtime":
                install_runtime(self._progress, self._cancel.is_set)
            else:
                install_model(self.target, self._progress, self._cancel.is_set)
            self.stage = "done"
            self.ratio = 1.0
        except InterruptedError as exc:
            self.stage = "cancelled"
            self.error = str(exc)
        except (urllib.error.URLError, OSError) as exc:
            self.stage = "error"
            self.error = f"网络错误: {exc}"
        except Exception as exc:  # noqa: BLE001 - 任务状态需回传用户，不能让线程静默死
            self.stage = "error"
            self.error = str(exc)
        finally:
            self.finished = True


class DownloadManager:
    """进程级单例：同一组件同时只允许一个任务在跑。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tasks: dict[str, DownloadTask] = {}

    def start(self, kind: str, target: str = "") -> DownloadTask:
        component = "runtime" if kind == "runtime" else f"model:{target}"
        with self._lock:
            existing = self._tasks.get(component)
            if existing and not existing.finished:
                return existing
            task = DownloadTask(component, kind, target)
            self._tasks[component] = task
        thread = threading.Thread(target=task.run, name=f"download-{component}", daemon=True)
        task._thread = thread
        thread.start()
        return task

    def get(self, component: str) -> DownloadTask | None:
        return self._tasks.get(component)

    def progress(self) -> list[dict]:
        with self._lock:
            return [task.to_dict() for task in self._tasks.values()]

    def cancel(self, component: str) -> bool:
        task = self._tasks.get(component)
        if not task or task.finished:
            return False
        task.request_cancel()
        return True


_MANAGER: DownloadManager | None = None
_MANAGER_LOCK = threading.Lock()


def get_download_manager() -> DownloadManager:
    global _MANAGER
    if _MANAGER is None:
        with _MANAGER_LOCK:
            if _MANAGER is None:
                _MANAGER = DownloadManager()
    return _MANAGER
