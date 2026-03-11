# Upstream Triage Snapshot

- Repository: `666ghj/MiroFish`
- State filter: `open`
- Captured: `2026-03-11T11:39:25.726371+00:00`
- Issues: `36` total (`open=36`, `closed=0`)
- Pull requests: `33` total (`open=33`, `closed=0`)
- Mirrored in `origin`: `33` of `33` PR refs

## Recently Updated Issues

- #140 [open] 让我想到了刘慈欣的一个小说，要是把真实世界放进去，得多大的算力啊 (no labels)
- #139 [open] Graph build task failed  ：（ (no labels)
  - Graph build task failed: Traceback (most recent call last): File "/app/backend/.venv/lib/python3.11/site-packages/zep_cloud/graph/raw_client.py", line 713, in create _response_json = _response.json() ^^^^^^^^^^^^^^^^ File "/app/backend/.venv/lib/python3.11/site-packages/httpx/_models.py", line 832, in json return jsonlib.loads(self.content, **kwargs) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File "/u…
  - latest comment by `dosubot[bot]`: <!-- Answer --> The `401 unauthorized` error indicates a Zep Cloud API authentication issue. Here are the most likely causes and solutions: **1. Version Bug** — If you're using MiroFish v0.1.0, there's a [known authentication bug](https://…
- #135 [open] 报错，Zep图谱构建失败 (no labels)
  - Graph build task failed: Traceback (most recent call last): File "/app/backend/app/api/graph.py", line 418, in build_task builder.set_ontology(graph_id, ontology) File "/app/backend/app/services/graph_builder.py", line 230, in set_ontology attr_name = safe_attr_name(attr_def["name"]) # 使用安全名称 ~~~~~~~~^^^^^^^^ TypeError: string indices must be integers, not 'str'
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @rheeh! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这个错误是因为 `attr_def` 应该是字典格式 `{"name": "attr_name", ...}`，但实际收到的是字符串。 **根本原因**：LLM 生成的 ontology 中，`attributes` 字段可能返回了简单的…
- #133 [open] 本地部署，启动已经显示成功了，访问却失败 (question)
  - 前后端启动都显示成功了，0.0.0.0:5001无法访问，提示404。前端0.0.0.0:3000虽然可以访问，但是一到这个界面就会报错 <img width="2550" height="1233" alt="Image" src="https://github.com/user-attachments/assets/032cf0ac-78ae-406d-831d-da5b9a28d5a0" />，看了项目也没有报错日志，请问这是什么问题呢
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @Axing93! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 这是一个常见的前后端连接配置问题。 **后端 5001 返回 404 是正常的** — [根路径 `/` 未定义端点](https://github.com/666ghj/MiroFish/issues/68)，实际 API 通过具体…
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
- #42 [open] 项目在3/5开始模拟时会消耗大量内存 (no labels)
  - 作为可能会用到的信息，我上传了大约有260000字符的《白夜行》前十二章。推测原因是simulation.py的接口会把所有动作读全量并返回，这些动作会随着模拟变大而线性膨胀，从而导致巨量内存消耗。 <img width="988" height="666" alt="Image" src="https://github.com/user-attachments/assets/3fce3699-5e8d-4a8c-a33f-5290b236a2f0" />
  - latest comment by `666ghj`: 我后续会进行算法层面的优化
- #84 [open] 报告生成失败，请问有没有办法重新生成？ (question)
  - <img width="2538" height="1213" alt="Image" src="https://github.com/user-attachments/assets/e3d01822-aa09-45b7-9210-2ce8e23bca8f" /> 好像是Zep超出调用限额导致报告生成失败，但是即使我充值了Zep，似乎也没有办法重新生成报告，难道只能重新走一轮？
  - latest comment by `dosubot[bot]`: <!-- Greeting --> Hi @luchenwei9266! I'm [Dosu](https://go.dosu.dev/dosubot) and I’m helping the MiroFish team. <!-- Answer --> 目前 MiroFish **不支持通过界面重试报告生成**，这是一个[已知问题](https://github.com/666ghj/MiroFish/issues/30)。系统虽然有 `force_regenerate`…

## Recently Updated Pull Requests

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
- #122 [open, mergeable=clean, mirrored=yes] fix(llm_client): remove response_format json_object for local LLM compatibility (`fix/lm-studio-json-object-compat` -> `main`)
  - ## Problem `chat_json()` uses `response_format={"type": "json_object"}`, but LM Studio and Ollama do not support this parameter (only `json_schema` or `text`), causing API calls to fail when using local LLMs. Related references: - LM Studio: https://github.com/lmstudio-ai/lmstudio-bug-tracker/issues/534 - Similar to issue #110 (API call failures) ## Solution Remove `response_format` from `chat_js…
- #119 [open, mergeable=clean, mirrored=yes] feat: add an option to switch to english language (`language-option` -> `main`)
  - Right now the content of the website is mostly in Chinese , Added an button to switch between Chinese and english language . [`Demo Video`](https://drive.google.com/file/d/15VYI0J1SoDRf27Zvprm1P-D4MO8hA7yE/view?usp=sharing)
  - latest comment by `Pratiyankkumar`: <img width="1470" height="835" alt="Screenshot 2026-03-10 at 11 42 33 PM" src="https://github.com/user-attachments/assets/1483f8c1-da70-4d76-8058-6a5752204564" /> **PR summary (last two prompts):** 1. **Error message i18n** – Added `errors…
