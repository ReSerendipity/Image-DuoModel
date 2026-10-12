#!/usr/bin/env python3
"""scripts/check_model_links.py — 引擎权重引用可解析性探针（NEXT P0-1）

portable 模式下运行时从 ``pretrained_models/``（经 Junction/Symlink 指向外部
模型库）解析引擎权重。本脚本**复用运行时同一解析函数**（``resolve_model_path`` /
``resolve_engine_model_paths``，见 ``config_models.py``），对 config.yaml 注册的
全部引擎做「引用 → 文件存在性」检查，防止链接悬空 / 文件缺失到加载时才暴露
（与 GOTCHAS #43 同类问题）。

覆盖范围：
- 每个引擎的 text_encoder / unet / vae 主权重（``sub_path``）；
- 附加权重（``sub_paths``，如 FLUX.1-dev 的 clip_l 挂 ``models/clip/`` 下）。

用法::

    python scripts/check_model_links.py                  # 全量；有缺失 exit 1
    python scripts/check_model_links.py --engine flux2_klein_native  # 单引擎
    python scripts/check_model_links.py --json          # JSON 输出（CI 友好）

退出码: 0=全部可解析；1=存在缺失引用；2=参数/配置错误。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from pathlib import Path

from app.integrated_app.config import load_validated_config
from app.integrated_app.config_models import ModelPaths, resolve_model_path


def _check_one(mp: ModelPaths, cfg, label: str, out: list[dict]) -> None:
    """解析单个 ModelPaths 并记录存在性。"""
    p = resolve_model_path(mp, cfg.models, cfg.project_root)
    exists = Path(p).is_file()
    out.append(
        {
            "engine": label[0],
            "role": label[1],
            "path": p,
            "exists": exists,
        }
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="引擎权重引用可解析性探针")
    parser.add_argument("--engine", default=None, help="只检查指定引擎（默认全部）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args(argv)

    cfg = load_validated_config()
    engines = cfg.models.engines
    if args.engine and args.engine not in engines:
        print(f"[error] 引擎不存在: {args.engine}", file=sys.stderr)
        return 2

    results: list[dict] = []
    for name, engine in engines.items():
        if args.engine and name != args.engine:
            continue
        for attr in ("text_encoder", "unet", "vae"):
            mp: ModelPaths | None = getattr(engine, attr, None)
            if not mp or not mp.sub_path:
                continue
            _check_one(mp, cfg, (name, attr), results)
            for extra in mp.sub_paths or []:
                if extra and extra.sub_path:
                    _check_one(extra, cfg, (name, f"{attr}+"), results)

    missing = [r for r in results if not r["exists"]]
    if args.json:
        print(json.dumps({"total": len(results), "missing": missing}, ensure_ascii=False, indent=2))
        return 1 if missing else 0

    for r in results:
        flag = "OK  " if r["exists"] else "MISS"
        print(f"[{flag}] {r['engine']:24s} {r['role']:12s} {r['path']}")
    print("-" * 80)
    print(f"引擎引用权重总数: {len(results)}，缺失: {len(missing)}")
    for r in missing:
        print(f"  MISSING {r['engine']}.{r['role']}: {r['path']}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
