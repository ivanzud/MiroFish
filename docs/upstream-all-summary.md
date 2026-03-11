# Upstream Triage Snapshot

- Repository: `666ghj/MiroFish`
- State filter: `all`
- Captured: `2026-03-11T10:10:59.225029+00:00`
- Issues: `83` total (`open=36`, `closed=47`)
- Pull requests: `47` total (`open=33`, `closed=14`)
- Mirrored in `origin`: `34` of `47` PR refs

## Recently Updated Issues

- #138 [open] 生成的报告让人看不懂 (question)
  - 生成的报告感觉有点太偏题了，看不懂😭 ，比如我写了一个游戏的设计方案，预测这个游戏的受众群体将会是什么，给我的报告题目是《未来受众群体生态的静默与解体：一项基于模拟的预测报告》
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @huamingjie0815! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 感谢反馈！这个问题我找到原因了 😊 **根本原因**：报告标题生成的 [Prompt 模板](https://github.com/666ghj/MiroFish/blob/985f89f49acbb44ee14d9d6…
- #135 [open] 报错，Zep图谱构建失败 (no labels)
  - Graph build task failed: Traceback (most recent call last): File "/app/backend/app/api/graph.py", line 418, in build_task builder.set_ontology(graph_id, ontology) File "/app/backend/app/services/graph_builder.py", line 230, in set_ontology attr_name = safe_attr_name(attr_def["name"]) # 使用安全名称 ~~~~~~~~^^^^^^^^ TypeError: string indices must be integers, not 'str'
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @rheeh! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这个错误是因为 `attr_def` 应该是字典格式 `{"name": "attr_name", ...}`，但实际收到的是字符串。 **根本原因**：LLM 生成的 ontology 中，`attributes` 字段可能返回了简单的…
- #134 [open] 别再交“学费”了，一步到位才是最省钱的 (no labels)
  - 你以为用复杂的脚本搭个 VPS 就能掌控一切？现实是，面对公网晚高峰 20% 的丢包率和无差别的 TCP 阻断，你所有的伪装协议都不堪一击。一旦 IP 被墙，寻找新机器、重置环境的成本远超买一个现成服务。 WgetCloud 是“折腾党”的最终归宿。我们通过全线 BGP 中转 + 双向 IEPL 专线，从物理层面上抹平了网络波动与封锁风险。把专业底层的运维交出去，别让修梯子占用了你写代码、做产品和思考商业模式的核心精力。 点击下方链接注册新用户即可享受全员无门槛8折优惠券： ### [WgetCloud官网链接：wgetcloud.org](https://invite.wgetcloud.ltd/auth/register?code=jll8) 以下为晚高峰测速： ![image](https://github.com/cadencando/SSSSRV2RayTrojanClash/…
- #133 [open] 本地部署，启动已经显示成功了，访问却失败 (question)
  - 前后端启动都显示成功了，0.0.0.0:5001无法访问，提示404。前端0.0.0.0:3000虽然可以访问，但是一到这个界面就会报错 <img width="2550" height="1233" alt="Image" src="https://github.com/user-attachments/assets/032cf0ac-78ae-406d-831d-da5b9a28d5a0" />，看了项目也没有报错日志，请问这是什么问题呢
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @Axing93! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这是一个常见的前后端连接配置问题。 **后端 5001 返回 404 是正常的** — [根路径 `/` 未定义端点](https://github.com/666ghj/MiroFish/issues/68)，实际 API 通过具体…
- #121 [closed] 卡在了Exception in handleNewProject: Network Error (question)
  - <img width="859" height="151" alt="Image" src="https://github.com/user-attachments/assets/1a41f8a5-2cff-40a3-837b-f4955cc7b9b7" />
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @jackytianjp! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这个 "Network Error" 发生在 [`handleNewProject`](https://github.com/666ghj/MiroFish/blob/985f89f49acbb44ee14d9d680682c…
- #123 [closed] プリセット業界知識RAGの導入（方式3: ローカルファイル注入） (no labels)
  - ## 概要 シミュレーションのエージェント生成時に、キュレーション済みの業界知識・ドメイン知識をLLMプロンプトに注入する仕組みを構築する。 ## 背景 - 現状、Topプレイヤー生成・転職先企業推定・キャリア評価はすべてLLMの内部知識のみに依存 - Web検索APIの導入はプロンプトインジェクションリスクがある - Zepグラフに業界知識を入れるとグラフ可視化が汚れる ## 方針（方式3: ローカルファイル注入） - キュレーション済みMarkdownファイルとして業界知識を保持 - 候補者の職種・業界をLLM判定した時点で、該当ファイルのみを読み込みプロンプトに注入 - Zepグラフは候補者データ専用のまま維持 ## ファイル構成案 ``` preset_knowledge/ ├── industries/ │ ├── it_software.md │ ├── consulting…
- #117 [open] ### Feature Request: English Language Support (enhancement)
  - Hi, First of all, thank you for creating and open-sourcing this amazing project. MiroFish is a very interesting and powerful multi-agent prediction engine. Currently, a large portion of the documentation, UI text, and comments appear to be primarily in Chinese. This makes it difficult for international developers to fully understand and use the project. ### Request It would be very helpful if the…
- #110 [open] 阿里云百炼 API 调用异常：付费计划（Coding Plan）非千文模型及大模型API中转站的API均失效，仅免费额度模型或coding plan的千文模型可用 (LLM API)
  - 阿里云百炼 API 调用异常：付费计划（Coding Plan）非千文模型及大模型API中转站的API均失效，仅免费额度模型或coding plan的千文模型可用
  - latest comment by `lukeliu95`: 使用以下方式调用Coding Plan LLM_BASE_URL=https://coding.dashscope.aliyuncs.com/v1 LLM_MODEL_NAME=qwen3.5-plus
- #64 [open] 一直卡在上传文件错误：Request failed with status code 500 (no labels)
  - <img width="1206" height="1234" alt="Image" src="https://github.com/user-attachments/assets/5befa186-6f0f-493a-a6fa-7fb33940f233" /> TXT、MD、PDF文件格式都试了，内容甚至精简到就几百字，但就是卡在上传文件错误，到底什么原因？
  - latest comment by `666ghj`: 以前的代码因为编码格式的缘故会报这样的错，最新代码已经修复了。 你是把他部署在服务器上吗，那好像会有一些问题。
- #106 [open] 能否采用除了zep的别的知识图谱 (no labels)
  - 如题所示，今天在跑的时候发现zep的免费额度被耗光了，能否添加使用本地部署的memv作为知识图谱
  - latest comment by `addisjeams`: 对，一开始半天都是网络报错，后来才发现是这个问题。必须要申请zep

## Recently Updated Pull Requests

- #127 [closed, mergeable=clean, mirrored=yes] Fix potential crash in LLMClient when content is None (`fix/llm-client-none-content` -> `main`)
  - Added `if content is None: return ""` in `backend/app/utils/llm_client.py` to prevent `re.sub` TypeError. --- *Automated PR created by OpenClaw daily-pr routine.*
  - latest comment by `sjhddh`: Closing this PR as it was submitted with an incorrect Git author configuration. Apologies for the noise!
- #120 [closed, mergeable=clean, mirrored=no] fix: 修复subsystems目录下neo4j_client导入路径错误; feat: 添加TODO.md开发规划文档 (`main` -> `main`)
  - 新增neo4j 板块
- #105 [open, mergeable=clean, mirrored=yes] fix: security improvements and error handling fixes (`fix/security-improvements` -> `main`)
  - ## 问题概述 这个PR修复了项目中发现的多个安全问题和代码质量问题。 ## 安全修复 1. **硬编码的SECRET_KEY** - `backend/app/config.py` - 之前：使用硬编码的`'mirofish-secret-key'`作为默认值 - 现在：如果未设置环境变量，会生成随机密钥并发出警告 2. **DEBUG模式默认为True** - `backend/app/config.py` - 之前：`DEBUG`默认为`True` - 现在：`DEBUG`默认为`False`，生产环境更安全 3. **CORS配置允许所有来源** - `backend/app/__init__.py` - 之前：`CORS(app, resources={r"/api/*": {"origins": "*"}})` - 现在：通过环境变量`CORS_ALLOWED_ORIGINS…
  - latest comment by `JasonOA888`: ## 代码审查反馈 优秀的PR！这些安全修复非常关键，特别是生产环境部署时。 ### 几个建议： 1. **SECRET_KEY随机生成** - 建议添加日志记录生成的key，方便调试但不要泄露到错误响应中 2. **CORS配置** - 考虑添加`CORS_ALLOW_METHODS`和`CORS_ALLOW_HEADERS`配置，提供更细粒度的控制 3. **error_handler.py** - 建议添加自定义异常类型，让API可以抛出特定错误而不是通用Except…
- #132 [open, mergeable=clean, mirrored=yes] docs:add simple system architecture part for README-EN.md & README.md (`docs/add-sys-architecture-part` -> `main`)
  - ## PR Title docs(readme): simplify system architecture section to Layer Breakdown + Project Code Structure Tree only ## Summary This PR simplifies the **System Architecture** section in both Chinese and English README files by keeping only two high-signal sections: - **Layer Breakdown** - **Project Code Structure Tree** The previously added overall architecture diagram and related agent-intro blo…
- #131 [open, mergeable=clean, mirrored=yes] feat(graph_builder): add retry mechanism for Zep Cloud connection failures (`feat/zep-retry-mechanism` -> `main`)
  - ## Description Adds automatic retry mechanism to handle transient network errors when connecting to Zep Cloud API. This prevents graph build failures caused by temporary connection issues such as "Connection reset by peer" (errno 54). The retry logic uses exponential backoff (2s, 4s, 6s) and provides detailed progress feedback to users. ## Changes - Added retry logic (max 3 attempts) to `create_g…
- #130 [open, mergeable=clean, mirrored=yes] docs: 添加贡献指南文档 (`docs/add-pr-guide` -> `main`)
- #129 [open, mergeable=clean, mirrored=yes] fix(report_agent): handle API token overflow crash with context lengt… (`fix/fix-priority-issues-mNNjT` -> `main`)
  - Add error handling in LLMClient for context_length_exceeded errors with automatic message trimming and retry (fixes https://github.com/666ghj/MiroFish/issues/52) Add configurable LLM_MAX_TOKENS env variable (default 4096) so users with different models can set appropriate limits Add message history pruning in report agent ReACT loop to prevent unbounded context growth that causes token overflow I…
- #126 [open, mergeable=clean, mirrored=yes] feat: Add custom exceptions and enhanced config validation (`feature/custom-exceptions-and-config-validation` -> `main`)
  - ## Summary This PR improves the robustness of the MiroFish backend by implementing two key architectural improvements: ### 1. Custom Exception Hierarchy - Created a `MiroFishError` base class with error codes, severity levels, and HTTP status codes. - Added domain-specific exceptions for Configuration, Graphs, Simulations, and External APIs to replace generic Exception catches. ### 2. Enhanced Co…
- #125 [open, mergeable=clean, mirrored=yes] fix: improve new-project network error diagnostics (`fix/issue-121` -> `main`)
  - ## Summary Improve frontend error feedback when creating a new project so users can quickly diagnose "Network Error" and timeout failures instead of seeing a generic message. ## Changes - Added `formatProjectInitError` in `frontend/src/views/Process.vue` - Distinguish timeout errors and provide actionable hint (reduce file size / check model speed) - Distinguish network errors and show configured…
- #124 [open, mergeable=clean, mirrored=yes] fix: robust JSON extraction for mixed LLM responses (`fix/issue-64` -> `main`)
  - ## SummarynnHarden backend JSON parsing for LLM responses so mixed outputs (markdown fences, pre/post text) are handled more robustly, reducing 500 errors reported during ontology generation.nn## Changesnn- Updated `LLMClient.chat()` to remove `<think ...>...</think>` tags case-insensitivelyn- Added `LLMClient._extract_json_payload()` to normalize and extract JSON from noisy model responsesn- Upd…
