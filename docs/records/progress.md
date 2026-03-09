# PlaybookOS MVP 进展记录

## 当前状态

- 仓库位置：`/home/greed/playbookos-mvp`
- Git 状态：`master` 分支持续开发中，本文件会随每轮实现持续补记并在完成后推送
- 项目结构：`src/`、`tests/`、`docs/`、`data/` 已形成可运行 MVP，覆盖控制面、持久化、预览服务与前端 Dashboard
- 约束文件：当前未在仓库内发现额外的仓库级 `AGENTS.md`

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
- 已新增 `src/playbookos/object_store/service.py` 与 `src/playbookos/object_store/__init__.py`，提供本地对象存储能力，用于持久化原始 SOP 文本与元数据 sidecar
- `POST /api/playbooks/ingest` 与 preview server ingest 链路现在会自动保存原始 SOP，并把 `source_object_id / uri / checksum / mime_type` 回填到 `playbook.compiled_spec`
- 已新增 `GET /api/objects`、`GET /api/objects/{object_id}`、`GET /api/objects/{object_id}/content`，支持列出原始对象、读取元数据与直接查看原文内容
- Dashboard 的 `Skill 配置引导` 区块现会展示原始 SOP 已保存提示，并提供原文回看链接，方便用户在配置 Skill 时回审原文
- 已新增 `tests/test_object_store_unittest.py`，并扩充 ingestion / dashboard 测试覆盖对象存储与前端呈现
- 设计文档已更新：当前系统已具备“文本类 SOP 导入 -> Playbook/Skill 建议 -> authoring wizard 引导 -> 原文落对象存储”的第一版闭环；剩余缺口集中在任意格式附件解析、更多对象自动物化与更强的引导式配置
- 已把 SOP ingestion 的重点从“扩更多文件格式”调整为“打磨 Markdown SOP 的工具识别提示词链”：新增工具发现、Skill 上传、MCP 接入三类 prompt block，并在页面内直接回显
- ingest 结果现在会返回结构化 `tooling_guidance`，包含 required MCP、可复用 Skill 候选、下一步动作、工具证据与推荐提示词，帮助用户按 SOP 反推该上传哪些 Skill / MCP
- 已补上 `MCPServer` 控制面主链：内存/SQLite store、API、preview server、Dashboard 资源区与表单都已支持 MCP 的创建、查询与编辑
- SOP ingestion 的 `tooling_guidance` 现在会区分已登记 MCP 与缺失 MCP，并支持从引导卡片一键生成 `draft MCP`，把“识别工具 -> 补 MCP”真正串起来

- 已继续完成 `MCPServer` 控制面主链：内存/SQLite store、FastAPI、preview server、Dashboard 工作台与编辑器都支持 MCP 的创建、查询、更新
- 已新增 `POST /api/playbooks/{playbook_id}/mcp-drafts`，支持根据 SOP `tooling_guidance` 中的缺口一键生成 draft MCP
- ingest 结果现在会返回 `existing_mcp_candidates` / `missing_mcp_servers`，前端可直接把“已登记 MCP”和“仍缺的 MCP”区分展示
- Dashboard 已补齐 `materialize-mcp` 动作链，用户可从 SOP 工具引导卡片直接创建 draft MCP，并在页面上立即看到状态变化
- 已修复 `BoardSnapshot` API 响应模型遗漏 `mcp_servers` 统计的问题，避免前端看板漏显示 MCP 资源数量
- 已补齐 `playbookos.ingestion` 对 `materialize_required_mcp_in_store` 等对象的导出，修复 preview server / tests 的导入错误
- 已更新测试与文档，当前全量 `44` 个单测已全部通过：`python3 -m compileall src tests && PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'`

- 已完成前端重构的第一轮方案设计，并新增 `docs/ui-redesign.md`：把首页重新定义为“全局看板”，同时确定左侧导航、工作台节点、设置页、共享组件和分阶段实施 TODO
- 已明确新的导航结构：`全局看板` + `目标 / SOP / Skill / MCP / 知识库 / 任务 / 会话 / 自动迭代 / 审批流 / 提示词` + `模型设置 / 全局设置 / 会话管理`
- 已确认实现顺序：先做 `AppShell + 左侧导航 + 全局看板`，再把现有 Action Center / Session Tree / Patch Review / Authoring Wizard 等模块迁移到对应工作台页面

- 已开始落地前端重构第一阶段：Dashboard 现已具备 `AppShell` 壳层、左侧导航、顶部上下文栏和 hash 路由，默认打开即进入 `全局看板`
- 左侧导航已接入一级节点：`全局看板 / 目标 / SOP / Skill / MCP / 知识库 / 任务 / 会话 / 自动迭代 / 审批流 / 提示词 / 模型设置 / 全局设置 / 会话管理`，并按当前快照展示数量徽标
- 首页已新增 `任务流程总览` 区块，把 `Goal -> SOP -> Skill/MCP -> Task -> Run -> Acceptance/Reflection -> Knowledge` 做成可点击的全局链路摘要
- 本轮先重组前端壳层与信息架构，不改后端 API；后续继续把现有 Workbench / Action Center / Session Tree / Patch Review 分别迁移到对应页面

- 已继续完成前端重构第二阶段：`SOP / Skill / 审批流 / 提示词` 路由新增页面级 focus 卡片，进入对应工作台后会先看到该节点自己的状态摘要与待处理线索
- `Quick Resource Peek` 已改为按当前路由过滤资源样本，减少全局长列表噪音，让不同工作台只暴露最相关的对象
- 已修复本轮 Dashboard 重构过程中丢失的资源区 / 编辑器 / 提交处理函数，重新通过 `python3 -m compileall src tests`、`PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'` 与 `node --check /tmp/playbookos_dashboard_check.js`

- 已继续推进前端重构第三阶段：`MCP / 知识库 / 任务` 路由新增专属 `route detail` 内容区，分别展示 `MCP 注册表 / 接入缺口`、`知识条目 / 更新提案`、`任务队列 / 执行压力`
- Dashboard 现在除 `route focus` 外，还具备面向工作台的双栏内容区；进入 `MCP / 知识库 / 任务` 后，用户会先看到该节点的关键实体与待处理线索，再进入表单或编辑器
- 已补充 `tests/test_dashboard_unittest.py` 覆盖 `route-detail-section`、新路由映射与相关标题键，并再次通过 `python3 -m compileall src tests`、`PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'` 与 `node --check /tmp/playbookos_dashboard_check.js`

- 已继续补完整局看板第二阶段：新增 `关键阻塞区 / 推荐动作区`，首页现在会汇总 blocked goals、waiting_human runs、failed runs、rejected reflections 与 SOP 检测出的 missing MCP
- 推荐动作区会根据当前状态主动提示进入 `审批流 / MCP / Skill / 自动迭代 / 任务` 等工作台，不再只展示静态流程链与摘要卡
- 已补充 `tests/test_dashboard_unittest.py` 覆盖 `dashboard-alerts-section` 与 `renderDashboardAlerts()`，并再次通过 `python3 -m compileall src tests`、`PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'` 与 `node --check /tmp/playbookos_dashboard_check.js`

- 已继续推进前端重构第四、五阶段：`会话 / 自动迭代` 路由新增专属 `route detail` 内容区，`模型设置 / 全局设置 / 会话管理` 也开始展示实时摘要
- `会话工作台` 现在会先展示最新 supervisor / worker 会话、绑定 task/run、child session 与 event 信号；`自动迭代工作台` 会先展示 reflection / knowledge update 流水线和待处理学习队列
- 设置页不再只是静态占位卡：现已显示最近一次模型调用配置、当前 UI/API 状态和 session/event 实时计数

- 已继续补完整局看板第三阶段：新增 `进行中任务区 / 自动迭代动态区`，首页现在会主动展示 ready/running/waiting_human 任务，以及最近的 reflection / knowledge update / draft capability 信号
- 到目前为止，全局看板六块核心信息都已具备：系统摘要、流程总览、关键阻塞、推荐动作、进行中任务、自动迭代动态
- 已补充 `tests/test_dashboard_unittest.py` 覆盖 `dashboard-tasks-section`、`dashboard-learning-section`、`renderDashboardTaskSections()` 与 `renderDashboardLearningSections()`

- 已把顶部 `全局范围` 做成真实筛选器：新增二级值选择，支持按 `Goal / SOP / 状态` 过滤页面数据，而不再只是静态下拉框
- 当前筛选会联动全局看板、工作台摘要、资源速览、操作区、会话/学习/设置页摘要，以及左侧导航计数
- 已补充 `tests/test_dashboard_unittest.py` 覆盖 `global-scope-value-select`、`applyGlobalScope()`、`scopeOptions()` 与 `filterResourcesByScope()`

- 已继续完成设置页第一块真实可编辑能力：新增 `src/playbookos/runtime_settings.py`，把模型运行时配置从纯环境变量读取扩展为“环境变量默认值 + 本地 JSON 覆盖”的统一存储层
- Preview Server 与 FastAPI API 均已新增 `GET /api/runtime-settings`、`PUT /api/runtime-settings`，并把 `autopilot / execute` 的 `OpenAIAgentsSDKAdapter` 配置切换为运行时设置对象
- Dashboard 的 `模型设置` 页面已从静态摘要升级为可编辑表单，支持修改 `base_url / model / api_format / timeout / temperature / max_output_tokens / organization / project / api_key`，并支持 masked API Key 展示与保存后即时刷新
- 已新增 `tests/test_runtime_settings_unittest.py`，覆盖运行时设置存储的 merge / 持久化 / clear api key；并扩展 `tests/test_dashboard_unittest.py` 校验模型设置入口、读写 API 调用与保存按钮
- 本轮已再次通过 `python3 -m compileall src tests`、`PYTHONPATH=src python3 -m unittest tests/test_dashboard_unittest.py tests/test_runtime_settings_unittest.py tests/test_preview_server_unittest.py` 与 `node --check /tmp/playbookos_dashboard_runtime.js`

- 已继续把设置页第二块做实：`runtime-settings` 现已从仅包含 `model` 扩展为统一的 `model + global` 运行时配置，支持默认语言、自动刷新、默认范围、默认路由和系统导航显隐
- Dashboard 的 `全局设置` 页面现已可编辑并真正驱动 UI：无本地覆盖时会应用默认语言 / 默认筛选 / 默认路由，并按配置启动自动刷新定时器
- 已新增 `PUT /api/sessions/{session_id}`（FastAPI 与 Preview Server 均已接入），`会话管理` 页面现支持按 Goal / Run 过滤 session，并修改 session 的状态、标题、objective 与 summary
- 已扩展 `tests/test_runtime_settings_unittest.py` 覆盖全局设置字段，并扩展 `tests/test_dashboard_unittest.py` 覆盖 `global-settings` / `session-admin` 新表单与会话保存入口

- 已继续增强 `模型设置`：运行时设置现在会返回 `provider_presets`，并内置 `OpenAI / Responses`、`OpenAI / Chat Completions` 与 `Custom OpenAI-Compatible` 三个 preset
- 已新增 `RuntimeSettingsStore.test_model_settings()` 与 `POST /api/runtime-settings/test`（FastAPI / Preview Server 均已接入），可对当前模型配置执行轻量 probe，并返回 `missing_api_key / ok / error` 等明确状态
- Dashboard 的 `模型设置` 页面已新增 preset 下拉、一键应用 preset 按钮和 `测试连通性` 按钮；测试结果会在设置摘要区和状态栏中直接回显
- 已扩展 `tests/test_runtime_settings_unittest.py` 覆盖 preset 列表、missing key probe、transport probe；并扩展 `tests/test_dashboard_unittest.py` 覆盖 preset/test 控件与 `runtime-settings/test` 调用入口

- 已继续补齐 `模型设置` 的环境化能力：运行时设置现已支持 `model_profiles`、`active_model_profile` 与 `last_successful_model_test`，可以保存命名模型环境并切换当前生效配置
- 已新增 `POST /api/runtime-settings/profiles`、`POST /api/runtime-settings/profiles/activate`（FastAPI / Preview Server 均已接入），Dashboard 现支持“保存为环境”与“切换环境”
- 最近一次成功的模型连通性测试现在会被持久化保存，不再只是前端临时状态；页面会直接显示最近成功配置摘要
- 已顺手增强 `全局设置`：新增 `environment_label`，并在设置摘要里展示当前环境标签，方便后续扩展多环境治理视角

- 已完成设置页这一轮增强：`模型设置` 现支持命名环境（profile）保存/切换、最近成功 probe 状态展示，以及从已保存环境回填表单做检查
- `全局设置` 已补充 `environment_label`，可在 UI 中保存并回读，作为当前实例/环境的显式标识
- `runtime settings` API 现已补齐 profile 保存/激活接口，并对非法输入返回 `400`，避免前端设置页因空名称或错误载荷触发 `500`
- 已将 `data/runtime_settings.json` 纳入 `.gitignore`，避免 demo 运行时生成的本地配置污染仓库状态
- 已再次通过 `python3 -m compileall src tests`、`PYTHONPATH=src python3 -m unittest discover -s tests -p 'test*_unittest.py'` 与 Dashboard JS `node --check`
- 已重启公网预览 `http://20.200.217.83:8081/` 并确认 `GET /api/runtime-settings`、`POST /api/runtime-settings/profiles/activate` 以及首页设置页脚本均返回最新实现

- 已重新审计 `README.md`，把文档内容收敛到当前真实实现：补齐实际存在的 API、设置页能力、Dashboard 结构，并移除对多格式 SOP / 未落地能力的过度表述
- 已按当前产品计划把 `SOP ingestion` 逻辑收敛到 `Markdown-first`：非 Markdown `source_kind` 现在会直接返回明确错误，避免文档与产品策略不一致
- 已优化 `tooling_guidance` 的当前逻辑：action items 现在会按“先复用已登记 MCP / Skill，再补缺口，再绑定步骤”的顺序输出，prompt blocks 也会显式带上已有候选与缺口上下文
- Dashboard 的 SOP 导入表单已同步收敛为 `Markdown only`，避免用户在 UI 中误以为当前版本已经支持 `json/txt/csv` ingestion

- 已开始补 `MCP runtime / credential / health` 的第一步：新增 `MCP health probe`，可对已登记 MCP endpoint 做轻量探测并回写最近一次健康状态
- FastAPI 与 Preview Server 均已新增 `POST /api/mcp-servers/{mcp_server_id}/probe`；Dashboard 的 `MCP` 工作台现在可直接点击 `Probe MCP` 并查看最近一次探测结果
- 当前实现仍然不是完整 MCP runtime，但已经把“有没有登记 MCP”推进到“这个 MCP 现在能不能连上”

- 审查 Dashboard 真实渲染后又修掉了一处 MCP 工作台脚本问题：`join('\n')` 在 Python 模板里会落成非法 JS 换行，现已统一修正为安全转义，避免页面在浏览器里静默失效

- 已把“PlaybookOS 不只给人类看，也要给外部 agent 作为控制面使用”的方向落进文档，并新增 `docs/agent-operator.md` 作为第一版方案记录
- 已新增 agent-friendly 接口：`GET /api/agent/manifest`、`GET /api/agent/context`、`POST /api/agent/intake`，供 OpenClaw 这类 agent 用于能力发现、上下文同步与对话转操作计划
- 已在仓库中新增 `skills/playbookos-operator/`，让外部 agent 安装代码和 skill 后即可理解 PlaybookOS 的对象、工作流与安全操作顺序

- 已新增 `DelegationProfile` 第一版及其控制面接口：`GET/POST/PUT /api/delegation-profiles*`，用于为外部 agent 定义允许路由、审批门槛与单次 apply 上限
- 已新增 `POST /api/agent/apply`：在重新计算 intake 计划后，按 `operation_ids` 执行受 delegation 约束的一组 builder 操作，并把 agent 身份写入事件来源

- 已新增 `docs/managed-agent-demo.md`，把当前已跑通的 `manifest -> delegation profile -> agent apply -> playbook/skill/mcp draft` 演示链记录为项目示例
- 已把 agent 治理与错误日志等后续细节统一沉淀进文档 TODO，并明确当前策略是 `runnable-first`：先确保完整主链跑通，再逐步补日志、审计、回滚与托管巡检

- 已重写仓库根 `README.md`，把文档改为中英双语，并补齐项目定位、当前真实能力、快速启动、OpenClaw / 外部 agent 接入方式、关键接口、限制与文档索引

- 已在 `README.md` 中补充 OpenClaw / 外部 agent 的 `5 分钟跑通示例`，包含 `manifest -> context -> intake -> delegation profile -> apply` 的完整 curl 流程

- 已按“中文主 README + 英文独立 README-EN”重构仓库说明文档，去掉同段中英混排，并保持两份文档的结构一致
- 已新增 `scripts/openclaw_demo.sh`，把 OpenClaw / 外部 agent 的演示升级为可执行脚本：自动完成 `manifest -> context -> intake -> delegation profile -> apply`

- 已基于 `progress / iteration-memory / git log` 重新整理本轮完整建设脉络，并新增 `docs/records/building-playbookos-story.md`，记录 PlaybookOS 从控制面骨架、Markdown SOP ingestion、执行闭环、前端重构、设置治理到 OpenClaw / agent 接入面的逐步搭建过程
- 已把本轮参考统计一并记入建设文章：工具 `Codex`、模型 `GPT-5.4`、总耗时约 `24h`、总请求数约 `2235` 次、总 Token 约 `432M`

- 已新增对外可发布版本的建设文章 `docs/articles/how-we-built-playbookos.md`，将本轮 24h 搭建过程整理为更适合外部阅读的叙事文章
- 已在 `README.md` 与 `README-EN.md` 末尾追加“接下来的工作目标与改进方向”，明确 P0-P4 主线、暂缓项与后续 roadmap 收敛原则
