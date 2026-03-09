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

- 已新增 `src/playbookos/ui/preview_server.py`，提供零依赖的本地 Dashboard 预览服务
- 已新增 `tests/test_preview_server_unittest.py`，覆盖 demo store 的 dashboard 数据填充

- 已新增 `src/playbookos/observability/error_log.py`，以 JSONL 文件形式记录运行中遇到的错误
- 已在 preview server 与 FastAPI API 的核心错误路径接入 `record_error`
- 已新增 `GET /api/errors` 与 preview `GET /api/errors`，可直接查看错误记录文件内容
- preview server 默认端口已切换为 `8081`
- 已新增 `tests/test_error_log_unittest.py`，覆盖错误记录文件的写入与读取

- 已将 `Skill` 从领域模型接入到 in-memory / SQLite store 与 board snapshot 聚合
- 已新增 `POST /api/skills`、`GET /api/skills`、`GET /api/skills/{skill_id}` 接口
- `POST /api/tasks` 现在会校验 `assigned_skill_id`，支持手动把 Skill 绑定到 Task
- Dashboard 现已展示 `Skills` 维度，并在 demo preview 中注入示例 Skill
- 已新增 `tests/test_skill_store_unittest.py`，覆盖手动创建 Skill 与任务绑定
- 已新增 `docs/records/iteration-memory.md`，记录当前完成度、缺口和推荐下一优先级

- 已新增 `Session`、`Acceptance`、`Event` 领域模型，并接入 in-memory / SQLite store
- 已新增 `src/playbookos/supervisor/service.py`，用于维护 Goal 主控会话、Run 子会话、验收与事件流
- `dispatch_goal_in_store` 现会自动创建 supervisor / worker session，并生成 `run.created` 等事件
- `execute_run_in_store` 现会同步更新 worker session 的状态、summary 与输出上下文
- 已新增 `GET /api/sessions`、`GET /api/acceptances`、`GET /api/events`、`POST /api/tasks/{task_id}/accept`
- Dashboard 与 preview server 已展示 `skills / sessions / acceptances / events`，并继续支持中英文切换
- 已新增 `tests/test_supervisor_unittest.py`，覆盖会话生成、验收与事件链路
- 已完成 `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'`，共 21 项测试通过

- 已新增 `KnowledgeBase` 模型，并接入 in-memory / SQLite store、board snapshot 与 demo 数据
- 已新增 `POST /api/knowledge-bases`、`GET /api/knowledge-bases`、`GET /api/knowledge-bases/{knowledge_id}`
- `Playbook import` 现支持直接提交 `compiled_spec`，可从前端表单手动录入 SOP 步骤与 MCP 列表
- Dashboard 已升级为可写工作台，支持在页面中直接创建 Goal、SOP、Skill、Knowledge、Task
- preview server 已支持 `POST /api/goals`、`POST /api/playbooks/import`、`POST /api/skills`、`POST /api/knowledge-bases`、`POST /api/tasks`
- 已新增 `tests/test_knowledge_store_unittest.py`，并更新 dashboard / preview / store 相关测试
- 已完成 `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'`，共 23 项测试通过

- 已新增 `PUT /api/goals/{goal_id}`、`PUT /api/playbooks/{playbook_id}`、`PUT /api/skills/{skill_id}`、`PUT /api/knowledge-bases/{knowledge_id}`、`PUT /api/tasks/{task_id}`
- preview server 已支持对应 `PUT` 能力，使 8081 工作台可以直接编辑既有实体
- Dashboard 已新增实体详情 / 编辑器面板，支持选择已有 Goal / SOP / Skill / Knowledge / Task 并保存修改
- 已更新 `tests/test_dashboard_unittest.py`，覆盖编辑器入口与 `putJson` 客户端逻辑
- 已再次完成 `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'`，共 23 项测试通过

- 已新增 `Task.knowledge_base_ids`，任务执行时可显式读取知识库条目
- 已新增 `KnowledgeUpdate` 模型与 `src/playbookos/knowledge/service.py`，支持由执行/反思链路自动生成知识回写提案
- `reflect_run_in_store` 现会同步生成 `KnowledgeUpdate`，`analyze_goal_learning` 也会聚合知识提案摘要
- 已新增 `GET /api/knowledge-updates`、`GET /api/knowledge-updates/{knowledge_update_id}`、`POST /api/knowledge-updates/{knowledge_update_id}/apply`、`POST /api/knowledge-updates/{knowledge_update_id}/reject`
- preview server 已支持 `knowledge_updates` 查询和 apply / reject API
- Dashboard 已把 `knowledge_updates` 纳入资源可视区，Task 创建表单也可直接绑定 `knowledge_base_ids`
- 已新增 `tests/test_knowledge_update_unittest.py`，并扩充 executor/reflection/dashboard/preview 测试
- 已完成 `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'`，共 25 项测试通过

- 已修复 Dashboard 空白页问题，根因是生成 JS 时 `splitLines` 的换行正则被错误转义，导致浏览器脚本启动即报语法错误
- Dashboard 现已新增页面内可见的 boot error 面板；如果前端再报错，用户可直接看到错误详情而不是只看到空框架
- 已使用 `node --check` 校验生成后的前端脚本语法
- 已使用 `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'` 完成全量回归，25 项测试通过
- 已重启本地 demo 预览服务到 `http://127.0.0.1:8081/` 并确认页面已渲染出“控制看板 / 配置工作台”等实际内容

- Dashboard 已新增“操作中心”，把 Goal 编排、Run 审批、Task 验收、Knowledge Update 应用/拒绝、Reflection 评测/批准/发布整合到一个用户可见界面
- preview server 已补齐对应动作接口：`goal plan/dispatch/autopilot`、`run execute/approve/reject/reflect`、`task accept/complete`、`reflection evaluate/approve/reject/publish`
- 已再次使用 `node --check` 校验生成 Dashboard 脚本，并用无头浏览器确认 `8081` 页面渲染出“操作中心 / 目标编排 / 人工审批 / 复盘 / 知识更新”等实际内容

- 已新增 Skill 版本服务，支持 `create-version`、`activate`、`deprecate`、`rollback` 四类版本生命周期动作
- Dashboard 已新增“技能版本中心”，集中展示版本链、当前激活版本、回滚目标与相关动作
- preview demo 数据已补齐真实 Skill 版本链，便于在 `8081` 直接看到版本演进与回滚入口
- 已补上主控聚合会话刷新逻辑：supervisor 会按 Goal 自动汇总 task/run/acceptance/reflection/knowledge update/session/event 状态
- 执行链路现在会在 worker 下生成可见子会话：`Context synthesis`、`AI execution`、`Supervisor verification`、`Reflection and learning`
- Dashboard 已新增“主控聚合中心”，直接展示主进程收集、检测、学习与事件汇总结果
- dispatch 现在会生成可见 `Dispatch wave` 会话，把同批 ready task 放进同一个并行波次父会话下
- supervisor 现在会维护 `Supervisor arbitration` 子会话，并输出下一步推荐动作、待人工审批、待验收、待评测/发布学习项等仲裁结果
- Dashboard 的主控聚合中心已扩展出仲裁区块，展示并行波次、推荐动作与待处理事项

- 已把 `OpenAIAgentsSDKAdapter` 升级为真实可配置 API 适配层，支持 `responses` / `chat.completions` 两种请求格式，并读取当前环境变量配置
- preview server 的 `/api/runs/{id}/execute` 与 `/api/goals/{id}/autopilot` 已切到真实 OpenAI 适配层；未配置 API Key 时会保留 prepared payload 供页面可见审计
- Dashboard 已新增“执行检查器”，集中展示 request payload、tool call 记录、配置摘要与执行结果
- 已把设计回顾结论同步进文档，明确当前最大缺口在前置建模链：`SOP ingestion -> compiler/parser -> skill recommendation -> authoring wizard`
- 已开始实现该链路的第一步：支持把原始 SOP 文本导入为 Playbook，并返回解析摘要与 Skill 建议
- 已新增 `src/playbookos/ingestion/service.py`，提供原始 SOP `markdown/text/json` 解析、MCP 线索提取和 Skill 建议生成
- 已新增 `POST /api/playbooks/ingest`，可把原始 SOP 文本导入为已编译 Playbook，并返回步骤数、MCP 提示、解析说明与 Skill 建议
- Dashboard 工作台已新增原始 SOP 导入表单，支持读取本地文本文件、展示解析摘要，并自动把首个 Skill 建议预填进 Skill 表单
- 已新增 `tests/test_ingestion_unittest.py`，并通过全量 `36` 个单测
- 已新增 `POST /api/playbooks/{playbook_id}/skill-drafts`，支持把某条 Skill 建议一键物化为 `draft Skill`
- Dashboard 的 Skill 建议卡已支持“一键创建 Draft Skill”与“创建并绑定步骤”，并会在页面内回显已创建结果
- 若选择“创建并绑定步骤”，会把未绑定的 `compiled_spec.steps[].assigned_skill_id` 自动回填，供后续 planner 直接产出带 Skill 的任务
- 当前全量单测已更新为 `38` 个并全部通过
- 已新增 `src/playbookos/authoring/service.py`，为 draft Skill 生成 authoring pack，补齐 input/output schema、approval policy、evaluation policy 的推荐默认值
- 已新增 `GET /api/skills/{skill_id}/authoring-pack` 与 `POST /api/skills/{skill_id}/apply-authoring-pack`
- Dashboard 已新增 `Skill Authoring Wizard` 区块，可对 draft Skill 一键应用推荐配置，并跳转到编辑器继续细修
- 已新增 `tests/test_authoring_unittest.py`，当前全量单测已更新为 `40` 个并全部通过
