# Image-DuoModel 许可证合规台账（License Compliance）

> 最后更新：2026-08-27（家族治理 Phase D6，实测枚举）。
> ⚠️「商用合规 / 合规要求」两列仅记录**事实与风险提示**，不构成法律意见；标「需人工确认」者必须人工补查后再分发。

## 1. 主程序许可

| 组件 | 许可证 | 商用合规 | 合规要求 |
|---|---|---|---|
| Image-DuoModel 项目代码 | Apache-2.0（以根级 LICENSE 为准） | 宽松许可 | 保留版权声明与 NOTICE |

## 2. 内嵌 ComfyUI 内核（`comfy_kernel/`）

| 组件 | 许可证 | 商用合规 | 合规要求 |
|---|---|---|---|
| `comfy_kernel/`（上游 ComfyUI 内核，含 `comfy/`、`comfy_extras/`、`comfy_execution/` 等） | GPL-3.0（上游） | ⚠️ 传染风险；`config.yaml → models.engines.*` 全部 7 个引擎均为 `backend: native`，进程内复用该内核 | 保留上游版权；本仓唯一形态即进程内复用，**无「不加载内核」的替代引擎路径** |
| `comfy_kernel/custom_nodes/` | **无第三方节点包**（仅 `example_node.py.example` 示例与 `websocket_image_save.py` 内部脚本） | — | 新增第三方节点必须同步补入本台账 |

> 完整第三方组件说明（含 Z-Image Turbo、diffusers 等核心引擎）见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本台账仅记录**随仓内嵌**组件的许可矩阵。native（进程内复用 `comfy_kernel/`）是当前**默认且唯一**的引擎形态——自 v1.2.0 起已完全脱离外部 ComfyUI 进程（见根 `README.md`「原生进程内引擎」），`config.yaml → models.engines.*` 全部 7 个引擎均为 `backend: native`；`app/integrated_app/native/diffusers_engine.py` 是框架内的一个实现分支，不是「替代/迁移目标」。

## 3. 模型权重

| 组件 | 许可证 | 商用合规 | 合规要求 |
|---|---|---|---|
| Z-Image-Turbo 权重（`pretrained_models/`，即 `config.yaml → models.portable.internal_models_dir`，用户自行下载获得） | Apache-2.0（HuggingFace 模型卡） | 可随便携包分发 | 保留模型卡版权与免责声明 |

## 4. 维护约定

- 新增/升级任何随仓内嵌组件（comfy_kernel 或节点包），**必须**同步更新本台账与 THIRD_PARTY_NOTICES.md。
- 复核命令（只读）：`Get-ChildItem comfy_kernel/custom_nodes -Directory`（当前为空）。
