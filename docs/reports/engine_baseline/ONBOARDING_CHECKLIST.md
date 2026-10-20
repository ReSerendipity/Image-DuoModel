# 新引擎接入 Checklist（Onboarding Definition of Done）

> 对应 MLOps 评估报告 M8：过去新引擎接入只要求「preflight 能出图」就合入，
> 没有质量门槛。本清单作为 `models.engines.<new>` 合入 main 的硬性 DoD。

## 合入前必须全部完成

- [ ] **权重就位**：`pretrained_models/` 下实际存在 UNet / TE / VAE 三个文件，
      `config.yaml → models.engines.<new>` 的 `sub_path` 指向真实文件，
      `weight_sha256` 字段已填（从 `scripts/generate_weight_manifest.py` 输出复制）。
- [ ] **preflight 真机通过**：`python scripts/preflight_<new_engine>.py` 在目标 GPU 上 rc=0，
      VRAM 峰值不超过 `vram_gb` 声明。
- [ ] **config 校验**：`python scripts/check_config_refs.py` 通过；
      `python scripts/check_spec_refs.py --self` 通过。
- [ ] **单元测试**：至少一个 `tests/native/test_<new_engine>.py` 用 `IMM_FAKE_ENGINE=1`
      覆盖参数 schema / 路径拼装 / sampler 选择逻辑（不依赖真 GPU）。
- [ ] **出图基线**：在 `docs/reports/engine_baseline/<new_engine>/` 下存 3 张样图
      （人物 / 风景 / 复杂构图）+ `meta.json`（weight_sha256、precision、日期、人评）。
- [ ] **GOTCHAS 记录**：接入过程踩的坑（键前缀 / 量化描述符 / 双 TE / latent_channels 等）
      追加到 `docs/agents/GOTCHAS.md`。
- [ ] **README 功能表**：若引擎面向用户，在 `README.md` 功能亮点表加一行。
- [ ] **CHANGELOG**：`CHANGELOG.md` Unreleased 节 Added 段记一条。

## 反例（过去踩过的坑，不要再犯）

- 只写 config 不填 `weight_sha256` → 加载前完整性校验 fail-open，静默放过未登记权重。
- 新引擎没写 `latent_channels` / `latent_downscale` → 错误回退到 Z-Image 的 16/8（commit `f802686` 实录）。
- fp8_e5m2 与 fp8_e4m3fn 混用 → 出图噪点爆炸（config.yaml line 359 注释实录）。
