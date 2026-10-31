#!/usr/bin/env python3
"""routes/downloads.py — 「下载管理」页的数据后端。

瘦包不含 Python 环境（torch）与模型权重，用户装完软件后必须先在这里安装它们，
才能开始推理。本模块提供该页面的状态查询与安装/取消/卸载操作。

硬约束（改动前务必读完）：

    **禁止在本模块顶层 import torch，也禁止 Depends(get_config) 一类会拉起重模块的依赖。**

首次启动时后端跑在**引导解释器**上（只有 Web 依赖、没有 torch）。若本模块因缺
torch 而导入失败，「下载管理」页就打不开，用户会陷入「装了软件却没法装环境」的
死局——而这条链路恰恰是瘦包唯一的自救通道。因此：

    - 配置从 ``request.app.state.config`` 取（lifespan 已放好），不 import 会顺带
      拉起 ModelManager / 引擎 / torch 的依赖模块；
    - torch 版本 / CUDA 标签从 ``RUNTIME.json`` 读，不 import torch 探测。

端点（6 个）::

    GET  /api/downloads/status     整体状态（运行形态 / 环境 / 各模型就位）
    GET  /api/downloads/catalog    可下载组件清单（环境包分卷 + 模型文件）
    POST /api/downloads/start      启动下载任务
    GET  /api/downloads/progress   全部任务进度快照（前端 1s 轮询）
    POST /api/downloads/cancel     请求取消
    POST /api/downloads/uninstall  卸载环境或某个模型的权重
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from ..download_service import (
    build_status,
    catalog_view,
    current_mode,
    get_download_manager,
    runtime_catalog,
    uninstall_model,
    uninstall_runtime,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/downloads", tags=["下载管理"])

# 与 /api/system/shutdown 同一套回环白名单：下载 / 删除是重操作，只认本机
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost", "::ffff:127.0.0.1"})


def _client_config(request: Request) -> Any:
    """取配置对象：优先 lifespan 放在 app.state 的实例，回退全局单例。

    刻意不用 ``Depends(get_config)``：本仓 dependencies 侧一旦引入引擎 / ModelManager，
    依赖注入链就会把 torch 拉进引导态，下载管理页随之 500。
    """
    config = getattr(request.app.state, "config", None)
    if config is not None:
        return config
    from ..config import get_config

    return get_config()


def _deny_remote(request: Request) -> None:
    client_host = (request.client.host if request.client else "") or ""
    if client_host not in LOOPBACK_HOSTS:
        logger.warning("拒绝非本机下载管理请求，来源: %s", client_host or "<unknown>")
        raise HTTPException(status_code=403, detail="仅允许本机调用")


class StartRequest(BaseModel):
    kind: str = Field(description="runtime | model")
    target: str = Field(default="", description="kind=model 时的引擎名")


class ComponentRequest(BaseModel):
    kind: str = Field(description="runtime | model")
    target: str = Field(default="", description="kind=model 时的引擎名")


@router.get("/status")
async def status(request: Request) -> dict:
    """下载管理页的整体状态：运行形态、环境就位情况、各引擎权重就位情况。"""
    return build_status(_client_config(request))


@router.get("/catalog")
async def catalog(request: Request) -> dict:
    """可下载组件清单：环境包（含分卷与校验和）+ 各引擎权重条目。"""
    return catalog_view(_client_config(request))


@router.post("/start")
async def start(request: Request, payload: StartRequest) -> dict:
    """启动一个下载任务。重复调用同一组件时返回既有任务（不会并行下两遍）。"""
    _deny_remote(request)
    kind = payload.kind.strip()
    if kind not in ("runtime", "model"):
        raise HTTPException(status_code=400, detail="kind 必须是 runtime 或 model")
    if kind == "model" and not payload.target.strip():
        raise HTTPException(status_code=400, detail="kind=model 必须指定 target")
    if kind == "runtime":
        entry = runtime_catalog()
        if not entry or not entry.get("volumes"):
            raise HTTPException(
                status_code=503,
                detail="未找到可用的环境包清单（downloads_catalog.json 缺少 volumes），无法确定下载地址",
            )
    task = get_download_manager().start(kind, payload.target.strip())
    return task.to_dict()


@router.get("/progress")
async def progress() -> dict:
    """全部下载任务的进度快照（前端轮询）。"""
    return {"mode": current_mode(), "tasks": get_download_manager().progress()}


@router.post("/cancel")
async def cancel(request: Request, payload: ComponentRequest) -> dict:
    """请求取消：置取消标志，下载循环在下一次读块时退出。"""
    _deny_remote(request)
    component = "runtime" if payload.kind == "runtime" else f"model:{payload.target.strip()}"
    return {"cancelled": get_download_manager().cancel(component)}


@router.post("/uninstall")
async def uninstall(request: Request, payload: ComponentRequest) -> dict:
    """卸载组件：删除 torch 家族包 + RUNTIME.json，或某个引擎的权重文件。"""
    _deny_remote(request)
    kind = payload.kind.strip()
    if kind == "runtime":
        return {"uninstalled": "runtime", **uninstall_runtime()}
    if kind == "model" and payload.target.strip():
        name = payload.target.strip()
        return {
            "uninstalled": f"model:{name}",
            **uninstall_model(name, _client_config(request)),
        }
    raise HTTPException(status_code=400, detail="kind 必须是 runtime 或 model+target")
