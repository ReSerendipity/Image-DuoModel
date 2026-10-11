#!/usr/bin/env python3
"""scripts/engine_baseline.py — 引擎固定评估集执行器（NEXT P1-4）

评估集定义：``docs/reports/engine_baseline/prompts.json``（10 条固定 prompt、
seed=42、固定分辨率/参数）。本脚本在发版或换权重前后运行，产物按
``docs/reports/engine_baseline/runs/<YYYYMMDD>/<engine>/`` 归档（PNG + meta.json），
供质量回归与漂移对比（对应 engine_baseline README 的"固定评估集"落地）。

两种模式:
- ``--dry-run``（默认）: 只读校验——评估集文件完整（10 条、seed 固定）、引擎在
  config 注册、引擎权重引用可解析、归档目录可写。无 GPU 依赖，CI/本机可直接跑。
- ``--run``: 通过正在运行的本地服务（FastAPI :8288）逐条生成并归档。
  真实推理需 GPU 环境（本机红线不强跑，由 GPU runner / 人工触发）。

用法::

    python scripts/engine_baseline.py --dry-run
    python scripts/engine_baseline.py --run --base-url http://127.0.0.1:8288 --engines flux2_klein_native
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BASELINE_DIR = Path(REPO_ROOT) / "docs" / "reports" / "engine_baseline"
PROMPTS_FILE = BASELINE_DIR / "prompts.json"
EXPECTED_PROMPT_COUNT = 10
EXPECTED_SEED = 42


def load_eval_set() -> dict:
    """加载并校验评估集定义；异常时抛 ValueError。"""
    if not PROMPTS_FILE.is_file():
        raise ValueError(f"评估集文件缺失: {PROMPTS_FILE}")
    data = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))
    prompts = data.get("prompts", [])
    if len(prompts) != EXPECTED_PROMPT_COUNT:
        raise ValueError(f"评估集应为 {EXPECTED_PROMPT_COUNT} 条 prompt，实际 {len(prompts)}")
    if data.get("seed") != EXPECTED_SEED:
        raise ValueError(f"评估集 seed 应为 {EXPECTED_SEED}，实际 {data.get('seed')}")
    ids = [p.get("id") for p in prompts]
    if sorted(ids) != list(range(1, EXPECTED_PROMPT_COUNT + 1)):
        raise ValueError(f"prompt id 应连续 1..{EXPECTED_PROMPT_COUNT}，实际 {ids}")
    for p in prompts:
        if not p.get("name") or not p.get("prompt"):
            raise ValueError(f"prompt {p.get('id')} 缺少 name/prompt")
    return data


def _resolve_engine_refs(cfg) -> dict[str, dict]:
    """复用运行时同一解析函数（config_models.resolve_model_path），返回引擎引用可解析性。"""
    from app.integrated_app.config_models import ModelPaths, resolve_model_path

    out: dict[str, dict] = {}
    for name, engine in cfg.models.engines.items():
        refs = []
        for attr in ("text_encoder", "unet", "vae"):
            mp: ModelPaths | None = getattr(engine, attr, None)
            if not mp or not mp.sub_path:
                continue
            for m in [mp] + list(mp.sub_paths or []):
                if m and m.sub_path:
                    p = resolve_model_path(m, cfg.models, cfg.project_root)
                    refs.append({"role": attr, "path": p, "exists": Path(p).is_file()})
        out[name] = {"refs": refs}
    return out


def dry_run(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="引擎评估集 dry-run（只读校验）")
    args = ap.parse_args(argv)

    ok = True

    # 1) 评估集完整性
    try:
        data = load_eval_set()
        print(f"[OK] 评估集: {PROMPTS_FILE.name}（{len(data['prompts'])} 条 prompt，seed={data['seed']}）")
    except ValueError as e:
        print(f"[FAIL] 评估集校验失败: {e}")
        return 1

    # 2) 引擎注册 + 权重引用可解析
    try:
        from app.integrated_app.config import load_validated_config

        cfg = load_validated_config()
        engines = cfg.models.engines
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] config 加载失败: {e}")
        return 1

    for name in data["engines"]:
        if name not in engines:
            print(f"[FAIL] 评估集引擎未在 config 注册: {name}")
            ok = False
    refs = _resolve_engine_refs(cfg)
    for name in data["engines"]:
        missing = [r for r in refs[name]["refs"] if not r["exists"]]
        if missing:
            for r in missing:
                print(f"[FAIL] {name}.{r['role']} 权重引用不可解析: {r['path']}")
            ok = False
        else:
            print(f"[OK] {name}: {len(refs[name]['refs'])} 个权重引用全部可解析")

    # 3) 归档目录可写
    run_dir = BASELINE_DIR / "runs" / date.today().strftime("%Y%m%d")
    try:
        run_dir.mkdir(parents=True, exist_ok=True)
        probe = run_dir / ".probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        print(f"[OK] 归档目录可写: {run_dir}")
    except OSError as e:
        print(f"[FAIL] 归档目录不可写: {run_dir} ({e})")
        ok = False

    print("-" * 60)
    print("dry-run 结论:", "PASS（评估集可用）" if ok else "FAIL（存在阻断项）")
    return 0 if ok else 1


def run(argv: list[str] | None = None) -> int:
    """真实推理：通过本地服务逐条生成并归档。需 GPU 环境 + 服务已启动。"""
    ap = argparse.ArgumentParser(description="引擎评估集真实推理（需 GPU + 本地服务运行中）")
    ap.add_argument("--base-url", default="http://127.0.0.1:8288")
    ap.add_argument("--engines", nargs="+", default=None, help="默认取评估集 engines 全部")
    args = ap.parse_args(argv)

    import urllib.parse
    import urllib.request

    data = load_eval_set()
    engines = args.engines or data["engines"]

    # 服务探活
    try:
        with urllib.request.urlopen(args.base_url + "/api/system/health", timeout=5) as r:
            if r.status != 200:
                print(f"[FAIL] 服务未就绪: {args.base_url}", file=sys.stderr)
                return 1
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 无法连接本地服务 {args.base_url}: {e}", file=sys.stderr)
        print("提示：需先启动服务（start.bat）且具备 GPU 环境。", file=sys.stderr)
        return 1

    run_dir = BASELINE_DIR / "runs" / date.today().strftime("%Y%m%d")
    run_dir.mkdir(parents=True, exist_ok=True)

    failed: list[str] = []
    for engine in engines:
        engine_dir = run_dir / engine
        engine_dir.mkdir(parents=True, exist_ok=True)
        meta: list[dict] = []
        for p in data["prompts"]:
            body = json.dumps(
                {
                    "prompt": p["prompt"],
                    "engine_name": engine,
                    "width": data["defaults"]["width"],
                    "height": data["defaults"]["height"],
                    "cfg": data["defaults"]["cfg"],
                    "steps": data["defaults"]["steps"],
                    "seed": data["seed"],
                }
            ).encode("utf-8")
            req = urllib.request.Request(
                args.base_url + "/api/generate",
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    task = json.loads(r.read().decode("utf-8"))
                task_id = task.get("task_id")
                if not task_id:
                    failed.append(f"{engine}/{p['name']}: 无 task_id")
                    continue
                # 轮询任务直到完成（简单超时 300s）
                deadline = time.time() + 300
                out_paths: list[str] = []
                while time.time() < deadline:
                    with urllib.request.urlopen(
                        args.base_url + "/api/tasks/" + urllib.parse.quote(task_id), timeout=10
                    ) as r:
                        detail = json.loads(r.read().decode("utf-8"))
                    st = detail.get("status")
                    if st == "completed":
                        out_paths = [o.get("path", "") for o in (detail.get("outputs") or []) if o.get("path")]
                        break
                    if st in ("failed", "cancelled"):
                        failed.append(f"{engine}/{p['name']}: {st}")
                        break
                    time.sleep(3)
                meta.append(
                    {
                        "id": p["id"],
                        "name": p["name"],
                        "prompt": p["prompt"],
                        "task_id": task_id,
                        "status": st if "st" in locals() else "timeout",
                        "outputs": out_paths,
                    }
                )
            except Exception as e:  # noqa: BLE001
                failed.append(f"{engine}/{p['name']}: {e}")
        meta_file = engine_dir / "meta.json"
        meta_file.write_text(json.dumps({"engine": engine, "seed": data["seed"], "items": meta}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{len(meta) - len([m for m in meta if m.get('status') in ('failed','cancelled','timeout')])}/{len(meta)}] {engine} -> {engine_dir}")

    print("-" * 60)
    if failed:
        print("失败项:")
        for f in failed:
            print(f"  - {f}")
        return 1
    print("全部完成，归档于:", run_dir)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="引擎固定评估集执行器（NEXT P1-4）")
    ap.add_argument("--dry-run", action="store_true", help="只读校验（默认行为）")
    ap.add_argument("--run", action="store_true", help="真实推理（需 GPU + 本地服务）")
    args, rest = ap.parse_known_args(argv)

    if args.run:
        return run(rest)
    return dry_run(rest)


if __name__ == "__main__":
    raise SystemExit(main())
