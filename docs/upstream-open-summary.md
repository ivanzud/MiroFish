# Upstream Triage Snapshot

- Repository: `666ghj/MiroFish`
- State filter: `open`
- Captured: `2026-03-11T17:34:01.772369+00:00`
- Issues: `39` total (`open=39`, `closed=0`)
- Pull requests: `37` total (`open=37`, `closed=0`)
- Mirrored in `origin`: `37` of `37` PR refs
- Mirrored in `ivanzud/MiroFish`: `39` of `39` issues
- Local issue coverage map: `docs/upstream-coverage.json`

## Recently Updated Issues

- #149 [open, mirror=#90] 一直卡在 Waiting for agent actions (question)
  - local coverage [covered]: Step 3 now reconciles stale persisted `running` states when the worker PID is gone, and the detailed status payload exposes compact simulation-log diagnostics while waiting for the first actions. That prevents indefinite "Waiting for agent actions" polling after a dead worker and makes true startup stalls visible in the UI.
  - <img width="947" height="398" alt="Image" src="https://github.com/user-attachments/assets/09b45da5-150c-4d3b-82c0-6ba2204c1743" />
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @jidancong! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这个问题通常是因为后端的 agent 动作数据没有正确生成或传递到前端。以下是几个常见原因和排查建议： **1. 检查 LLM API 配置** 最常见的原因是 [API URL 格式不正确](https://github.com…
- #146 [open, mirror=#88] [Feature Request] Add Husky for Git Hook Automated Checks (enhancement)
  - local coverage [covered]: The repo now ships an opt-in, repo-native git hook workflow: `.githooks/pre-commit` runs the shared fast validation bundle, `.githooks/pre-push` runs the full validation bundle, and `npm run hooks:install` enables them without introducing a mandatory Husky/Node-only hook dependency.
  - Background The current project lacks automated validation before code commits, which may lead to the following issues: 1. Committing non-compliant code (e.g., syntax errors, messy formatting); 2. Inconsistent commit messages, which is not conducive to subsequent maintenance and version tracking; 3. Inefficiency in team collaboration due to the need for manual reminders of specifications. Solution…
- #145 [open, mirror=#2] 知识图谱中存在重复实体节点 (no labels)
  - local coverage [partial]: Repo-native partial mitigations are now landed locally for both simulation inputs and the Process graph view: `ZepEntityReader.filter_defined_entities()` collapses obvious same-entity alias variants before simulation/profile generation, and `frontend/src/views/processGraphData.js` now collapses the same conservative alias pairs while rendering the graph so title-prefixed duplicates such as `美国总统特朗普` vs `特朗普` no longer show as separate nodes in the main visualization. Full graph-level deduplication still remains tracked under beads issue `mirofish-975` because upstream PR #141 is not safe to cherry-pick wholesale.
  - ## 问题描述 在使用 MiroFish 构建知识图谱时，Zep 会将同一现实实体识别为多个不同节点。 例如输入包含"特朗普"相关内容的文本后，图谱中会同时出现"特朗普"和 "美国总统特朗普"两个独立节点，它们各自有独立的边和关系。 这会导致： - 图谱中同一实体的信息被分散到多个节点上 - 后续的模拟推演基于不完整的实体关系进行，影响准确性 - 图谱可视化时出现冗余节点，影响可读性 ## 复现步骤 1. 准备一段包含同一人物/组织不同称呼的背景文本 2. 通过前端正常流程构建知识图谱 3. 查看生成的图谱，可以看到同一实体被拆分为多个节点 ## 截图 <img width="675" height="399" alt="Image" src="https://github.com/user-attachments/assets/593f4188-e766-46b3-9b88-25486…
- #142 [open, mirror=#3] 这个方向最后商业化落地应用的点是什么呢 (question)
  - local coverage [no_action]: Upstream issue #142 asks about long-term commercialization direction rather than reporting a reproducible bug or scoped feature request, so there is no local implementation task attached to it.
- #64 [open, mirror=#4] 一直卡在上传文件错误：Request failed with status code 500 (no labels)
  - local coverage [covered]: Upload and graph-build failures now surface structured per-file parser/config validation errors instead of collapsing common deployment or document-ingest problems into a generic 500.
  - <img width="1206" height="1234" alt="Image" src="https://github.com/user-attachments/assets/5befa186-6f0f-493a-a6fa-7fb33940f233" /> TXT、MD、PDF文件格式都试了，内容甚至精简到就几百字，但就是卡在上传文件错误，到底什么原因？
  - latest comment by `666ghj`: 以前的代码因为编码格式的缘故会报这样的错，最新代码已经修复了。 你是把他部署在服务器上吗，那好像会有一些问题。
- #140 [open, mirror=#5] 让我想到了刘慈欣的一个小说，要是把真实世界放进去，得多大的算力啊 (no labels)
  - local coverage [no_action]: Upstream issue #140 is general project commentary rather than an actionable defect report or scoped feature request, so it does not require local implementation work.
- #135 [open, mirror=#6] 报错，Zep图谱构建失败 (no labels)
  - local coverage [covered]: Graph ontology ingestion now accepts string-valued attribute definitions for entity and edge schemas, so malformed LLM ontology output no longer crashes graph builds with `TypeError: string indices must be integers`.
  - Graph build task failed: Traceback (most recent call last): File "/app/backend/app/api/graph.py", line 418, in build_task builder.set_ontology(graph_id, ontology) File "/app/backend/app/services/graph_builder.py", line 230, in set_ontology attr_name = safe_attr_name(attr_def["name"]) # 使用安全名称 ~~~~~~~~^^^^^^^^ TypeError: string indices must be integers, not 'str'
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @rheeh! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这个错误是因为 `attr_def` 应该是字典格式 `{"name": "attr_name", ...}`，但实际收到的是字符串。 **根本原因**：LLM 生成的 ontology 中，`attributes` 字段可能返回了简单的…
- #133 [open, mirror=#7] 本地部署，启动已经显示成功了，访问却失败 (question)
  - local coverage [covered]: The backend root path `/` plus `/health` and `/healthz` now return a small JSON status payload with the live API prefixes, so local or Docker users no longer need to infer backend health from a bare 404.
  - 前后端启动都显示成功了，0.0.0.0:5001无法访问，提示404。前端0.0.0.0:3000虽然可以访问，但是一到这个界面就会报错 <img width="2550" height="1233" alt="Image" src="https://github.com/user-attachments/assets/032cf0ac-78ae-406d-831d-da5b9a28d5a0" />，看了项目也没有报错日志，请问这是什么问题呢
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @Axing93! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这是一个常见的前后端连接配置问题。 **后端 5001 返回 404 是正常的** — [根路径 `/` 未定义端点](https://github.com/666ghj/MiroFish/issues/68)，实际 API 通过具体…
- #117 [open, mirror=#8] ### Feature Request: English Language Support (enhancement)
  - local coverage [covered]: The English support sweep now covers workflow chrome, deterministic Step 2/3 system-log copy, report/interview parsing, and Step 5 interview fallbacks: Step 3/5 labels flow through shared i18n dictionaries, Step 2 prepare-stage progress and Step 3 round/PID logs localize through shared helpers, Step 4 tool-output parsers accept both Chinese and English markers, and zep_tools now localizes deterministic interview-selection/question/summary fallback copy in English mode.
  - Hi, First of all, thank you for creating and open-sourcing this amazing project. MiroFish is a very interesting and powerful multi-agent prediction engine. Currently, a large portion of the documentation, UI text, and comments appear to be primarily in Chinese. This makes it difficult for international developers to fully understand and use the project. ### Request It would be very helpful if the…
- #110 [open, mirror=#9] 阿里云百炼 API 调用异常：付费计划（Coding Plan）非千文模型及大模型API中转站的API均失效，仅免费额度模型或coding plan的千文模型可用 (LLM API)
  - local coverage [covered]: The backend and docs now support direct OpenAI-compatible gateways plus OPENAI_* aliases, including a documented DashScope Coding Plan example, so users no longer need a provider-specific raw LLM setup path.
  - 阿里云百炼 API 调用异常：付费计划（Coding Plan）非千文模型及大模型API中转站的API均失效，仅免费额度模型或coding plan的千文模型可用
  - latest comment by `lukeliu95`: 使用以下方式调用Coding Plan LLM_BASE_URL=https://coding.dashscope.aliyuncs.com/v1 LLM_MODEL_NAME=qwen3.5-plus

## Recently Updated Pull Requests

- #147 [open, mergeable=clean, mirrored=yes] feat: Russian localization (Русская локализация) (`russian-localization` -> `main`)
  - local coverage [partial]: Safe subset landed locally: added a repo-native `README-RU.md` plus language cross-links, but the full branch is not safe to cherry-pick because it replaces large frontend/backend sections and drops current local tooling, tests, and upstream-triage assets.
  - ## 🇷🇺 Russian Localization This PR adds a complete Russian translation of MiroFish: ### Changes: - **15 Vue components** — all UI labels, buttons, placeholders, error messages, and tooltips translated from Chinese to Russian - **README-RU.md** — full Russian documentation with quick start guide - Translation files are in `frontend-ru/src/` (ready to merge into `frontend/src/` when approved) - LLM…
- #141 [open, mergeable=clean, mirrored=yes] feat: add entity deduplication after graph building (`feature/entity-deduplication` -> `main`)
  - local coverage [not_safe]: Not safe to cherry-pick: the entity-deduplication branch rewinds large portions of the current tree (tooling, tests, i18n, OpenAI-compatible docs/config) while adding a large graph mutation feature, so it needs a repo-native reimplementation with targeted regression coverage instead of a blind merge.
  - Hi @666ghj I noticed that during graph building, Zep sometimes creates duplicate entity nodes for the same real-world entity (e.g. "特朗普" and "美国总统特朗普" appear as separate nodes). This affects the accuracy of the knowledge graph. This PR adds an automatic entity deduplication step after graph building, using name similarity pre-filtering + type compatibility check + LLM confirmation to identify and…
- #144 [open, mergeable=clean, mirrored=yes] feat(kg): add dual-mode knowledge graph support (`feat/local-knowledge-graph` -> `main`)
  - local coverage [tracked]: Tracked under beads issue `mirofish-8eg`: the dual-mode local knowledge graph branch is directionally aligned with the non-Zep backend request, but it is not safe to cherry-pick wholesale because it adds a large new adapter plus dependency stack on top of an older tree without current graph/simulation regression coverage.
  - ## Summary - Add kg_adapter for dual-mode knowledge graph (cloud/local) - Support switching between Zep Cloud and local Graphiti + Neo4j - Improve entity extraction and report agent robustness - Add test_kg_adapter.py with unit tests ## Test plan - [ ] Test cloud mode with Zep Cloud - [ ] Test local mode with Graphiti + Neo4j - [ ] Run unit tests 🤖 Generated with [Claude Code](https://claude.com/…
- #143 [open, mergeable=clean, mirrored=yes] docs: fix README alt text URL encoding (`docs/urlEncoding` -> `main`)
  - local coverage [landed]: Landed locally as a repo-native docs cleanup: the Shanda logo alt text now uses the correct URL-encoded `666ghj%2FMiroFish` slug across all README variants, not just the primary Chinese README.
  - ## Summary Fix the Shanda image alt text in README.md by changing 666ghj%2MiroFish to 666ghj%2FMiroFish. ## Details 666ghj%2MiroFish is not a valid URL-encoded representation, so it cannot be decoded correctly. Using 666ghj%2FMiroFish correctly encodes the slash and can be properly decoded to 666ghj/ MiroFish. ## Impact Documentation-only change. No code or runtime behavior is affected.
- #105 [open, mergeable=clean, mirrored=yes] fix: security improvements and error handling fixes (`fix/security-improvements` -> `main`)
  - local coverage [landed]: Landed locally: backend security/config hardening now includes env-driven CORS controls with a localhost-only default allowlist, `DEBUG=False` by default, and generated fallback `SECRET_KEY` behavior.
  - ## 问题概述 这个PR修复了项目中发现的多个安全问题和代码质量问题。 ## 安全修复 1. **硬编码的SECRET_KEY** - `backend/app/config.py` - 之前：使用硬编码的`'mirofish-secret-key'`作为默认值 - 现在：如果未设置环境变量，会生成随机密钥并发出警告 2. **DEBUG模式默认为True** - `backend/app/config.py` - 之前：`DEBUG`默认为`True` - 现在：`DEBUG`默认为`False`，生产环境更安全 3. **CORS配置允许所有来源** - `backend/app/__init__.py` - 之前：`CORS(app, resources={r"/api/*": {"origins": "*"}})` - 现在：通过环境变量`CORS_ALLOWED_ORIGINS…
  - latest comment by `JasonOA888`: ## 代码审查反馈 优秀的PR！这些安全修复非常关键，特别是生产环境部署时。 ### 几个建议： 1. **SECRET_KEY随机生成** - 建议添加日志记录生成的key，方便调试但不要泄露到错误响应中 2. **CORS配置** - 考虑添加`CORS_ALLOW_METHODS`和`CORS_ALLOW_HEADERS`配置，提供更细粒度的控制 3. **error_handler.py** - 建议添加自定义异常类型，让API可以抛出特定错误而不是通用Except…
- #132 [open, mergeable=clean, mirrored=yes] docs:add simple system architecture part for README-EN.md & README.md (`docs/add-sys-architecture-part` -> `main`)
  - local coverage [landed]: Landed locally: README architecture overview.
  - ## PR Title docs(readme): simplify system architecture section to Layer Breakdown + Project Code Structure Tree only ## Summary This PR simplifies the **System Architecture** section in both Chinese and English README files by keeping only two high-signal sections: - **Layer Breakdown** - **Project Code Structure Tree** The previously added overall architecture diagram and related agent-intro blo…
- #131 [open, mergeable=clean, mirrored=yes] feat(graph_builder): add retry mechanism for Zep Cloud connection failures (`feat/zep-retry-mechanism` -> `main`)
  - local coverage [landed]: Safe subset landed locally: transient Zep failures now retry with bounded backoff.
  - ## Description Adds automatic retry mechanism to handle transient network errors when connecting to Zep Cloud API. This prevents graph build failures caused by temporary connection issues such as "Connection reset by peer" (errno 54). The retry logic uses exponential backoff (2s, 4s, 6s) and provides detailed progress feedback to users. ## Changes - Added retry logic (max 3 attempts) to `create_g…
- #130 [open, mergeable=clean, mirrored=yes] docs: 添加贡献指南文档 (`docs/add-pr-guide` -> `main`)
  - local coverage [landed]: Landed locally: `CONTRIBUTING.md`.
- #129 [open, mergeable=clean, mirrored=yes] fix(report_agent): handle API token overflow crash with context lengt… (`fix/fix-priority-issues-mNNjT` -> `main`)
  - local coverage [landed]: Safe subset landed locally for context-length retry, configurable `LLM_MAX_TOKENS`, and report-agent history pruning.
  - Add error handling in LLMClient for context_length_exceeded errors with automatic message trimming and retry (fixes https://github.com/666ghj/MiroFish/issues/52) Add configurable LLM_MAX_TOKENS env variable (default 4096) so users with different models can set appropriate limits Add message history pruning in report agent ReACT loop to prevent unbounded context growth that causes token overflow I…
- #126 [open, mergeable=clean, mirrored=yes] feat: Add custom exceptions and enhanced config validation (`feature/custom-exceptions-and-config-validation` -> `main`)
  - local coverage [landed]: Safe subset landed locally for structured config validation and non-sensitive config summaries.
  - ## Summary This PR improves the robustness of the MiroFish backend by implementing two key architectural improvements: ### 1. Custom Exception Hierarchy - Created a `MiroFishError` base class with error codes, severity levels, and HTTP status codes. - Added domain-specific exceptions for Configuration, Graphs, Simulations, and External APIs to replace generic Exception catches. ### 2. Enhanced Co…
