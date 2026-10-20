# staging 部署与 post-deploy smoke（P2-11）

> 评估依据：`OPS_STABILITY_ASSESSMENT_v2.0.0.md` §9-P2-11
> 检查脚本：`scripts/post_deploy_smoke.py`
> CI 门禁：`ci.yml → post-deploy-smoke`（每次 push 演练）+ `deploy.yml → staging`（配置了 staging secrets 才是真部署，否则同为演练，见 §5）
> 单元测试：`tests/release/test_post_deploy_smoke.py`

## 1. 目的

发布/晋级前自动验证部署后的服务真的可用，**smoke 失败即阻断晋级，不允许仅打印日志**。

## 2. 六项检查

| # | 检查 | 端点 | 判定标准 |
|---|---|---|---|
| 1 | health | `GET /api/health` | 200 且 `status ∈ {ok, healthy, degraded}` |
| 2 | config | `GET /api/config` | 200 且 `runtime.task_queue.maxsize > 0` |
| 3 | engines | `GET /api/engine/engines` | 列表包含 `z_image_turbo_native` |
| 4 | generation | `POST /api/generate` → 轮询 `GET /api/tasks/{id}` | 假任务在超时内 completed |
| 4b | generation_output | 同上 + 校验 `outputs` | **仅 `--require-real-output` 时启用**：产物文件真实存在、字节数 > 0、像素尺寸与请求一致 |
| 5 | queue_protection | `GET /api/metrics/prometheus` | 暴露 `queue_depth` 与 `queue_rejected_total`（P1-8 保护已装载） |
| 6 | sse | `GET /api/events` | 建流成功且收到首块字节 |

CSRF：脚本预热时从 `/api/health` 响应头取 `X-CSRF-Token`，并以「头 + 同名 cookie」双重提交方式访问 POST 端点（与 `middleware/csrf.py` 的双重提交校验匹配）。

> ⚠️ **为什么需要 `--require-real-output`（Gotcha #47）**
> `IMM_FAKE_ENGINE=1` 下任务同样会走到 `completed`，只断言状态会给**假绿灯**——
> 服务可能根本没落盘、或落了 0 字节。晋级门禁必须带上 `--require-real-output`，
> 让第 4 项从 `generation_completed` 升级为 `generation_output`（校验产物实体）。
>
> DB 元数据（`file_size`/`width`/`height`）为空时，脚本会**回退到磁盘 stat + PIL 读尺寸**再判定，
> 避免真实部署因元数据缺失被误判为失败（Gotcha #49）；回退次数会写进检查项说明里便于追溯。
> 若产物路径前缀为 `imm_fake`，说明引擎是假实现，**直接判失败**不参与晋级。

## 3. 用法

```bash
# 对已部署环境跑全量检查
python scripts/post_deploy_smoke.py --base-url http://staging:8288 --timeout 15 --output smoke_report.json

# 只跑读路径（快速探活）
python scripts/post_deploy_smoke.py --base-url http://staging:8288 --checks health,config,engines

# 晋级门禁用法：带上 --require-real-output，校验产物真实落盘
python scripts/post_deploy_smoke.py --base-url http://staging:8288 --timeout 15 \
  --generation-timeout 120 --require-real-output --output smoke_report.json

# 失败时 exit code = 1（CI / 部署脚本据此阻断晋级）
python scripts/post_deploy_smoke.py --base-url http://staging:8288 || { echo "SMOKE FAILED — 停止晋级"; exit 1; }
```

## 4. 晋级流水线（deploy.yml）

```
release.yml（打 tag → 构建不可变镜像 → SBOM）
        │ workflow_run
        ▼
deploy.yml:staging（部署 staging → post_deploy_smoke 门禁 → 通过才标记 active slot）
        │ needs: staging（smoke 失败时 job 已红，无法进入）
        ▼
deploy.yml:production（人工批准 + blue-green promote + 观察窗口 + 自动回退，见 P2-12）
```

要点：

- `smoke` 步骤**没有** `continue-on-error`，失败即 job 失败；
- 「标记 active slot」步骤仅在 `steps.smoke.outcome == 'success'` 时执行，失败版本永远不会接管流量；
- 显式增加 `Block promotion on smoke failure` 步骤，输出可操作的失败摘要；
- `smoke_report.json` 以 artifact 形式保留，供复盘。

## 5. 无 staging secrets 时的演练模式

未配置 `STAGING_HOST/USER/SSH_KEY`（即仓库变量 `HAS_STAGING_SECRETS != 'true'`）时，
`deploy.yml:staging` 在托管 runner 上 `docker build` 真实镜像 + `docker run -e IMM_FAKE_ENGINE=1`
起服，**在容器内**（`docker exec`）跑同一份 `post_deploy_smoke.py`，再 `docker rm -f` 拆服。
`ci.yml` 的 post-deploy-smoke job 走 uvicorn + `IMM_FAKE_ENGINE=1`，两者同源。

演练覆盖的是「镜像能构建、服务能起、6 项检查跑通、失败能阻断晋级」这条**门禁管道**，
**不等于**真实环境验证：fake engine 无真实产物、无 GPU、无网络边界。因此
`deploy.yml:production` 的首个步骤会在 `HAS_STAGING_SECRETS != 'true'` 时**硬失败拒绝晋级**，
而不是静默跳过。

> ⚠️ **演练为什么必须绕开 docker compose（两个独立原因）**
> 1. `docker-compose.yml` 与 `docker-compose.bluegreen.yml` 无条件声明
>    `deploy.resources.reservations.devices: driver=nvidia`，托管 runner 无 nvidia 容器工具链，
>    `docker compose up` 直接报 `could not select device driver "nvidia"`
>    （CI 34612430147 即败于此，此后 Deploy 无一次成功）。
> 2. `config.yaml` 的 `server.host: 127.0.0.1` 使容器内只监听回环，主机侧 `-p` 转发打不进去，
>    故探活与 smoke 都必须在容器内执行。

> ⚠️ **演练模式不加 `--require-real-output`**：`IMM_FAKE_ENGINE=1` 下产物路径前缀为 `imm_fake`，
> 脚本对其直接判失败，开启产物校验会 100% 红。该 flag 的启用位置：
> `deploy.yml:staging`（仅 `HAS_STAGING_SECRETS == 'true'` 分支）、
> `scripts/deploy/bluegreen.sh` 的 `smoke_full()`。

## 6. 验收对照（§9-P2-11）

- [x] 部署后自动检查 health / config / engine list / 假生成任务 / 队列满保护 / SSE；
- [x] smoke 失败自动停止晋级（exit 1 + job 红 + slot 不切换 + production needs 不满足）；
- [x] 每项检查有独立单测（22 项，含失败路径与退出码断言）；
- [x] 已在真实 uvicorn + fake engine 上端到端验证（6 项全过，用时 ~3s）；
- [x] **产物实体校验**：`--require-real-output` 校验文件存在 / 非 0 字节 / 尺寸一致，
      拒绝 `imm_fake` 假产物，DB 元数据缺失时回退磁盘 stat（6 项新增单测覆盖）。
