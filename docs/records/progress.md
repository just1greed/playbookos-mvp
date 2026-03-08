# PlaybookOS MVP 进展记录

## 当前状态

- 仓库位置：`/home/greed/playbookos-mvp`
- Git 状态：`master` 分支，当前还没有任何提交
- 项目结构：已包含 `src/`、`tests/`、`docs/`、`data/` 目录，但暂时没有实际代码文件
- 约束文件：当前未在仓库内发现额外的 `AGENTS.md`

## 协作约定

- 我会把每次重要变更、决策和已完成事项追加记录到这个文件
- 当你给出下一步目标后，我会先实现，再同步更新这里的进展

## 会话记录

### 2026-03-08

- 已定位 `playbookos-mvp` 项目
- 已确认仓库目前基本为空壳
- 已建立项目内进展记录文件
- 已补充 `README.md`，明确 PlaybookOS 的产品定位与分层方案
- 已新增 `docs/prd.md`、`docs/architecture.md`、`docs/data-model.md`、`docs/mvp-plan.md`
- 已建立 `pyproject.toml` 与 `src/playbookos/` Python 包骨架
- 已实现八个核心对象的第一版领域模型：Goal、Playbook、Skill、MCPServer、Task、Run、Artifact、Reflection
- 已新增基础测试文件 `tests/test_domain_models.py`
- 已使用 `python3 -m compileall src` 完成语法校验
- 已使用 `PYTHONPATH=src python3` 完成领域模型实例化校验
- 当前环境未提供 `python` 与 `pytest` 命令别名，后续如需完整测试可补装或切到已有 Python 工具链环境
- 已开始 Milestone 2，优先实现控制面 API 骨架
- 已新增 `src/playbookos/api/store.py`，提供内存版 repository/store 与看板聚合快照
- 已新增 `src/playbookos/api/schemas.py`，定义 Goal、Playbook、Task、Run、Reflection 等 API 请求/响应模型
- 已新增 `src/playbookos/api/app.py`，提供 FastAPI 应用、健康检查、元数据接口、Board 接口与核心资源路由
- 已在 `pyproject.toml` 中补充 `fastapi`、`uvicorn` 依赖和 `playbookos-api` 启动脚本
- 已更新 `README.md`，补充 API 列表与本地启动方式
- 已新增 `tests/test_api_store_unittest.py`，覆盖内存存储与看板快照基础行为
- 已修正 `playbookos.api` 包的导入耦合，避免在未安装 FastAPI 时影响存储层测试
- 已将时间戳生成切换为时区感知 UTC，消除 Python 3.12 的 `utcnow()` 弃用告警
- 已完成 `python3 -m compileall src tests` 语法校验
- 已完成 `python3 -m unittest tests/test_api_store_unittest.py` 校验
- 当前环境未安装 `fastapi`，因此尚未实际启动 HTTP 服务；代码和依赖声明已准备好，安装依赖后即可运行 API
- 已将 API 存储依赖抽象为 `RepositoryProtocol` / `StoreProtocol`，解除控制面与具体存储实现的耦合
- 已新增 `src/playbookos/persistence/sqlite_store.py`，提供基于 `sqlite3` 的持久化 repository/store 实现
- API 默认存储已从纯内存切换为 SQLite 持久化，默认数据库文件为 `data/playbookos.db`
- 已新增 `data/sql/postgres_schema.sql`，定义正式部署可用的 PostgreSQL 主表 schema 草案
- 已新增 `data/sql/sqlite_schema.sql`，同步保留本地开发 schema 文件
- 已更新 `README.md` 与 `docs/data-model.md`，补充持久化策略、环境变量与 schema 文件位置
- 已新增 `tests/test_sqlite_store_unittest.py`，验证实体跨实例持久化与看板聚合快照
- 已完成 `python3 -m unittest tests/test_api_store_unittest.py tests/test_sqlite_store_unittest.py` 校验
- 当前 API 运行时已经具备持久化能力；PostgreSQL 运行时 adapter 尚未接入，但 schema 与 repository 边界已准备好
- 已新增 `src/playbookos/planner/service.py`，实现 `PlaybookPlanner` 与 `plan_goal_in_store`
- planner 已支持基于 `compiled_spec.steps` 生成 `Task DAG`，支持默认串行依赖和显式 `depends_on` 解析
- 已新增 `POST /api/goals/{goal_id}/plan` 接口，用于显式执行规划并返回本次任务生成摘要
- `POST /api/goals/{goal_id}/start` 现已自动触发 planner，并保持重复启动不重复创建任务
- 已新增 `tests/test_planner_unittest.py`，覆盖 DAG 生成、幂等规划与错误依赖校验
- 已完成 `python3 -m unittest tests/test_api_store_unittest.py tests/test_sqlite_store_unittest.py tests/test_planner_unittest.py` 校验
- 已新增 `src/playbookos/orchestrator/service.py`，实现本地可运行的编排核心与 `TemporalWorkflowSpec`
- orchestrator 已支持提升可执行任务、创建 `Run`、等待人工审批状态，以及任务完成后的下游推进
- 已新增 `POST /api/goals/{goal_id}/dispatch` 和 `POST /api/tasks/{task_id}/complete` 接口
- `POST /api/goals/{goal_id}/start` 现已串起 planner + orchestrator，能从 Goal 直接进入调度
- 已增强 `POST /api/runs/{run_id}/approve` / `reject` 的任务与 Goal 状态联动
- 已新增 `tests/test_orchestrator_unittest.py`，覆盖调度、下游推进、审批等待与 Goal review 转换
- 已新增 `src/playbookos/executor/service.py`，实现 `OpenAIAgentsSDKAdapter`、本地执行器和 `autopilot_goal_in_store`
- 已新增 `src/playbookos/reflection/service.py`，实现单次 Run 反思与 Goal 级学习汇总
- 已新增 `POST /api/runs/{run_id}/execute`、`POST /api/runs/{run_id}/reflect`、`POST /api/goals/{goal_id}/autopilot`、`GET /api/goals/{goal_id}/learning`
- executor 现已支持基于 Playbook 步骤和 MCP 列表构造 OpenAI Agents SDK 风格执行载荷
- 已补上“自动跑大量相似任务 + 产出 SOP patch proposal”的第一版骨架，但仍保留人工批准，不直接自动发布到生产
- 已新增 `tests/test_executor_reflection_unittest.py`，覆盖 run 执行、reflection proposal 与 autopilot 学习摘要
- 已完成 `python3 -m unittest tests/test_api_store_unittest.py tests/test_sqlite_store_unittest.py tests/test_planner_unittest.py tests/test_orchestrator_unittest.py tests/test_executor_reflection_unittest.py` 校验
- 已将 `Artifact` 从领域模型接入到实际存储链路，新增 `store.artifacts` in-memory/SQLite repository
- 已更新 `data/sql/sqlite_schema.sql` 与 `data/sql/postgres_schema.sql`，补充 `artifacts` 主表定义
- 已新增 `POST /api/artifacts`、`GET /api/artifacts`、`GET /api/artifacts/{artifact_id}` 接口
- `execute_run_in_store` 现会自动生成 `run_report` Artifact，持久化输出摘要、trace、tool_calls 与 metrics
- 已更新 `RunExecutionRead` 与 board snapshot，支持返回 `artifact_ids` 并聚合 artifact kind 计数
- 已增强 `tests/test_api_store_unittest.py`、`tests/test_sqlite_store_unittest.py`、`tests/test_executor_reflection_unittest.py`，覆盖 Artifact 存储、持久化与执行联动
- 已完成 `PYTHONPATH=src python3 -m unittest tests/test_api_store_unittest.py tests/test_sqlite_store_unittest.py tests/test_executor_reflection_unittest.py` 校验

- 已新增 `src/playbookos/ui/dashboard.py`，提供无外部前端依赖的单页控制台 HTML 生成器
- 已在 `src/playbookos/api/app.py` 新增 `GET /` 首页路由，直接渲染 PlaybookOS Dashboard
- Dashboard 已支持展示 board summary、资源入口、最近资源预览与 snapshot JSON 调试视图
- 已新增 `tests/test_dashboard_unittest.py`，覆盖首页 HTML 骨架、API 入口和转义安全
- 已完成 `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'` 全量校验
- 已完成 `python3 -m compileall src tests` 语法校验
