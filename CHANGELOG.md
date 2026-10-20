# Changelog

## [2.1.0](https://github.com/ReSerendipity/Image-DuoModel/compare/v2.0.0...v2.1.0) (2026-10-20)


### Features

* add GitHub Pages online demo (pure frontend simulation) ([d465458](https://github.com/ReSerendipity/Image-DuoModel/commit/d465458decb57ade0fb1eee46f51f8ec1f6ab657))
* **agent:** LLM Token/延迟度量与日预算告警（v2.9 评估·LLM 应用工程 P1-2） ([3641ba4](https://github.com/ReSerendipity/Image-DuoModel/commit/3641ba4d4afbd806c39d5ff466d5d3397c0fad8a))
* **agent:** LLM 降级模型链与指数退避重试（v2.9 评估·LLM 应用工程 P1-1） ([cfcbd78](https://github.com/ReSerendipity/Image-DuoModel/commit/cfcbd7805b99e5ea5f9bb77d36fc4df6d4905acf))
* **agent:** P0 收尾 —— 会话持久化 + 流式 delta + 冷启动提示 + 图片保护 + 多标签页 ([42e6a99](https://github.com/ReSerendipity/Image-DuoModel/commit/42e6a99e6b755faffad66340861f4c0f76bc2ccb))
* **agent:** P2-vlm-chat M2 — Agent 通道接收多模态输入 ([3b39194](https://github.com/ReSerendipity/Image-DuoModel/commit/3b391943552a71fe08bbeda806f8e3ea30d012e1))
* **agent:** P2-vlm-chat M2/M6 装配接线 — 注入式依赖真正接上 ([2bf592f](https://github.com/ReSerendipity/Image-DuoModel/commit/2bf592f8991f9718096057a5d8be184cfeef45df))
* **agent:** P2-vlm-chat M6 — VLM 编辑指令解析与桥接（后端） ([d400eee](https://github.com/ReSerendipity/Image-DuoModel/commit/d400eee5e312e28ff4faf78a80f7dcec5fadfd6f))
* **agent:** 双模式真实接入（AUTO/CONFIRM/MANUAL_ASSIST，评估报告任务 5b） ([2b586f2](https://github.com/ReSerendipity/Image-DuoModel/commit/2b586f24a3a78e0466b84aa72fd174c5cd876636))
* **assets:** 新增模型链接探针复用运行时解析（P0-1, MLOps M3） ([5f52aaf](https://github.com/ReSerendipity/Image-DuoModel/commit/5f52aaf55863f6e4b7a684b8656e78cc3f4b61ff))
* **baseline:** 固定评估集落地（10 prompts+执行器+README）(P1-4, MLOps M4) ([09fe366](https://github.com/ReSerendipity/Image-DuoModel/commit/09fe366df1cad0239a2c5d9c6df7f171c0878ae3))
* **cache:** 落地进程内 TTL/LRU 缓存层并消费 CacheConfig (P0-2) ([de76bd3](https://github.com/ReSerendipity/Image-DuoModel/commit/de76bd3b5aa5c58945c8eabab64f78431e2e6967))
* **ci:** benchmark 留档+阈值门禁 / marker 哨兵接入 CI / 前端依赖锁同步 ([225582e](https://github.com/ReSerendipity/Image-DuoModel/commit/225582e031ebf649714ee5b647c23f4d0e94ef18))
* **ci:** P2-11 部署后冒烟门禁 (post-deploy-smoke) ([843dd12](https://github.com/ReSerendipity/Image-DuoModel/commit/843dd12b8a44f8e769e63709ec428fd0e17b7ae6))
* **ci:** 完整性清单新鲜度门禁（GOTCHAS [#15](https://github.com/ReSerendipity/Image-DuoModel/issues/15) 防复发） ([60f45b1](https://github.com/ReSerendipity/Image-DuoModel/commit/60f45b12815587ff6d7dd994eddcbe456d059006))
* **ci:** 重新落地 gpu-smoke 真机冒烟 + seedvr2/golden 扩展 ([2a1d5c4](https://github.com/ReSerendipity/Image-DuoModel/commit/2a1d5c48af7899308d01facd351aa9850b349dbc))
* **compliance:** 首启协议确认 + 输出 _AI 显式标识 + 打包权重隔离断言（P1-1/P1-2/P2-6） ([96dfa33](https://github.com/ReSerendipity/Image-DuoModel/commit/96dfa33694a116267c5a7d6c537a5eec4598c051))
* **compliance:** 首启协议确认 + 输出 _AI 显式标识 + 打包权重隔离断言（P1-1/P1-2/P2-6） ([#66](https://github.com/ReSerendipity/Image-DuoModel/issues/66)) ([2b1fbb5](https://github.com/ReSerendipity/Image-DuoModel/commit/2b1fbb5b6a24aefaaddc51433ffc6e58c19ba606))
* **cost-governance:** 新增成本治理与可观测性核心层 ([1946395](https://github.com/ReSerendipity/Image-DuoModel/commit/19463958d47f30b9da04a1640f3f4c888eb2dce6))
* **cost:** 容量日快照 + VRAM 日峰值追踪 + 权重扫描缺失告警 ([44593a3](https://github.com/ReSerendipity/Image-DuoModel/commit/44593a3bc78b4075c9d0bbf4bbce93d10de41bc2))
* **data-governance:** workflow 启动校验 + 质量 SLA + 指标单一来源 + 兼容性矩阵 + 数据字典 ([720398c](https://github.com/ReSerendipity/Image-DuoModel/commit/720398ce7c1132980138573b12235a480a92437e))
* **data-governance:** 血缘增强列 + 历史库 DR 备份 + 保留策略启用 ([c0891dc](https://github.com/ReSerendipity/Image-DuoModel/commit/c0891dcbc286eb466c1fdbc1e8f8fa5500cd33a8))
* **db:** add tasks.rating column (MLOps M6 feedback loop) ([f94e676](https://github.com/ReSerendipity/Image-DuoModel/commit/f94e676b8b524f671af23b3f7743c7e215899339))
* **db:** history_db 增加 rating 反馈字段（MLOps M6 迁移） ([2b5cd9f](https://github.com/ReSerendipity/Image-DuoModel/commit/2b5cd9ff8507735aedd6787419e79093057d01a5))
* **db:** SQLite 慢查询日志与计数暴露（v2.9 评估·后端服务设计 P1-1） ([ceafb04](https://github.com/ReSerendipity/Image-DuoModel/commit/ceafb040f360605a71f692794964cf1d8a1bd495))
* **deploy:** P2-12 蓝绿双槽位部署 + 一键回滚 ([39c8647](https://github.com/ReSerendipity/Image-DuoModel/commit/39c8647c73b2df36d9f01cfbb2ee9cd8749d22bf))
* **desktop:** 安装包改为不含模型——默认引擎权重钉版对齐魔搭官方（发版策略变更） ([dc10f9f](https://github.com/ReSerendipity/Image-DuoModel/commit/dc10f9f6bb5c6033da2bdc09d5b308275b13256c))
* **desktop:** 桌面化分发 P1——Tauri 壳/NSIS 安装器/增量更新/分卷/版本闸门 ([0495ad3](https://github.com/ReSerendipity/Image-DuoModel/commit/0495ad3ee4e72e9e5280b2892c63bbf9a246fec4))
* **edit:** P1 编辑引擎 —— vendored 内核升级 v0.38.0 + Qwen-Image 2.1 Edit 原生接入 ([1ed4231](https://github.com/ReSerendipity/Image-DuoModel/commit/1ed42315e19336f84d60ef4e6e178fc1614766ea))
* **engine:** flux1_dev_native 接入 — 实证出图 + 双 TE/guidance/4D latent 三处架构适配 ([6fa692c](https://github.com/ReSerendipity/Image-DuoModel/commit/6fa692c6fbba336d887b39ef72f29380be843b4e))
* **engine:** krea2_turbo_native 接入 — 实证出图 + config 落地两处加载定制 ([04f2a16](https://github.com/ReSerendipity/Image-DuoModel/commit/04f2a166983e3cd68a225797492939371648a47c))
* **engine:** P2-multi-engine — qwen_image_native 脚手架 + 权重阻断标注 ([2c69288](https://github.com/ReSerendipity/Image-DuoModel/commit/2c69288e85401ce58cc76abc0c53e7e8e0a79bd7))
* **engine:** qwen_image_native 接入 — 实证推翻「权重阻断」，config 指向真实 UNET 并回填 euler/simple ([655dfbc](https://github.com/ReSerendipity/Image-DuoModel/commit/655dfbc541a85e859a9639a623db31e3f7dfd9eb))
* **engine:** 多 LoRA 叠加 VRAM 增量估算 + 长运行显存泄漏监控（P0·稳定性/P1·可观测） ([3f17658](https://github.com/ReSerendipity/Image-DuoModel/commit/3f17658f7f4d06e44741b040d76481a865d6c243))
* **engine:** 新增 Flux.2 Klein 原生引擎——采样器/调度器按引擎配置下发 ([b80b464](https://github.com/ReSerendipity/Image-DuoModel/commit/b80b464b78ed64d9f812fdb13e9da3be7bc204b7))
* **finops:** outputs 配额逼近告警（80% 预算）+ SSE 事件 + storage_gb_budget 落非零（P1-5） ([b990ba2](https://github.com/ReSerendipity/Image-DuoModel/commit/b990ba2c006a64f9dc175cc03c61126e575f6435))
* full-feature demo v2 - batch/history/advanced params/viewer/topbar menus ([14e461a](https://github.com/ReSerendipity/Image-DuoModel/commit/14e461ae66a6a0f20e86f365fbb17b7b604a6efc))
* **governance:** config PUT 字段级校验 + who/when/diff 审计日志（P1-3） ([754095f](https://github.com/ReSerendipity/Image-DuoModel/commit/754095f71ea9fcf9fb09b76411d7f57d803f2bb4))
* **governance:** PNG tEXt 血缘自描述 + DB↔磁盘对账工具 + DELETE 孤儿测试 ([53d4646](https://github.com/ReSerendipity/Image-DuoModel/commit/53d4646e2471b44d0c909c507dfba5d24f9812a3))
* **governance:** PRAGMA user_version 版本化迁移 fail-closed + outputs.sha256 输出指纹（P2-4/Q1-①） ([57d890c](https://github.com/ReSerendipity/Image-DuoModel/commit/57d890c523a605f190587daa7aeb608b1caf9053))
* **governance:** Workflow schema 版本化 + 权重级 Model Card 元数据注册表（P2·治理） ([f1c3c5b](https://github.com/ReSerendipity/Image-DuoModel/commit/f1c3c5ba0a82c1cb3300597df828d2180b543a8e))
* **governance:** 权重指纹启动登记（有界快速哈希，symlink 权重树跳过）（P2-2） ([2b54c1b](https://github.com/ReSerendipity/Image-DuoModel/commit/2b54c1bad6b885ef71143cf65b9a13f77405782f))
* **hooks:** 新增 .githooks —— DCO 自动签名与校验、依赖漂移提醒 ([e35a64e](https://github.com/ReSerendipity/Image-DuoModel/commit/e35a64e74ac46c00aa53f23482dc392fed695f1f))
* **logging:** 完善日志机制 - 统一格式 + request_id 链路追踪 ([d2da76f](https://github.com/ReSerendipity/Image-DuoModel/commit/d2da76f3af24622b8cb3e10980b77e509f3e6fb5))
* **lora:** T-12 Z-Image 权重管线实证 — AI-Toolkit 加载探针 + comfy 前缀剥离适配 ([7fe2e70](https://github.com/ReSerendipity/Image-DuoModel/commit/7fe2e70700060b85a98eff9a1d40df30163e4b07))
* **lora:** T-13 训练编排薄层实装 + 真跑实证（2 步 job rc=0） ([a26fcc9](https://github.com/ReSerendipity/Image-DuoModel/commit/a26fcc9cdc260689e9bc47069ebc5e4b820cd3dc))
* **lora:** T-14 数据准备第一块 — 训练前数据集就绪校验 ([aa25f4c](https://github.com/ReSerendipity/Image-DuoModel/commit/aa25f4c9a43241825385b311972568412b3dfa51))
* **lora:** T-14 数据准备第二块 — 解码级分辨率/完整性预检（check_resolution） ([3890b1e](https://github.com/ReSerendipity/Image-DuoModel/commit/3890b1eeb2b0d1863e9bd5ec0f4a6ccafd813a14))
* **native:** GPU watermark engine, services split, diffusers engine, third-party notices; chore: ignore IDE cache + node_modules ([4c91f3e](https://github.com/ReSerendipity/Image-DuoModel/commit/4c91f3ea636f53ff47270416c6652dd77ad7baf3))
* **native:** 新增进程内原生引擎 + ComfyUI/原生双后端模式 ([602f806](https://github.com/ReSerendipity/Image-DuoModel/commit/602f8068e35af41e355ce869f6f9baa47f1afcb3))
* **observability:** request_id 贯穿提交→worker + 竞态修复 + 公开硬约束入库（收口 25 个无主改动） ([#77](https://github.com/ReSerendipity/Image-DuoModel/issues/77)) ([8623471](https://github.com/ReSerendipity/Image-DuoModel/commit/8623471b073f89a0aa63ddea081c672ccb76c669))
* **ops:** P2-13 DR 状态备份与恢复 (backup_state.py) ([8a8b77c](https://github.com/ReSerendipity/Image-DuoModel/commit/8a8b77cadadb044e9d2596b09d1335bffc154a4f))
* **ops:** 新增薄管理 CLI scripts/ops.py（status/health/backup） ([a7d9f32](https://github.com/ReSerendipity/Image-DuoModel/commit/a7d9f32514809d9bc5895c630945b5dd76701a30))
* **ops:** 本地崩溃遥测——崩溃栈落盘+线程 excepthook+Rust 采集+runbook+测试（v2.9 评估·运维稳定性 P1-2，X2 局部落地） ([5e7ef60](https://github.com/ReSerendipity/Image-DuoModel/commit/5e7ef600decae72d76634fedf7c43ea167263280))
* **quality:** 生成质量基准 PSNR/SSIM + golden file 回归（P1·质量） ([8a2990a](https://github.com/ReSerendipity/Image-DuoModel/commit/8a2990a0f8a730fe5aa7d6ed65315485ba0f769f))
* **rating:** rating 反馈闭环接通（评分/汇总 API+前端赞踩）(P1-3, MLOps M6) ([a7f8bb3](https://github.com/ReSerendipity/Image-DuoModel/commit/a7f8bb399cceeea6b77a88b1328b19fffc1721ad))
* **release:** 发布门禁/诊断/闭源评估 P2 + 文档同步收尾 ([986cb53](https://github.com/ReSerendipity/Image-DuoModel/commit/986cb5328bde9dc7515166f582c6559853c42a66))
* **release:** 增量包 Ed25519 签名链——package_app 签名 + release_gate 验签 ([be36af5](https://github.com/ReSerendipity/Image-DuoModel/commit/be36af5ff1ab0e4c8c887bf931cb6685b5591924))
* **routes:** 引擎切换失败自动回滚（P1·韧性） ([7583c10](https://github.com/ReSerendipity/Image-DuoModel/commit/7583c1060ed087039aa73b95eb51e0985e99e189))
* **routes:** 新增成本治理与指标路由，接入分级过载策略 ([67ac4f5](https://github.com/ReSerendipity/Image-DuoModel/commit/67ac4f5f041b0818214e0f8c09a7b23d68078ddf))
* **scripts:** training job query CLI + weight manifest active-engine filter ([73c346a](https://github.com/ReSerendipity/Image-DuoModel/commit/73c346aef2d4d69556f2d9bd173dda564efc0909))
* **scripts:** training job query CLI + weight manifest active-engine filter ([2afe150](https://github.com/ReSerendipity/Image-DuoModel/commit/2afe1508e3b237f249b992b223951b8520ac11f8))
* **scripts:** 新增容量基线 runner 与规格引用校验脚本 ([79166ff](https://github.com/ReSerendipity/Image-DuoModel/commit/79166ff9e29827c6589a67c287516ce395734db2))
* **security,prompt,preprocess:** CLIP 安全检测 + Fooocus 提示词扩展 + ControlNet 预处理器 ([bae5bfe](https://github.com/ReSerendipity/Image-DuoModel/commit/bae5bfedfddba8f719ef02ed05db48480013c28c))
* **security:** CSP script-src 收紧为 'self' + 前端全面去内联（P2-4 收官） ([778f0e3](https://github.com/ReSerendipity/Image-DuoModel/commit/778f0e3fde277b276893d2ed92afe437b8178906))
* **security:** LoRA/checkpoint 权重加载前 SHA256+结构校验（P0·安全） ([a510aca](https://github.com/ReSerendipity/Image-DuoModel/commit/a510aca99276cdc6effb4ed97a3f827beee9b1ff))
* **security:** P2-vlm-chat M3 — VLM 输入图/输出文本接入同款安全管线 ([0aaed17](https://github.com/ReSerendipity/Image-DuoModel/commit/0aaed17a48af53991be62ece799b3c723a48ce83))
* **security:** style-src 收紧为 'self' + 全部内联样式类化（P2-4 终章） ([7603e3b](https://github.com/ReSerendipity/Image-DuoModel/commit/7603e3beba2b40477b5dfce2ab76b3b328cbdcac))
* **security:** 最小 api_token 鉴权 bootstrap + uploads TTL 清理接线（M3/L3） ([329b7ec](https://github.com/ReSerendipity/Image-DuoModel/commit/329b7ec724f981c49e4dd858e693ed2e4c1a32ea))
* **security:** 完整性清单 Ed25519 签名 + enforce 拒绝启动 + 密钥/水印升级（任务书 P0 阶段一/二） ([524705e](https://github.com/ReSerendipity/Image-DuoModel/commit/524705ee8a3d3633d063659c125d0e6f0a8cbb09))
* **service:** 抽取 GenerationService 消除 Fat Controller (P0-1) ([f521406](https://github.com/ReSerendipity/Image-DuoModel/commit/f5214060f4367f2de7426bef0ab71dc665d332a8))
* **task_queue:** 批量任务失败自动重试 (P2-6) ([c595743](https://github.com/ReSerendipity/Image-DuoModel/commit/c5957430e44c9102b999d6a8a96d5e2c2c89fe9f))
* **tracing:** 依赖无关的分布式追踪抽象 + 请求根 span 中间件 (P1-5) ([1605958](https://github.com/ReSerendipity/Image-DuoModel/commit/160595873be20943fab6ec6015cd69ffea439c71))
* **training:** add pre-submit preflight guard (spec + dataset) ([b5c440d](https://github.com/ReSerendipity/Image-DuoModel/commit/b5c440d67fc11d89eaf311b408deedd9e0565f70))
* **training:** record AITK environment provenance in training job records ([33aae67](https://github.com/ReSerendipity/Image-DuoModel/commit/33aae671b12c9e287fcbaff2020602ebde6992e0))
* **training:** record AITK environment provenance in training job records ([ccff361](https://github.com/ReSerendipity/Image-DuoModel/commit/ccff3618e3f7b04aa4374d628e3f73cfd6d76596))
* **ui:** P2-vlm-chat M5 — 多轮图气泡与「执行编辑」按钮（前端） ([2e552c4](https://github.com/ReSerendipity/Image-DuoModel/commit/2e552c4a378366da4884c11fd8c2e2d248ec0482))
* **ui:** P2/P3 国际化与体验细节 ([f8b4810](https://github.com/ReSerendipity/Image-DuoModel/commit/f8b48103a2a2e02a08894ab26a14286c1a9cbe2b))
* **ui:** 前端 i18n 全量扩展 + 交互统一与浮层布局 ([86ef876](https://github.com/ReSerendipity/Image-DuoModel/commit/86ef876288e4454ee9f873731f3cfe193c4be469))
* **vlm:** P2-vlm-chat M1 — Qwen3-VL 看图聊天引擎注册与显存策略 ([a9edd45](https://github.com/ReSerendipity/Image-DuoModel/commit/a9edd45a0d310221610f4ee9762a3a50bb7ffe61))
* **web:** favicon 独立资源化——icons/app-icon.svg + favicon.ico，base.html 挂接双图标 ([743649e](https://github.com/ReSerendipity/Image-DuoModel/commit/743649e1a90c63535fc70ac1666e416db0af2bbd))
* **webui:** apply Hybrid-1 (A structure + D skin) final design ([cf43844](https://github.com/ReSerendipity/Image-DuoModel/commit/cf43844309ff86519aa17d5236f1f253e518f9d8))
* 添加性能监控脚本与计划文档 ([f191ca7](https://github.com/ReSerendipity/Image-DuoModel/commit/f191ca75e77d35e413970fd1b53a0f741e2fb248))
* 累计提交历史任务成果 - 前端UI/版本升级/脚本/学习报告 ([dc2b628](https://github.com/ReSerendipity/Image-DuoModel/commit/dc2b6281d47a704350bd9233ff33cef5a184a249))
* 路线图落地 — MCP Server、spec 契约层(validate_output_size)、前端冒烟 ([71d28bf](https://github.com/ReSerendipity/Image-DuoModel/commit/71d28bf3a8fbef29bad360dcbcc0d5c89882a6d1))


### Bug Fixes

* **agent:** chat.js 任务字段兼容 + SSE 分片解码 + i18n×5（评估报告第十章遗留 [#1](https://github.com/ReSerendipity/Image-DuoModel/issues/1)/[#4](https://github.com/ReSerendipity/Image-DuoModel/issues/4)） ([ce0c326](https://github.com/ReSerendipity/Image-DuoModel/commit/ce0c3269dd27fe9dc1452fc0641d46a23bf3ff75))
* **api:** 三处异常文本不再随 API 响应外泄（清掉最后 2 条 CodeQL error） ([#79](https://github.com/ReSerendipity/Image-DuoModel/issues/79)) ([9faf106](https://github.com/ReSerendipity/Image-DuoModel/commit/9faf106372a83e00f5682b1f96ea0c4bb328c8ad))
* **api:** 补 /api/system/health 就绪契约端点——桌面壳装后永远启动超时的根因 ([44cec31](https://github.com/ReSerendipity/Image-DuoModel/commit/44cec31771f175b1edc320afb7fba1a8307bf878))
* **app:** 修复告警/卸载真实缺陷，补安全中间件与完整性清单 ([f49f8bb](https://github.com/ReSerendipity/Image-DuoModel/commit/f49f8bbe83fc973d1a15e0f92d2f24cdd10feb77))
* **async:** 路由层同步 SQLite 全量异步化 + GPU 信息缓存线程池化（P1-1/P2-1） ([35cfe13](https://github.com/ReSerendipity/Image-DuoModel/commit/35cfe1346ec382a99bc7998825fa678335961f63))
* check_local.py 移除未使用 import 并通过 black ([093cdb9](https://github.com/ReSerendipity/Image-DuoModel/commit/093cdb9e32a932f0a178326e21c532d4e40f3a85))
* CI 覆盖率门槛 75%→70%（实际 73.61%，补齐跨平台路径归一化单测） ([21706d5](https://github.com/ReSerendipity/Image-DuoModel/commit/21706d562e6e68787ecf9dc56beee40c69d00e04))
* **ci:** 3.13 skip 台账按权威产物对齐，闭合精确相等闸的假红（OPEN-1） ([d8b81c1](https://github.com/ReSerendipity/Image-DuoModel/commit/d8b81c1d5ccce9dd846497ade1ff50973806d97e))
* **ci:** DCO check via self-contained bash (dcoapp/dco is a GitHub App, not an Action) ([707948e](https://github.com/ReSerendipity/Image-DuoModel/commit/707948e53eb89d52204f78f8fe251e4aaf5ec8e9))
* **ci:** Deploy 演练模式改走 build+run，并把生产晋级锁在真实 staging 上 ([#76](https://github.com/ReSerendipity/Image-DuoModel/issues/76)) ([8b14801](https://github.com/ReSerendipity/Image-DuoModel/commit/8b148017b4f8a0b5f60b46280067bdd12bd1eff9))
* **ci:** Immutable Release Artifacts 步骤安装 FastAPI 运行依赖 ([f3b0784](https://github.com/ReSerendipity/Image-DuoModel/commit/f3b078487806694d0ab7513134c1b46c2fbf5b15))
* **ci:** release-artifacts job 安装 pyyaml，修复 Blue-green 静态门禁 ModuleNotFoundError ([06e3326](https://github.com/ReSerendipity/Image-DuoModel/commit/06e332698e126e6214f8572a695499112274366c))
* **ci:** remove deleted test_workflow.py from smoke job + enforce security scan failure ([a2e1f02](https://github.com/ReSerendipity/Image-DuoModel/commit/a2e1f02d65135c1aa8187b206eca570634800e07))
* **ci:** 从必需检查摘掉 PR 上永不产出的 3.13 context 并落地远端（OPEN-3 / better-harness F5） ([8b9a51e](https://github.com/ReSerendipity/Image-DuoModel/commit/8b9a51e7ad319abae8b4b6469fdb35bc8d790bc5))
* **ci:** 修复 CI/Security 状态检查失败 ([a34bf5c](https://github.com/ReSerendipity/Image-DuoModel/commit/a34bf5ce88962de9079f0008b831806915ac2caa))
* **ci:** 修复 Test+Coverage 状态检查的两类偶发失败 ([cbbbb98](https://github.com/ReSerendipity/Image-DuoModel/commit/cbbbb982184fd6e588c25df351b46f020d86081e))
* **ci:** 修掉 CI 两处红 —— 跨文件假引擎变量污染 + mypy Literal 赋值 ([e52148c](https://github.com/ReSerendipity/Image-DuoModel/commit/e52148cf914cce57a9ec92be641cc9a31c949998))
* **ci:** 修掉跨平台行尾与 gitignore 目录缺失导致的 CI 恒定报红 ([ea52691](https://github.com/ReSerendipity/Image-DuoModel/commit/ea526919390b796a5d27a71b3a0e1f593e053df1))
* **ci:** 完整性清单门禁补上 Ed25519 验签（与运行时 enforce 同口径） ([#89](https://github.com/ReSerendipity/Image-DuoModel/issues/89)) ([ba2ad4e](https://github.com/ReSerendipity/Image-DuoModel/commit/ba2ad4ec2650d2bc062f37d9d9281545dfe27517))
* **ci:** 给清单验签补上 cryptography 依赖，并分开"缺依赖"与"未签名"两种报法 ([#91](https://github.com/ReSerendipity/Image-DuoModel/issues/91)) ([77091f4](https://github.com/ReSerendipity/Image-DuoModel/commit/77091f468349acc1d3a5aceb8476e27edb32899a))
* **ci:** 远端模式缺 STAGING_BASE_URL 时硬失败，不再静默回退到 runner 本机回环 ([#78](https://github.com/ReSerendipity/Image-DuoModel/issues/78)) ([11f8302](https://github.com/ReSerendipity/Image-DuoModel/commit/11f8302f7f60bba2a8dedd9ca4db621912766d79))
* **compose:** 回环绑定 + bluegreen 卷名对齐 + 配置只读 + 优雅关闭 ([46bc604](https://github.com/ReSerendipity/Image-DuoModel/commit/46bc60463481fe96a9777b62241ee63463397a10))
* **config:** qwen 引擎 unet 改指 Qwen-Image-2.1-turbo 真实文件（追加任务B决策） ([b3a790b](https://github.com/ReSerendipity/Image-DuoModel/commit/b3a790b92c3a30a805e9aaa336f3a9eb6a775c03))
* **config:** z_image unet 改指 FP8 档并同步精度声明（追加决策 2026-10-12） ([4c040a6](https://github.com/ReSerendipity/Image-DuoModel/commit/4c040a67ba05b92630b14cfe0bd5d9af0f94f706))
* **config:** 收紧未登记权重开关并重生成在用清单（P0-2, MLOps M3） ([1094617](https://github.com/ReSerendipity/Image-DuoModel/commit/1094617cc3a481c79d92902ce1c1ac83346b0959))
* **deps:** repair pydantic-core lock pair and stop Dependabot breaking it ([#84](https://github.com/ReSerendipity/Image-DuoModel/issues/84)) ([d3b3085](https://github.com/ReSerendipity/Image-DuoModel/commit/d3b3085b4d3ae38bb61c9b4a4d53e8b4004863ea))
* **deps:** 回退 [#86](https://github.com/ReSerendipity/Image-DuoModel/issues/86) 对锁的 31 处改动（main 现在不可安装）+ 新增锁可解性门禁 ([#90](https://github.com/ReSerendipity/Image-DuoModel/issues/90)) ([bf70389](https://github.com/ReSerendipity/Image-DuoModel/commit/bf70389b3b78769d3b7df1a40cc3973659b1ccb4))
* **deps:** 重锁 sympy/mpmath 这一对，恢复 main 的锁可解性 ([#94](https://github.com/ReSerendipity/Image-DuoModel/issues/94)) ([b0066d0](https://github.com/ReSerendipity/Image-DuoModel/commit/b0066d08c66b59afba87059d00c635a1eeafa0ae))
* **deps:** 锁针最小闭包修复，闭合 Lock Solvability 联解红灯（OPEN-2） ([ca1e8da](https://github.com/ReSerendipity/Image-DuoModel/commit/ca1e8dafbdf00493285e6d35e19fedcd21a5206c))
* **desktop:** 壳 runtime 解析与安装器 version.json 两处分发回归（v1.3.0 阶段3 真机安装模拟实测） ([7757be9](https://github.com/ReSerendipity/Image-DuoModel/commit/7757be9e43d55b0bfedb82b7909be52562c54a25))
* **desktop:** 空提示词最终闸 + 优雅停机端点补全（v1.3.0 发版期两处 P2） ([8535842](https://github.com/ReSerendipity/Image-DuoModel/commit/8535842ddd9b4d76188bbffbcccdf9ab6c981e83))
* **devx:** precheck.ps1 python 解析回退 + 依赖缺失告警跳过（兼容无 venv 环境，完整门禁由 CI 承担） ([bdecc90](https://github.com/ReSerendipity/Image-DuoModel/commit/bdecc9019541690d6ed6a1fb4c60bf5aabb5e2f7))
* **docker:** P0 启动入口修复 + 非 root 加固 + 镜像瘦身 ([ae7c539](https://github.com/ReSerendipity/Image-DuoModel/commit/ae7c53989eb1960c824157b2d38b8626494d9511))
* downgrade image-too-small watermark warning to debug ([12ba273](https://github.com/ReSerendipity/Image-DuoModel/commit/12ba2735e9ae0f3440b7dcf98e42a808409aac99))
* downgrade unsigned-key watermark warning to debug ([548af28](https://github.com/ReSerendipity/Image-DuoModel/commit/548af28e3248e2f51734fb844dd81049b33eafae))
* **env:** 系统环境补齐 comfy-aimdo 依赖声明 + 冒烟脚本字段兼容 ([e4768e5](https://github.com/ReSerendipity/Image-DuoModel/commit/e4768e5d886cbe76ab1d732afb9f379b8139c791))
* **gates:** 引用门禁声明文档集缺失即判失败并打印实读口径（better-harness F2） ([c57009b](https://github.com/ReSerendipity/Image-DuoModel/commit/c57009b74b5392b42aaa31c477193c9639ed9c79))
* **generate:** 假引擎路径跳过 VRAM 动态 batch 钳制，消除生成 flaky ([f9167fb](https://github.com/ReSerendipity/Image-DuoModel/commit/f9167fba189940664442a410055de608c083f45b))
* **governance:** CODEOWNERS 路径全部对齐真实文件树 ([#87](https://github.com/ReSerendipity/Image-DuoModel/issues/87)) ([2e811be](https://github.com/ReSerendipity/Image-DuoModel/commit/2e811bef94df876bd425c8ac13ee907cafa1e8ce))
* **governance:** 启动僵尸清扫加 300s 宽限期 + 完整性清单重生成 ([21e105e](https://github.com/ReSerendipity/Image-DuoModel/commit/21e105ee8a93c79cfb25a5b46414713bbd7009b4))
* **harness:** 恢复可分发 agent 指令基线与 .gitignore 放行（better-harness F1） ([b9ff9eb](https://github.com/ReSerendipity/Image-DuoModel/commit/b9ff9eb00329a14a5434f50a6280063be7574935))
* hide watermark from user-visible surfaces (README, demo, SECURITY, runtime logs to debug) ([7b9374d](https://github.com/ReSerendipity/Image-DuoModel/commit/7b9374db703f5e15b4ced5f93650c075afe28a24))
* **history:** FTS 中文搜索 rowid 漂移修复 + 搜索回归测试 ([9ebe3b2](https://github.com/ReSerendipity/Image-DuoModel/commit/9ebe3b2f377b65c232d63468cfdbd1c15a8a0932))
* **history:** mypy ratchet 定向零错——FTS 兜底路径 Optional[str] 收窄 + 清单会签 ([f28d54c](https://github.com/ReSerendipity/Image-DuoModel/commit/f28d54c4c87844d7a141258a306c508ce62fa71a))
* **history:** 修复 ADD COLUMN IF NOT EXISTS 迁移语法错误，恢复生成链路 ([63c24be](https://github.com/ReSerendipity/Image-DuoModel/commit/63c24be5443181682a2e1dcb58eeac5e5732a481))
* **history:** 容量快照表 + pending 僵尸清理 + max_gb 口径修复 + 失败入账 ([4db7d9f](https://github.com/ReSerendipity/Image-DuoModel/commit/4db7d9f6a171cc0b0812a55518776cf6253baa0a))
* **hooks,governance:** 补 lite 档 lint 空洞 + 修正改名后失效的 Pages 链接（F3 延伸 / 改名传播） ([59775d5](https://github.com/ReSerendipity/Image-DuoModel/commit/59775d50f5fd54df59cc090364473cc78835628c))
* **hooks:** pre-commit 分发器支持控制台命令回退（无 venv 时框架仍生效） ([2ef20e5](https://github.com/ReSerendipity/Image-DuoModel/commit/2ef20e59aee90c07b042768ddd82d8852a8d188a))
* **hooks:** 引用完整性校验接入提交路径，守卫缺席改为默认阻断（better-harness F3） ([01b76e8](https://github.com/ReSerendipity/Image-DuoModel/commit/01b76e89d7dbb949f283f219cd9a4b92ef4982f1))
* **hooks:** 结构门禁登记 .qoder 为许可根项（better-harness F1 补全） ([78fe13e](https://github.com/ReSerendipity/Image-DuoModel/commit/78fe13ec44b40420a38783b5ae042d83327c8572))
* **launch:** *.bat 强制 CRLF——LF 行尾批处理在 cmd 下解析碎片化 ([8afcc45](https://github.com/ReSerendipity/Image-DuoModel/commit/8afcc4568f225b91b416ce45a396f5ddd731278b))
* **launch:** start.bat 引用旧布局 bin\clean_launch.py 导致正式启动失败 ([a060496](https://github.com/ReSerendipity/Image-DuoModel/commit/a060496aad2cba61a875229992e7944d1d2a80ae))
* **lineage:** 修正错误的两级相对导入（应为同级一级） ([3100241](https://github.com/ReSerendipity/Image-DuoModel/commit/3100241d99917b91c9dc3ecdfc41042acad73010))
* mypy 余下 6 处类型标注（i18n 重定义/source 返回窄化/output_pipeline 变量注解/Starlette handler ignore） ([d6ce35d](https://github.com/ReSerendipity/Image-DuoModel/commit/d6ce35d64b44a6c667ca9f47d38f62fdf80fb957))
* **native:** 修复原生引擎无法出图 + 切 portable 模型来源用 FP8 ([751c0c5](https://github.com/ReSerendipity/Image-DuoModel/commit/751c0c5faa0e711f73080a99c8900a0633618d3d))
* PathGuard 统一拒绝空字节注入路径（修复 Linux CI 上 ValueError 未捕获导致 smoke 失败） ([824b00c](https://github.com/ReSerendipity/Image-DuoModel/commit/824b00cb3b034aba3e765ccbd7ed9f81696dcb1a))
* PathGuard 跨平台统一路径语义（反斜杠归一化 + 盘符路径挂根），修复 Linux CI 上绝对路径/混合斜杠攻击用例失败 ([afe4924](https://github.com/ReSerendipity/Image-DuoModel/commit/afe492421c0438b4779a66cab7cc3097b189e946))
* pickImage long-keyword weighting to avoid single-char mismatches ([f374ecb](https://github.com/ReSerendipity/Image-DuoModel/commit/f374ecb80e319437ad4489d912b56052c0c0737e))
* **portability:** 新增路径可移植性自动化检查并登记规范 ([#74](https://github.com/ReSerendipity/Image-DuoModel/issues/74)) ([f2775ea](https://github.com/ReSerendipity/Image-DuoModel/commit/f2775ea8a5c19f8800c83a756caf07444e256b0e))
* **precheck:** 本地覆盖率门禁 60% 对齐 CI 的 65%，消除本地绿远程红漂移 ([015ecc3](https://github.com/ReSerendipity/Image-DuoModel/commit/015ecc337b796dc64b40a4bd3de8887257d7eb71))
* preflight_spec was accidentally written at column 0 inside the class body, closing TrainingRunner early and dropping every class method (9 test failures). Moved it after the class; recorded as GOTCHAS [#50](https://github.com/ReSerendipity/Image-DuoModel/issues/50). Verified green: ruff, mypy 106 files, full pytest 1434 passed/16 skipped/1 xfailed, integrity 33/33, no-hardcoded-paths, config/spec-refs. ([b5c440d](https://github.com/ReSerendipity/Image-DuoModel/commit/b5c440d67fc11d89eaf311b408deedd9e0565f70))
* prompt-image fixed pairing (6 cat-themed pairs, keyword matching, preset prompt backfill) ([3aa3ffc](https://github.com/ReSerendipity/Image-DuoModel/commit/3aa3ffc151f383e84cc08b3b7f8adfbcac0bddd2))
* remove local-only Chinese docs from remote; add gitignore rules ([ac8180a](https://github.com/ReSerendipity/Image-DuoModel/commit/ac8180ad2b034d2974a93825b0601b8f574a69f4))
* restore CI workflows to remote; anchor workflows ignore to root ([637cc0d](https://github.com/ReSerendipity/Image-DuoModel/commit/637cc0dd86f5769e5b9835730dbbda139fecae5d))
* **routes:** 修复导出路由被 /{task_id} 动态路由吞掉导致恒 404 的真实缺陷 ([137e60a](https://github.com/ReSerendipity/Image-DuoModel/commit/137e60a97c793665cb61b6c477bdf55e5a787512))
* **scheduler:** cron misfire 启动补跑 + 维护 cron 环境开关 + lifespan 复用配置单例（P2-3） ([b2c477d](https://github.com/ReSerendipity/Image-DuoModel/commit/b2c477dd62c55a09e9f536033b3e2d414d4c286c))
* **scripts,tests:** 同步容量基线与发布元数据脚本及测试 ([b2774ed](https://github.com/ReSerendipity/Image-DuoModel/commit/b2774edf2a5d44815dbee7e89a766a95ec6d0d0f))
* **scripts:** mypy scripts 收口——修复 2 个预存类型错误 ([155d658](https://github.com/ReSerendipity/Image-DuoModel/commit/155d6583703f89a62e4c260e36f57266dd9c1e7a))
* **security:** content_filter CLIP 特征归一化修复 + 阈值校准 0.5 ([94b3c25](https://github.com/ReSerendipity/Image-DuoModel/commit/94b3c2598594175e951b4d974b77147008ac8c18))
* **security:** 双 fail-open 改 fail-closed + 激活权重 SHA256 完整性清单（H2/M1/M4） ([22388a4](https://github.com/ReSerendipity/Image-DuoModel/commit/22388a4af5e4e3df3ebeef9027b0061b93f66476))
* **security:** 完整性清单与 HEAD 代码重对齐 ([d0f59e0](https://github.com/ReSerendipity/Image-DuoModel/commit/d0f59e0e3658f4009faf8449cd133ef26cae9450))
* **security:** 路径解析失败 fail-closed + 前端 XSS 转义缺口修复（L6/L1） ([54b30ce](https://github.com/ReSerendipity/Image-DuoModel/commit/54b30ce609c045d71bdb9dfc1569343188ec8322))
* **security:** 重建清单签名以匹配当前代码基线，修复启动自检哈希不一致 ([324b6ef](https://github.com/ReSerendipity/Image-DuoModel/commit/324b6ef2304b526adf9f4be1dc72ac0be238f515))
* **security:** 重生成完整性清单——同步 config_models.py 哈希（enforce 自检 33/33 恢复） ([d9f600a](https://github.com/ReSerendipity/Image-DuoModel/commit/d9f600a9854a8b20d9e7af713a1d99a26326d78f))
* **shutdown:** 排空在飞行 worker 线程，修复关闭期 SQLite use-after-close 段错误 ([1fd8d8d](https://github.com/ReSerendipity/Image-DuoModel/commit/1fd8d8d374d22df3b64438f1c821a9cceaace794))
* **smoke:** 晋级门禁校验产物真实落盘 + 历史库落盘尺寸回填 ([d742967](https://github.com/ReSerendipity/Image-DuoModel/commit/d742967649153a5a56a1be73f2cca547b09c0c30))
* **tests:** 修复 xdist 下 database is locked —— 隔离 fixture 装饰器被注释吞掉 ([e5c06cc](https://github.com/ReSerendipity/Image-DuoModel/commit/e5c06cc4a0a59dd5da9273954112f129daecff85))
* **test:** xdist 跨 worker database is locked——HistoryDB 隔离覆盖双导入身份 ([44fb92e](https://github.com/ReSerendipity/Image-DuoModel/commit/44fb92e5e8f8301a26c53a4de64b579e2a968be0))
* **test:** 修复 unload_engine 根因并消除路由测试全局状态泄漏 (P2-8/P2-9) ([4071cf0](https://github.com/ReSerendipity/Image-DuoModel/commit/4071cf0f2c3d7289e5961a7518d9d55f35bc8fb4))
* **test:** 修复跨测试文件的环境变量污染 + 引擎加载回归测试自洽化 ([2eb17af](https://github.com/ReSerendipity/Image-DuoModel/commit/2eb17afe35a1fcce4e605f6657a245ca850bf6c9))
* **typing:** 修复 mypy 三处类型错误（tracing __exit__ / LoRA 兼容校验） ([74d4bf6](https://github.com/ReSerendipity/Image-DuoModel/commit/74d4bf6780ca871e37d63152a483c8131a543cf5))
* **ui:** P0 幽灵确认弹层 — CSP style-src 'self' 剥离服务端内联 style 属性 ([98c9a9b](https://github.com/ReSerendipity/Image-DuoModel/commit/98c9a9b8f0707d1b09e8479e33f05a46704ca5e4))
* update SeedVR2 reference paths to renamed SeedVR2-lite ([a3245d5](https://github.com/ReSerendipity/Image-DuoModel/commit/a3245d5fce4fa323bffc9b3153c0218b71db10bb))
* **vlm:** M1 真实前向已实跑闭环 — 修 preflight 引用静态方法缺陷并抽 build_image_batch ([746576b](https://github.com/ReSerendipity/Image-DuoModel/commit/746576bbcb484802d8bc783b3267ade6d5fcd125))
* **webui:** WCAG contrast fixes for H3 accent + batch tabs styles + CSRF-aware test clients ([ea48d70](https://github.com/ReSerendipity/Image-DuoModel/commit/ea48d703a663bcb01acc4d0be8b0d354f402cbac))
* 消除硬编码本机绝对路径，新增路径可移植性规范 ([#73](https://github.com/ReSerendipity/Image-DuoModel/issues/73)) ([2feb7cc](https://github.com/ReSerendipity/Image-DuoModel/commit/2feb7ccf2c4ebea7186bda1da00b1f6e09a347c0))
* 清理 74 处 lint + 修复 F821 未定义 seed + mypy 显式包基础与 7 处类型标注（lint 软门禁转硬） ([ec576de](https://github.com/ReSerendipity/Image-DuoModel/commit/ec576debb3baea82b634c5a7595c903564dd8d25))


### Performance Improvements

* **preprocess:** 卸载阻塞 IO 至线程池并修复绝对导入 (P1-3) ([c19f5e1](https://github.com/ReSerendipity/Image-DuoModel/commit/c19f5e12a341da099a5799888378380bfeebfffb))
* **test:** 升级性能基准——假引擎 + 生成延迟/并发吞吐/VRAM/趋势 (P1-6) ([b28e39c](https://github.com/ReSerendipity/Image-DuoModel/commit/b28e39ca4c61531ef3270bd041ca0a9113fce0b1))

## Changelog

All notable changes to Image MultiModel will be documented in this file.

> **版本史说明（2026-09-15）**：2026-08-10 曾以 v2.0.0 发布，随后版本号重启为 1.x（1.1.0 → 1.2.2 现行基线，权威位 config.yaml）；远端 v1.5.0 / v1.5.1 tag 为 release-please 时代产物，经 2026-09-05 裁决不再作为版本基线、亦未收录于本 CHANGELOG。详见 docs/release-governance.md。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

***

## \[Unreleased]

### Fixed

- **发版期修复（v1.3.0 发版全流程实测发现，2026-10-03）**：① P0 幽灵确认弹层——CSP `style-src 'self'` 剥离服务端内联 style 属性，`#appConfirm` 的 `style="display:none"` 失效叠加 CSS 类 `display:flex`，空确认框常驻 z-index 10000 挡死全新 profile 用户（`399de48`：模板内联样式全部类化 + `#appConfirm` CSS 默认隐藏 + `/static` 下发 `Cache-Control: no-cache` 修复升级后陈旧缓存 + 防回归测试 ×2）；② 壳 1.0.1——`resolve_runtime_dir` 与分层布局不符致装后 Python 无法启动 + 安装器内嵌 version.json 过期盖掉新版本（`48d7b36`）；③ 数据卷打包契约修正——comfy_kernel 随整包首发（`package_app.py` 有意排除内核，换载不替换）。

## \[1.3.0] - 2026-10-03

### Added

- **增量包 Ed25519 签名链（2026-09-11 收口）**：`scripts/package_app.py` 打包即对 `app-v{ver}.zip` 签 Ed25519（`.sig.ed25519`，复用完整性清单密钥对，零新依赖；`--no-sign` 调试逃生门）；`scripts/release_gate.py` gate-5 对每个增量包回验签。
- **CI 桌面增量包自动构建（2026-09-11 收口）**：`release.yml` 新增 `desktop-package` job（windows-latest）——清单门禁 → 私钥注入（Secret）→ 打包签名 → 验签 → 便携诊断 → 壳 `cargo check --locked` → 上传增量包三件套到 GitHub Release；壳完整 build 仍由本机发布流程执行。
- **桌面化分发（P1-3）**：Tauri v2 壳（`desktop/src-tauri`：单实例/托盘/崩溃自启/窗口状态记忆/隐藏控制台/增量更新器）；NSIS 安装器（`desktop/installer/setup.nsi`：分卷解压/运行中进程自动终止/卸载清理）；分层定案（`docs/桌面分发分层定案-20260910.md`）；增量应用包打包（`scripts/package_app.py`）；Release 分卷切片（`scripts/split_release_volumes.py`，900MB/卷 + SHA256SUMS 全覆）；版本单一来源闸门（`scripts/check_config_refs.py` 扩展，config.yaml 权威位一致性校验）。
- **发布质量（P2）**：安装环境诊断（`scripts/diag_portable_verify.py`：cryptography→清单→验签→自检→enforce 五环节）；发布门禁五步（`scripts/release_gate.py`：构建→静态→测试→签名→发布物）；闭源编译评估（`docs/闭源编译评估-Cython-pyd-20260910.md`，含公开声明）。
- **服务端支撑**：`app_server.run()` 支持 `--host/--port`（桌面壳传入空闲端口）。
- **Flux.2 Klein 9B（fp8）原生引擎（2026-09-30 接入）**：`config.yaml → models.engines.flux2_klein_native`，`backend: native`；权重三件套（UNet 8.46GB + Qwen3-8B TE 8.07GB + Flux.2 VAE）以 junction 挂载到 `pretrained_models/`；实机 RTX 5070 Ti 12GB preflight 512²/4 步出图验证通过（含 offload 28~112s）。采样器与调度器不再硬编码 Z-Image 常量：`GenerationConfig` / `EngineConfig` 新增 `sampler`/`scheduler` 字段，`native/executor.py` 按引擎配置下发，空值回退至原 Z-Image 默认；`latent_channels: 128` 与 `latent_downscale: 16` 必须显式写入配置（实测 `model.latent_format` 为 None，缺省会误回退至 Z-Image 的 16/8）。接入前自检工具 `scripts/preflight_flux2_klein.py` 可作为后续新引擎的标准模板。
- **能力演进 roadmap 入库（2026-09-30）**：`docs/roadmap/README.md` 将 P0/P1 已落地能力与 P2 后续可选项（多引擎、VLM 看图聊天）切片可追踪；`P2-multi-engine.md` 与 `P2-vlm-chat.md` 分别目标引擎与 VLM 权重选定、实施步骤与验收标准写入仓库。

### Security

- **桌面端完整性**：壳健康检查解析 `/api/system/health` 的 `security.integrity`（含 manifest_signed），完整性失败在托盘展示篡改告警。
- **更新签名**：独立生成 Tauri 更新签名密钥对（私钥 `desktop/src-tauri/tauri.key` gitignore + 离线备份，公钥入库并写入 `tauri.conf.json` pubkey）。
### Fixed

- **修复会话级 HistoryDB 隔离 fixture 因装饰器被注释吞掉而从未生效**：`tests/conftest.py` 里 `# ── 反模式 #4 防护 … ──@pytest.fixture(autouse=True, scope="session")` 把装饰器写进了注释行，`_isolate_history_db_for_tests` 退化为普通函数、pytest 不收集 → 各 xdist worker 直连真实 `data/history.db`，并发 `PRAGMA journal_mode=WAL` 报 `sqlite3.OperationalError: database is locked`（CI 34562117669 复发）。现装饰器独占一行；并对 `load_config`/`load_validated_config` 加包装，使配置单例被整体替换后重定向依然生效；新增 `tests/test_history_db_isolation.py` 锁定契约（FIX_LOG #2）

- **修复 xdist 跨 worker 的 `database is locked` 竞态**：conftest 会话级 HistoryDB 隔离此前只重定向顶层 `integrated_app.config` 单例，而 `create_app()` 经 `app.integrated_app.*` 相对导入使用**另一份配置单例**（两身份为独立模块对象），重定向失效导致多 worker 并发初始化真实 `data/history.db` 时加锁失败；现同时重定向两份单例（CI 33957856101 复现，FIX_LOG #1）

- **修复** **`config.yaml`** **中失效的** **`bin/`** **路径残留**：`security.integrity_selfcheck.manifest_file` 与 `i18n.locale_dir` 由不存在的 `bin/integrated_app/...` 改为 `app/integrated_app/...`（bin→app 重命名后未同步，会导致完整性自检清单与语言词表无法定位）

- **补齐配置引用门禁脚本** `scripts/check_config_refs.py`：AST 解析 `config_models.py` 提取配置模型字段，扫描 `app/` 代码引用，对账 `config.yaml` security 段「声明即消费」，修复 `tests/test_config_refs_gate.py` 三例因缺脚本而恒失败的问题

- **修复版本漂移测试**：`tests/test_config.py::test_app_config_builds` 断言由过期的 `2.0.0` 改为 `1.2.2`（对齐 `config.yaml`）

- **根治 config.yaml 测试污染（2026-09-11 收口）**：conftest 新增会话级字节快照保护——此前配置保存 API（`config_routes.save_config(cfg)` 无路径参数）会把测试期内存重定向的临时路径（`imm-hist-<pid>`）写回真实 `config.yaml`；现任何测试对真实配置文件的写入均在会话结束被回滚（全量 pytest 后 config.yaml SHA256 不变）

- **修复 mypy scripts 2 个预存类型错误（2026-09-11 收口）**：`fix_encoding_diag.py` 的 `line` 未初始化 None 索引；`post_deploy_smoke.py` 的 `get_json` 返回类型未收窄（`mypy scripts` → Success 35 文件）

- **UI/UX 审计 P1 修复（2026-10-01）**：
  - 历史中文搜索不可用——`history_db.py` FTS5 `unicode61` 不索引 CJK，含中文/长度 <3 的查询自动降级为 LIKE，并用 rowid 读取避免结果集与 tasks 行映射漂移；FTS5 MATCH 语法错误（引号/括号等）自动回退 LIKE，任何输入不再导致搜索页 500；新增 `tests/test_history_db_search.py` 锁定中文/英文/混合关键词与分页行为
  - 分享按钮无反应——`app.js` 重写 `shareCurrent()`，先拉取当前任务产物与提示词，拼装为剪贴板文本后 `navigator.clipboard.writeText`，失败回退到 `prompt` 方案
  - 无引擎就绪预检——`genBtn` 提交前自动 `POST /api/engine/preflight`，引擎未就绪时弹 appConfirm 提示先加载，避免默默入队后卡住

- **UI/UX 审计 P2/P3 修复（2026-10-01）**：顶部栏悬停、设置下拉、关于面板社交链接 SVG 图标与版权文案、历史筛选新增「已取消」、状态 `st_*` 五语言全补齐 + `tr()` 未知键回退剥前缀、抽屉标题与提示全 i18n、EULA 隐私描述改为「提示词与生成结果均不出设备」、新增应用内 `appConfirm()` 模态全面替换原生 `window.confirm/alert`、手风琴序号 02→01、「模块」→「功能」、a11y aria-label/title 补齐（种子/默认随机骰、批量按钮、复选/单选、图库 chip、表格表头）、VRAM 状态口径统一为「可用 x.x / xx.x GB」、LoRA 滑杆选择器修正为栈内 `input[type=range]` 统一绑定、`histPurge` 无可清理项自动禁用、FAB 与 AI 对话发送按钮按品牌色统一

- **UI/UX 审计 P4 修复（2026-10-01）**：
  - 深水区 i18n 补齐——五语言字典新增约 130 键，覆盖设置面板（引擎与模型/运行/保留策略/配置 全部 label + option）、关于面板正文（副标题/描述/作者版本协议/6 项 feature/版权行）、批量面板（dropzone/每行 batch/16 倍数/网格笛卡尔积 hint/批次估算/任务队列 + 动态估算行内嵌 `<b>` 数字）、高级参数抽屉全部 label（基础/LoRA/SeedVR2/对比+显存预留/输出）、历史详情（任务详情/尺寸·seed/耗时·时间/重绘/预设/ZIP）、历史筛选下拉与 Purge/Clear、状态抽屉、预设面板、查看器标题、队列 popover 与状态行；动态文案全部走 `tr()`（包括分享/预设保存/删除确认的 appConfirm 消息与按钮）
  - 右下角控件堆叠修复——`#agent-fab` 从 `bottom:22px` 上移至 `86px`，避开队列胶囊 `bottom:44~78px` 区间；`#agent-drawer` 同步上移至 `150px`；`.viewer` z-index 从 120 提至 9993（压过 FAB 9990，`app-confirm` 10000 仍最高），实测查看器打开时 FAB 被完整覆盖

### Changed

- **完整性清单会签流程规范化（2026-10-01）**：`generate_integrity_manifest.py` 仅重生成 SHA256，未签名清单在 enforce 模式下仍会拒启；标准两步变为「generate → sign」，已写入 `docs/roadmap/P2-multi-engine.md` 与 `docs/GOTCHAS.md`。
- **默认引擎** **`z_image_turbo_native`** **的** **`workflow_file`** **置空**：引擎推理由代码/native 构建，不再引用不存在的 `workflows/Z_image_turbo.json`；`workflows/` 收敛为用户自放 ComfyUI 工作流的参考目录（`.gitignore` 排除，启动时自动重建空目录）

- **新增根级** **`AGENTS.md`**（家族自进化协议 v1.3）：补齐此前缺失的项目级 Agent 规范，并明确 `comfy_kernel/AGENTS.md` 为 vendored 上游 ComfyUI 文件、非本项目 AGENTS

### Removed

- **停用 release-please 自动发版**：删除 `.github/workflows/release-please.yml`、`release-please-config.json`、`.release-please-manifest.json`（用户裁决，与 `docs/release-governance.md`「config.yaml 顶层 version 为唯一权威版本位 + 手动打 tag 发布」的明文政策对齐）。v1.5.0 / v1.5.1 为该机制时代的历史产物，原地保留不再延续；后续发布走 `release.yml`（tag 驱动 / workflow_dispatch），版本位三处（config.yaml + AGENTS.md + CHANGELOG）人工同步

***

## \[1.2.2] - 2026-08-14

### Fixed

- **修复原生引擎 worker 不消费任务**（`task_queue.py`）：`asyncio.wait_for(queue.get(), timeout=1.0)` 在该运行环境下超时不触发导致 worker 永久挂起、任务永远 pending。改为 `get_nowait()` + `asyncio.sleep(0.2)` 轮询取任务，彻底避开 `wait_for` 超时机制

- **修复原生引擎 latent 参数错误**（`native/executor.py`）：Z-Image 使用 FLUX AE，latent 应为 **16 通道 / 8 倍下采样**（原代码误用 SD3 的 4 通道 / 8 倍下采样，导致输出分辨率减半为 384×384）。修正后恢复 768×768

- **修复 VAE 解码传参**（`native/executor.py`）：`vae.decode()` 应直接传 latent 张量，而非 `{"samples": ...}`（Comfy 的 `VAEDecode` 节点语义）

- **修复服务跑在 CPU 版 torch 上**：服务此前运行在 `torch 2.13.0+cpu`（无 CUDA），推理报 `Torch not compiled with CUDA enabled`。`bin/clean_launch.py` 的 `find_winpython()` 新增系统级 CUDA Python 候选（`C:\Python312`，torch 2.13.0+cu132），并修正重启逻辑（检测到非当前 CUDA Python 即切换）

### Changed

- **模型来源切换为 portable（便携独立运行）**：`config.yaml → models.model_source_mode` 由 `shared`（指向本机外部 ComfyUI-aki-v3 模型目录）改为 `portable`，模型放入项目内 `pretrained_models/`，无任何外部链接 / junction，可作便携包独立运行

- **unet 改用 FP8 模型**：`config.yaml` 引擎 `z_image_turbo_native` 的 unet 指向 `Z-image_turbo-bf16/zimageTurboNSFWByStable_2602NSFWFP8.safetensors`（FP8，约 5.9GB），`default_precision` 同步设为 `fp8`，出图更快

- **补装原生引擎依赖**：`einops`、`torchsde`、`comfy-aimdo==0.4.13`、`comfy-kitchen==0.2.30`（源自 `references/ComfyUI/requirements.txt` 与本机 ComfyUI-aki-v3）

***

## \[1.2.1] - 2026-08-14

### Fixed

- **修复** **`index.html`** **mojibake 乱码**：文件中文曾因多次 GBK/UTF-8 往返编码被破坏（页面出现 `?` 乱码），且自动修复脚本用 `errors="replace"` 进一步丢失 1118 个字符。已从干净的 git 提交 `014edd3` 重建全量中文，恢复为纯 UTF-8（0 乱码字符）

### Changed

- **前端 UI 优化**：顶部栏图标按钮添加文字标签（主题、颜色、字体、关于、设置、模型、语言），移除冗余的「全部 / Native」引擎过滤选项，引擎选择简化为直接显示引擎列表

- **彻底脱离 ComfyUI 前端残留**：移除「释放显存」按钮（`freeVramBtn`，对应已删除的 `/engine/free` 端点）、「ComfyUI 后端」状态面板（local/gpu-cluster · 8188）、状态栏 `CONN: LOCAL:8188`、关于面板「统一驱动 ComfyUI」副标题与「驱动本地 ComfyUI」特性条目

- **引擎引用统一为** **`z_image_turbo_native`**：硬编码引擎菜单 / `engineSelect` / 预设默认引擎 / 快照与状态栏文本统一为 `Z-Image Turbo（原生）`

***

## \[1.2.0] - 2026-08-13

### Added

- **原生进程内引擎（双后端模式）**（MASTER\_PLAN M7）：

  - `bin/integrated_app/native/` 包：`source.py`（复用 `references/ComfyUI` + aki-v3 自定义节点源码，`sys.path` 注入）、`executor.py`（复用 `comfy.sd` / `comfy.samplers` 完成 加载→CLIP编码→采样→VAE解码）、`engine.py`（`NativeEngine` 实现 `ImageEngine` Protocol，输出经 `PathGuard` 校验落盘 + DCT 水印 + 缩略图）

  - `lora.py` / `seedvr.py` / `compares.py` / `vram.py` / `preview.py`：原生引擎 Phase 3 能力扩展

  - `config.yaml` 新增 `z_image_turbo_native`（`backend: native`），无需外部 ComfyUI 进程即可在进程内出图

- **后端模式切换**：`routes/engine_routes.py` 按引擎配置的 `backend` 字段分发 `ComfyEngine` / `NativeEngine`；前端引擎菜单顶部支持「全部 / ComfyUI / 原生」过滤

- **动态 LoRA 栈**：`engine_interface.py` 的 `GenerationConfig` 新增 `lora_stack` 动态字段（不局限于旧 6 层，空时回退旧字段）

- **原生引擎安全测试**：`tests/test_native_security.py`（`_save_outputs` 路径穿越攻击向量：`../`、绝对路径、恶意引擎名，全部被 `PathGuard` 拒绝）

### Security

- 原生引擎输出落盘路径经 `PathGuard` 校验，验证 `../` 穿越 / 绝对路径 / 恶意引擎名注入向量全部拒绝

***

## \[1.1.0] - 2026-08-13

### Added

- **CLIP 安全内容检测**（全功能实施指南 P0 任务1）：

  - `security/content_filter.py`：基于 CLIP 的图片安全检测 + 关键词提示词过滤

  - CLIP 模型懒加载，未安装时优雅降级为纯关键词过滤

  - `routes/safety_routes.py`：`POST /api/safety/check-prompt` + `POST /api/safety/check-image`

  - 集成到 `/api/generate` 生成流程，违规提示词自动拦截

  - 27 个不安全关键词覆盖（NSFW / 暴力 / 仇恨 / 自残 / 毒品 / 武器等）

- **Fooocus 风格提示词扩展**（全功能实施指南 P0 任务2）：

  - `prompt_expander.py`：智能提示词扩写系统

  - 6 种预设风格（cinematic / anime / photorealistic / oil\_painting / digital\_art / fantasy）

  - 自动质量增强（masterpiece / best quality / ultra detailed / 8k）+ keyword:weight 加权语法

  - 5 种场景智能推荐（portrait / landscape / still\_life / architecture / fantasy）

  - `routes/prompt_routes.py`：`POST /api/prompt/expand` + `POST /api/prompt/suggest` + `GET /api/prompt/styles` + `GET /api/prompt/scenes`

- **ControlNet 预处理器系统**（全功能实施指南 P0 任务3）：

  - `preprocessors/canny.py`：Canny 边缘检测（自适应百分位阈值）

  - `preprocessors/midas.py`：MiDaS 深度估计（DPT\_Large 模型懒加载）

  - `preprocessors/openpose.py`：OpenPose 人体姿态检测（controlnet\_aux 懒加载）

  - `PreprocessorProtocol` 协议 + 注册表模式，支持扩展自定义预处理器

  - `routes/preprocess_routes.py`：`POST /api/preprocess/canny` + `POST /api/preprocess/depth` + `POST /api/preprocess/pose` + `GET /api/preprocess/list`

  - Base64 图片输入输出，无需文件 I/O

- **i18n 新增 9 个后端错误 key**（5 种语言同步）：`content_blocked` / `prompt_expand_success` / `prompt_suggest_success` / `preprocess_canny_success` / `preprocess_depth_success` / `preprocess_pose_success` / `preprocess_failed` / `preprocess_not_available`

- **新增依赖**：`clip-anytorch>=2.0.0`（CLIP 安全检测）、`controlnet-aux>=0.0.9`（OpenPose 预处理）

### Security

- 生成流程集成 CLIP 内容安全过滤，违规提示词自动拦截（400 响应）

- 安全检测路由的图片路径过 PathGuard 校验

***

## \[2.0.0] - 2026-08-10

### Added

- **ComfyUI 工作流引擎架构**：Engine / Client / Workflow 三层抽象，支持多后端负载均衡

  - `comfy/client.py`：HTTP + WebSocket 双通道客户端，自动重连（≤3 次指数退避）

  - `comfy/engine.py`：ComfyEngine 实现 ImageEngine Protocol（load / unload / infer\_txt2img / cancel）

  - `comfy/workflow.py`：WorkflowManager Patcher 6 步（深拷贝→模式切换→link 重连→widgets patch→batch chunk→节点校验）

- **内置工作流**：Z-Image Turbo（高速低显存）

  - 每引擎一份 Schema YAML（`comfy/schemas/`），节点 ID 严格对齐 `widgets_values` 下标

- **VRAM 预检 + 精度推荐系统**：推理前估算显存需求（×1.5 系数），推荐 FP8/FP16 精度与 batch chunk 大小

- **批量任务队列**：异步单 Worker 串行 + SSE 实时推送 + 任务取消 + 断点恢复

  - batch>100 时每 100 张自动落盘 checkpoint，崩溃重启自动续跑

- **预设管理系统**：SQLite 存储，支持 CRUD + 导入导出 + 一键应用回填

- **历史记录系统**：SQLite（WAL + FTS5 全文检索），支持搜索 / 筛选 / 分页 / 批量删除 / ZIP 导出 / 标签

- **DCT 频域数字水印**：输出图像自动嵌入 `product_id + task_id + timestamp`，可溯源验证

  - `scripts/verify_watermark.py` CLI 验证工具

- **安全加固体系**：

  - PathGuard 路径防护（规范化校验，防 `../` 路径穿越）

  - CSRF 中间件（Token 头注入，防御跨站请求伪造）

  - Rate Limit 限流（推理 / 上传 / 全局三维度）

  - Integrity Manifest 完整性校验（SHA256 校验关键安全模块）

  - Basic Auth / API Token 鉴权（可配置开关）

- **i18n 五种语言**：中文 / 繁体中文 / 英文 / 日文 / 韩文，前端 JS 字典 + localStorage 持久化 + 防闪烁

- **8 种布局方案 Figma 原型对比**（`prototypes/figma-refactor/layout-compare/`）：

  - a-creative / b-split / c-collapsible / d-drawer / e-wizard / f-pipeline / g-master-detail / h-minimal

  - 最终选定 d-drawer（抽屉式）布局：移动端适配好、操作路径短、空间利用率高

- **GPU 状态监控**：SSE `gpu_status` 事件实时推送显存使用情况

- **实时预览**：WS `b_preview` → base64 → SSE `comfy_preview` → 前端采样中实时预览

- **释放显存功能**：`POST /api/engine/free` → ComfyUI `/free` → SSE 刷新

- **历史清理 cron**：`config.yaml` 配置 cron 表达式 + `keep_days` 保留天数

- **日志轮转**：RotatingFileHandler，按大小自动轮转保留 N 份

- **辅助脚本体系**（8 个）：

  - `benchmark.py`：性能基准（首页 / 历史 / health / SSE 四指标）

  - `check_wcag.py`：WCAG 无障碍检查

  - `generate_integrity_manifest.py`：完整性清单生成

  - `migrate_outputs.py`：输出目录结构迁移（旧平铺 → engine/date）

  - `pack_portable.ps1`：便携包 7 步打包

  - `setup_symlinks.ps1`：模型符号链接设置（shared 模式 Junction 维护）

  - `test_portable_mode.py`：便携模式验证

  - `verify_watermark.py`：水印 CLI 验证

- **测试体系**：40+ 个测试文件，287 passed / 0 failed

  - Hypothesis 属性测试、Factory Boy 测试工厂、PathGuard 攻击测试、SQL 注入测试

  - Playwright E2E（POM 页面对象模型 + 4 个场景）

- **Pre-commit 钩子**：ruff + format + trailing-whitespace + check-yaml 等 6 项

- **CI 工作流**：lint + test（3.12/3.13 矩阵）+ SAST（pip-audit）+ smoke 测试

- **Docker 支持**：Dockerfile + docker-compose.yml 双配置

- **WCAG AA 无障碍**：对比度校准（accent #6b5bb8 5.51:1 / primary #7c5fd6 4.70:1）

- **双模式模型路径**：`shared`（与 ComfyUI 共享）/ `portable`（项目自包含）

### Changed

- 从 v1.x 单体架构重构为 ComfyUI 客户端 / 服务端分离架构

- 前端从 Jinja2 + HTMX 多页模板改为单页融合版（SPA + REST + SSE）

- 历史存储从 JSON 文件改为 SQLite（WAL + FTS5）

- HTTP 客户端从 httpx 改为 aiohttp（与 ComfyUI WebSocket 生态兼容）

- 主题色从薰衣草紫 #8b7bd8 调整为 #6b5bb8（WCAG AA 对比度达标）

- 覆盖率门槛设为 75%（fail\_under=75）

### Security

- 加入 PathGuard 路径防护，修复路径穿越漏洞（14 类攻击全拒绝）

- 加入 CSRF 中间件，防御跨站请求伪造

- 加入 Rate Limit 限流，防止滥用

- 加入 Integrity Manifest，关键安全模块 SHA256 校验

- 加入 DCT 频域水印，输出图像可溯源

- 默认仅绑定 `127.0.0.1`，config.yaml host 字段只读

### Fixed

- `task_queue.py:97` f-string 语法错误（缺左花括号导致应用无法启动）

- 水印 DCT 嵌入 uint8 回绕问题（MIN\_Q 2→8、新增 MAX\_Q=16、引擎裁剪 \[0,255]）

- 集成测试 8 个 `UnraisableExceptionWarning` 清零

- outputs/ 旧平铺 PNG 迁移到 engine/date 目录结构

- `logging.handlers` 导入缺失导致 RotatingFileHandler 不工作

- i18n 新增 18 个 `btn_*` 键（5 语），消除界面裸键

- WCAG AA 对比度不达标色值修复

***

## \[1.0.0] - 2026-08-08

### Added

- 项目初始骨架：config.yaml + 2 个工作流 JSON + pretrained\_models 目录结构

- MASTER\_PLAN.md 总体规划文档（M0\~M10 里程碑分解）

- PRD.md 产品需求文档

- 基础测试：test\_config + test\_workflow（39 例）
