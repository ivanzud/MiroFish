# Upstream Triage Snapshot

- Repository: `666ghj/MiroFish`
- State filter: `all`
- Captured: `2026-03-11T15:39:38.999394+00:00`
- Issues: `87` total (`open=38`, `closed=49`)
- Pull requests: `50` total (`open=36`, `closed=14`)
- Mirrored in `origin`: `50` of `50` PR refs
- Mirrored in `ivanzud/MiroFish`: `87` of `87` issues
- Local issue coverage map: `docs/upstream-coverage.json`

## Recently Updated Issues

- #146 [open, mirror=#88] [Feature Request] Add Husky for Git Hook Automated Checks (enhancement)
  - local coverage [covered]: The repo now ships an opt-in, repo-native git hook workflow: `.githooks/pre-commit` runs the shared fast validation bundle, `.githooks/pre-push` runs the full validation bundle, and `npm run hooks:install` enables them without introducing a mandatory Husky/Node-only hook dependency.
  - Background The current project lacks automated validation before code commits, which may lead to the following issues: 1. Committing non-compliant code (e.g., syntax errors, messy formatting); 2. Inconsistent commit messages, which is not conducive to subsequent maintenance and version tracking; 3. Inefficiency in team collaboration due to the need for manual reminders of specifications. Solution…
- #145 [open, mirror=#2] 知识图谱中存在重复实体节点 (no labels)
  - local coverage [tracked]: Tracked under beads issue `mirofish-975`: upstream issue #145 confirms the duplicate-entity-node problem behind PR #141, but the only related upstream implementation is still not safe to cherry-pick wholesale on top of the current branch.
  - ## 问题描述 在使用 MiroFish 构建知识图谱时，Zep 会将同一现实实体识别为多个不同节点。 例如输入包含"特朗普"相关内容的文本后，图谱中会同时出现"特朗普"和 "美国总统特朗普"两个独立节点，它们各自有独立的边和关系。 这会导致： - 图谱中同一实体的信息被分散到多个节点上 - 后续的模拟推演基于不完整的实体关系进行，影响准确性 - 图谱可视化时出现冗余节点，影响可读性 ## 复现步骤 1. 准备一段包含同一人物/组织不同称呼的背景文本 2. 通过前端正常流程构建知识图谱 3. 查看生成的图谱，可以看到同一实体被拆分为多个节点 ## 截图 <img width="675" height="399" alt="Image" src="https://github.com/user-attachments/assets/593f4188-e766-46b3-9b88-25486…
- #142 [open, mirror=#3] 这个方向最后商业化落地应用的点是什么呢 (question)
  - local coverage [no_action]: Upstream issue #142 asks about long-term commercialization direction rather than reporting a reproducible bug or scoped feature request, so there is no local implementation task attached to it.
- #64 [open, mirror=#4] 一直卡在上传文件错误：Request failed with status code 500 (no labels)
  - local coverage [covered]: Upload and graph-build failures now surface structured per-file parser/config validation errors instead of collapsing common deployment or document-ingest problems into a generic 500.
  - <img width="1206" height="1234" alt="Image" src="https://github.com/user-attachments/assets/5befa186-6f0f-493a-a6fa-7fb33940f233" /> TXT、MD、PDF文件格式都试了，内容甚至精简到就几百字，但就是卡在上传文件错误，到底什么原因？
  - latest comment by `666ghj`: 以前的代码因为编码格式的缘故会报这样的错，最新代码已经修复了。 你是把他部署在服务器上吗，那好像会有一些问题。
- #139 [closed, mirror=#39] Graph build task failed  ：（ (no labels)
  - local coverage [covered]: Graph-build task failures now classify Zep 401/unauthorized responses into a concise ZEP_API_KEY guidance message and strip embedded traceback noise before returning task payload errors.
  - Graph build task failed: Traceback (most recent call last): File "/app/backend/.venv/lib/python3.11/site-packages/zep_cloud/graph/raw_client.py", line 713, in create _response_json = _response.json() ^^^^^^^^^^^^^^^^ File "/app/backend/.venv/lib/python3.11/site-packages/httpx/_models.py", line 832, in json return jsonlib.loads(self.content, **kwargs) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/u…
  - latest comment by `dosubot[bot]`: <!-- Answer --> The `401 unauthorized` error indicates a Zep Cloud API authentication issue. Here are the most likely causes and solutions: **1. Version Bug** — If you're using MiroFish v0.1.0, there's a [known authentication bug](https://…
- #140 [open, mirror=#5] 让我想到了刘慈欣的一个小说，要是把真实世界放进去，得多大的算力啊 (no labels)
  - local coverage [no_action]: Upstream issue #140 is general project commentary rather than an actionable defect report or scoped feature request, so it does not require local implementation work.
- #138 [closed, mirror=#40] 生成的报告让人看不懂 (question)
  - 生成的报告感觉有点太偏题了，看不懂😭 ，比如我写了一个游戏的设计方案，预测这个游戏的受众群体将会是什么，给我的报告题目是《未来受众群体生态的静默与解体：一项基于模拟的预测报告》
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @huamingjie0815! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 感谢反馈！这个问题我找到原因了 😊 **根本原因**：报告标题生成的 [Prompt 模板](https://github.com/666ghj/MiroFish/blob/985f89f49acbb44ee14d9d6…
- #135 [open, mirror=#6] 报错，Zep图谱构建失败 (no labels)
  - local coverage [covered]: Graph ontology ingestion now accepts string-valued attribute definitions for entity and edge schemas, so malformed LLM ontology output no longer crashes graph builds with `TypeError: string indices must be integers`.
  - Graph build task failed: Traceback (most recent call last): File "/app/backend/app/api/graph.py", line 418, in build_task builder.set_ontology(graph_id, ontology) File "/app/backend/app/services/graph_builder.py", line 230, in set_ontology attr_name = safe_attr_name(attr_def["name"]) # 使用安全名称 ~~~~~~~~^^^^^^^^ TypeError: string indices must be integers, not 'str'
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @rheeh! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这个错误是因为 `attr_def` 应该是字典格式 `{"name": "attr_name", ...}`，但实际收到的是字符串。 **根本原因**：LLM 生成的 ontology 中，`attributes` 字段可能返回了简单的…
- #133 [open, mirror=#7] 本地部署，启动已经显示成功了，访问却失败 (question)
  - local coverage [covered]: The backend root path `/` plus `/health` and `/healthz` now return a small JSON status payload with the live API prefixes, so local or Docker users no longer need to infer backend health from a bare 404.
  - 前后端启动都显示成功了，0.0.0.0:5001无法访问，提示404。前端0.0.0.0:3000虽然可以访问，但是一到这个界面就会报错 <img width="2550" height="1233" alt="Image" src="https://github.com/user-attachments/assets/032cf0ac-78ae-406d-831d-da5b9a28d5a0" />，看了项目也没有报错日志，请问这是什么问题呢
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @Axing93! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这是一个常见的前后端连接配置问题。 **后端 5001 返回 404 是正常的** — [根路径 `/` 未定义端点](https://github.com/666ghj/MiroFish/issues/68)，实际 API 通过具体…
- #121 [closed, mirror=#41] 卡在了Exception in handleNewProject: Network Error (question)
  - <img width="859" height="151" alt="Image" src="https://github.com/user-attachments/assets/1a41f8a5-2cff-40a3-837b-f4955cc7b9b7" />
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @jackytianjp! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这个 "Network Error" 发生在 [`handleNewProject`](https://github.com/666ghj/MiroFish/blob/985f89f49acbb44ee14d9d680682c…

## Recently Updated Pull Requests

- #141 [open, mergeable=clean, mirrored=yes] feat: add entity deduplication after graph building (`feature/entity-deduplication` -> `main`)
  - local coverage [not_safe]: Not safe to cherry-pick: the entity-deduplication branch rewinds large portions of the current tree (tooling, tests, i18n, OpenAI-compatible docs/config) while adding a large graph mutation feature, so it needs a repo-native reimplementation with targeted regression coverage instead of a blind merge.
  - Hi @666ghj I noticed that during graph building, Zep sometimes creates duplicate entity nodes for the same real-world entity (e.g. "特朗普" and "美国总统特朗普" appear as separate nodes). This affects the accuracy of the knowledge graph. This PR adds an automatic entity deduplication step after graph building, using name similarity pre-filtering + type compatibility check + LLM confirmation to identify and…
- #144 [open, mergeable=clean, mirrored=yes] feat(kg): add dual-mode knowledge graph support (`feat/local-knowledge-graph` -> `main`)
  - local coverage [tracked]: Tracked under beads issue `mirofish-8eg`: the dual-mode local knowledge graph branch is directionally aligned with the non-Zep backend request, but it is not safe to cherry-pick wholesale because it adds a large new adapter plus dependency stack on top of an older tree without current graph/simulation regression coverage.
  - ## Summary - Add kg_adapter for dual-mode knowledge graph (cloud/local) - Support switching between Zep Cloud and local Graphiti + Neo4j - Improve entity extraction and report agent robustness - Add test_kg_adapter.py with unit tests ## Test plan - [ ] Test cloud mode with Zep Cloud - [ ] Test local mode with Graphiti + Neo4j - [ ] Run unit tests 🤖 Generated with [Claude Code](https://claude.com/…
- #143 [open, mergeable=clean, mirrored=yes] docs: fix README alt text URL encoding (`docs/urlEncoding` -> `main`)
  - local coverage [landed]: Landed locally as a repo-native docs cleanup: the Shanda logo alt text now uses the correct URL-encoded `666ghj%2FMiroFish` slug across all README variants, not just the primary Chinese README.
  - ## Summary Fix the Shanda image alt text in README.md by changing 666ghj%2MiroFish to 666ghj%2FMiroFish. ## Details 666ghj%2MiroFish is not a valid URL-encoded representation, so it cannot be decoded correctly. Using 666ghj%2FMiroFish correctly encodes the slash and can be properly decoded to 666ghj/ MiroFish. ## Impact Documentation-only change. No code or runtime behavior is affected.
- #127 [closed, mergeable=clean, mirrored=yes] Fix potential crash in LLMClient when content is None (`fix/llm-client-none-content` -> `main`)
  - Added `if content is None: return ""` in `backend/app/utils/llm_client.py` to prevent `re.sub` TypeError. --- *Automated PR created by OpenClaw daily-pr routine.*
  - latest comment by `sjhddh`: Closing this PR as it was submitted with an incorrect Git author configuration. Apologies for the noise!
- #120 [closed, mergeable=clean, mirrored=yes] fix: 修复subsystems目录下neo4j_client导入路径错误; feat: 添加TODO.md开发规划文档 (`main` -> `main`)
  - 新增neo4j 板块
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
