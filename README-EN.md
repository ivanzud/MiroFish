<div align="center">

<img src="./static/image/MiroFish_logo_compressed.jpeg" alt="MiroFish Logo" width="75%"/>

<a href="https://trendshift.io/repositories/16144" target="_blank"><img src="https://trendshift.io/api/badge/repositories/16144" alt="666ghj%2FMiroFish | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

简洁通用的群体智能引擎，预测万物
</br>
<em>A Simple and Universal Swarm Intelligence Engine, Predicting Anything</em>

<a href="https://www.shanda.com/" target="_blank"><img src="./static/image/shanda_logo.png" alt="666ghj%2FMiroFish | Shanda" height="40"/></a>

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/MiroFish?style=flat-square&color=DAA520)](https://github.com/666ghj/MiroFish/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/network)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/666ghj/MiroFish)

[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white)](https://discord.com/channels/1469200078932545606/1469201282077163739)
[![X](https://img.shields.io/badge/X-Follow-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/mirofish_ai)
[![Instagram](https://img.shields.io/badge/Instagram-Follow-E4405F?style=flat-square&logo=instagram&logoColor=white)](https://www.instagram.com/mirofish_ai/)

[English](./README-EN.md) | [中文文档](./README.md) | [한국어](./README-KO.md) | [日本語](./README-JA.md) | [Русский](./README-RU.md)

</div>

## ⚡ Overview

**MiroFish** is a next-generation AI prediction engine powered by multi-agent technology. By extracting seed information from the real world (such as breaking news, policy drafts, or financial signals), it automatically constructs a high-fidelity parallel digital world. Within this space, thousands of intelligent agents with independent personalities, long-term memory, and behavioral logic freely interact and undergo social evolution. You can inject variables dynamically from a "God's-eye view" to precisely deduce future trajectories — **rehearse the future in a digital sandbox, and win decisions after countless simulations**.

> You only need to: Upload seed materials (data analysis reports or interesting novel stories) and describe your prediction requirements in natural language</br>
> MiroFish will return: A detailed prediction report and a deeply interactive high-fidelity digital world

### Our Vision

MiroFish is dedicated to creating a swarm intelligence mirror that maps reality. By capturing the collective emergence triggered by individual interactions, we break through the limitations of traditional prediction:

- **At the Macro Level**: We are a rehearsal laboratory for decision-makers, allowing policies and public relations to be tested at zero risk
- **At the Micro Level**: We are a creative sandbox for individual users — whether deducing novel endings or exploring imaginative scenarios, everything can be fun, playful, and accessible

From serious predictions to playful simulations, we let every "what if" see its outcome, making it possible to predict anything.

## 🌐 Live Demo

Welcome to visit our online demo environment and experience a prediction simulation on trending public opinion events we've prepared for you: [mirofish-live-demo](https://666ghj.github.io/mirofish-demo/)

## 📸 Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/运行截图1.png" alt="Screenshot 1" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图2.png" alt="Screenshot 2" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图3.png" alt="Screenshot 3" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图4.png" alt="Screenshot 4" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/运行截图5.png" alt="Screenshot 5" width="100%"/></td>
<td><img src="./static/image/Screenshot/运行截图6.png" alt="Screenshot 6" width="100%"/></td>
</tr>
</table>
</div>

## 🎬 Demo Videos

### 1. Wuhan University Public Opinion Simulation + MiroFish Project Introduction

<div align="center">
<a href="https://www.bilibili.com/video/BV1VYBsBHEMY/" target="_blank"><img src="./static/image/武大模拟演示封面.png" alt="MiroFish Demo Video" width="75%"/></a>

Click the image to watch the complete demo video for prediction using BettaFish-generated "Wuhan University Public Opinion Report"
</div>

### 2. Dream of the Red Chamber Lost Ending Simulation

<div align="center">
<a href="https://www.bilibili.com/video/BV1cPk3BBExq" target="_blank"><img src="./static/image/红楼梦模拟推演封面.jpg" alt="MiroFish Demo Video" width="75%"/></a>

Click the image to watch MiroFish's deep prediction of the lost ending based on hundreds of thousands of words from the first 80 chapters of "Dream of the Red Chamber"
</div>

> **Financial Prediction**, **Political News Prediction** and more examples coming soon...

## 🔄 Workflow

1. **Graph Building**: Seed extraction & Individual/collective memory injection & GraphRAG construction
2. **Environment Setup**: Entity relationship extraction & Persona generation & Agent configuration injection
3. **Simulation**: Dual-platform parallel simulation & Auto-parse prediction requirements & Dynamic temporal memory updates
4. **Report Generation**: ReportAgent with rich toolset for deep interaction with post-simulation environment
5. **Deep Interaction**: Chat with any agent in the simulated world & Interact with ReportAgent

## 🏗️ System Architecture

### Layer Breakdown

| Layer | Core Modules | Responsibilities |
|------|--------------|------------------|
| Presentation | `frontend/src/views/*`, `frontend/src/components/*` | 5-step workflow UI, live simulation status, report and interaction pages |
| API | `backend/app/api/graph.py`, `simulation.py`, `report.py` | Public APIs for graph build, simulation control, report generation and download |
| Orchestration | `simulation_manager.py`, `simulation_runner.py` | Simulation state machine, process lifecycle, pause/resume/stop, live status aggregation |
| Memory & Graph | `graph_builder.py`, `zep_entity_reader.py`, `zep_graph_memory_updater.py` | Seed structuring, graph writing, entity filtering, and post-simulation memory writeback |
| Reasoning & Report | `report_agent.py`, `zep_tools.py`, `utils/llm_client.py` | ReACT multi-step reasoning, tool calls, and interactive prediction report generation |

### Project Code Structure Tree

```text
MiroFish/
├── frontend/                                  # Vue3 frontend project
│   ├── package.json                           # frontend dependencies and scripts
│   ├── vite.config.js                         # Vite build/dev server config
│   ├── index.html                             # frontend HTML entry
│   └── src/
│       ├── main.js                            # Vue app bootstrap
│       ├── App.vue                            # root component
│       ├── api/                               # backend API wrappers
│       │   ├── index.js                       # Axios instance and shared request config
│       │   ├── graph.js                       # graph build related APIs
│       │   ├── simulation.js                  # simulation control APIs
│       │   └── report.js                      # report generation/download/chat APIs
│       ├── router/
│       │   └── index.js                       # frontend routes
│       ├── store/
│       │   └── pendingUpload.js               # pending upload state store
│       ├── views/                             # page-level views
│       │   ├── Home.vue                       # home page
│       │   ├── MainView.vue                   # main workflow container
│       │   ├── Process.vue                    # 5-step process page
│       │   ├── SimulationView.vue             # simulation preparation page
│       │   ├── SimulationRunView.vue          # live simulation monitor page
│       │   ├── ReportView.vue                 # report viewer page
│       │   └── InteractionView.vue            # deep interaction page
│       ├── components/                        # business components
│       │   ├── Step1GraphBuild.vue            # Step1 graph build component
│       │   ├── Step2EnvSetup.vue              # Step2 environment setup component
│       │   ├── Step3Simulation.vue            # Step3 simulation component
│       │   ├── Step4Report.vue                # Step4 report component
│       │   ├── Step5Interaction.vue           # Step5 interaction component
│       │   ├── GraphPanel.vue                 # graph data panel
│       │   └── HistoryDatabase.vue            # historical memory/data panel
│       └── assets/logo/                       # frontend logo assets
│           ├── MiroFish_logo_left.jpeg
│           └── MiroFish_logo_compressed.jpeg
├── backend/                                   # Flask backend project
│   ├── run.py                                 # backend service entrypoint
│   ├── requirements.txt                       # Python dependency list
│   ├── pyproject.toml                         # Python project metadata/tooling
│   ├── uv.lock                                # uv-locked dependency versions
│   ├── app/
│   │   ├── __init__.py                        # Flask app factory and blueprint wiring
│   │   ├── config.py                          # backend config and env loading
│   │   ├── api/                               # API route layer
│   │   │   ├── __init__.py                    # Blueprint initialization
│   │   │   ├── graph.py                       # graph build and graph management endpoints
│   │   │   ├── simulation.py                  # entity read, simulation create/run/control endpoints
│   │   │   └── report.py                      # report generate/query/download/chat endpoints
│   │   ├── services/                          # core business services
│   │   │   ├── graph_builder.py               # GraphRAG graph build service
│   │   │   ├── ontology_generator.py          # ontology/entity type generation
│   │   │   ├── text_processor.py              # seed text cleaning/preprocessing
│   │   │   ├── zep_entity_reader.py           # Zep graph entity read/filter service
│   │   │   ├── oasis_profile_generator.py     # OASIS persona/profile generation
│   │   │   ├── simulation_config_generator.py # simulation config auto-generation
│   │   │   ├── simulation_manager.py          # simulation lifecycle state manager
│   │   │   ├── simulation_runner.py           # background simulation execution/monitoring
│   │   │   ├── simulation_ipc.py              # simulation process IPC protocol
│   │   │   ├── zep_graph_memory_updater.py    # write simulation actions back to graph memory
│   │   │   ├── zep_tools.py                   # ReportAgent tool integrations
│   │   │   └── report_agent.py                # ReACT report generation and Q&A service
│   │   ├── models/                            # state model layer
│   │   │   ├── __init__.py
│   │   │   ├── project.py                     # project state and metadata manager
│   │   │   └── task.py                        # async task state model
│   │   └── utils/                             # shared infrastructure utilities
│   │       ├── __init__.py
│   │       ├── llm_client.py                  # OpenAI-SDK-compatible LLM client
│   │       ├── file_parser.py                 # uploaded file parsing utilities
│   │       ├── logger.py                      # layered logging system
│   │       ├── retry.py                       # retry helpers/decorators
│   │       └── zep_paging.py                  # Zep paging helper
│   ├── scripts/                               # OASIS runtime scripts
│   │   ├── run_parallel_simulation.py         # Twitter + Reddit parallel simulation entry
│   │   ├── run_twitter_simulation.py          # Twitter simulation runner
│   │   ├── run_reddit_simulation.py           # Reddit simulation runner
│   │   ├── action_logger.py                   # agent action logging utility
│   │   └── test_profile_format.py             # profile format validation script
│   ├── uploads/                               # runtime data (projects/simulations/reports)
│   └── logs/                                  # backend runtime logs
├── static/
│   └── image/                                 # README images and demo assets
├── package.json                               # root-level scripts for frontend/backend
├── docker-compose.yml                         # Docker orchestration (frontend + backend)
├── Dockerfile                                 # Docker image build definition
├── .env.example                               # environment variable template
├── README.md                                  # Chinese documentation
├── README-EN.md                               # English documentation
└── LICENSE                                    # open-source license
```

## 🚀 Quick Start

### Option 1: Source Code Deployment (Recommended)

#### Prerequisites

| Tool | Version | Description | Check Installation |
|------|---------|-------------|-------------------|
| **Node.js** | 18+ | Frontend runtime, includes npm | `node -v` |
| **Python** | ≥3.11, ≤3.12 | Backend runtime | `python --version` |
| **uv** | Latest | Python package manager | `uv --version` |

#### 1. Configure Environment Variables

```bash
# Copy the example configuration file
cp .env.example .env

# Edit the .env file and fill in the required API keys
```

**Required Environment Variables:**

```env
# LLM API Configuration (supports OpenAI, Codex-compatible, and other OpenAI-SDK-compatible backends)
# Standard OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_API_BASE_URL / OPENAI_MODEL aliases also work
# Recommended: Alibaba Qwen-plus model via Bailian Platform: https://bailian.console.aliyun.com/
# High consumption, try simulations with fewer than 40 rounds first
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus
# Optional: reduce this for OpenAI-compatible backends with smaller context windows
# LLM_MAX_TOKENS=4096

# Zep Cloud Configuration
# Free monthly quota is sufficient for simple usage: https://app.getzep.com/
ZEP_API_KEY=your_zep_api_key
```

The backend now accepts both the project-specific `LLM_*` variables and the standard `OPENAI_*` aliases, so you can point MiroFish directly at OpenAI, Codex-compatible gateways, LM Studio, Ollama, or other OpenAI-compatible backends without extra code changes or a separate `LLM_PROVIDER` flag. If multiple base-URL aliases are set, MiroFish resolves them in `LLM_BASE_URL` > `OPENAI_BASE_URL` > `OPENAI_API_BASE_URL` order; when those values disagree, `/api/graph/config/status` and `backend/scripts/print_config_status.py` now warn explicitly about which value won.

Common compatible backend examples:

```env
# OpenAI / Codex-compatible gateway
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini

# Alibaba DashScope Coding Plan
OPENAI_API_KEY=your_dashscope_key
OPENAI_API_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
OPENAI_MODEL=qwen3.5-plus
```

Verify the OpenAI-compatible path explicitly:

- Visit `http://localhost:5001/health` to confirm the backend is up.
- Or run `npm run check:backend-config` to print the same non-sensitive config-status payload without starting the server.
- Then open `http://localhost:5001/api/graph/config/status`. The JSON payload should report `llm.backend_mode = openai_compatible`.
- `summary.llm.sources` tells you whether MiroFish resolved `LLM_*` or `OPENAI_*` variables and whether the active base URL came from `OPENAI_BASE_URL` or `OPENAI_API_BASE_URL`, which is the quickest way to confirm a Codex/OpenAI-compatible gateway is wired correctly without adding `LLM_PROVIDER`.
- A warning about `SECRET_KEY` being generated temporarily is expected in local verification shells when `SECRET_KEY` is unset; it does not mean the direct `OPENAI_*` wiring failed.

If `http://localhost:5001` returns `404`, that usually does not mean the backend failed to boot. The backend root is API-only; use `http://localhost:5001/health` for a health check instead.

If Step 5 deep interaction frequently times out for single-agent chat, batch surveys, or all-agent interviews, increase both the frontend request timeout `VITE_API_TIMEOUT` (milliseconds) and the backend Interview wait windows `INTERVIEW_AGENT_TIMEOUT_SECONDS`, `INTERVIEW_BATCH_TIMEOUT_SECONDS`, and `INTERVIEW_ALL_TIMEOUT_SECONDS` (seconds).

For a first run, prefer a PDF / Markdown / TXT source under roughly 10k words and keep the simulation around 30 rounds. That lets you verify graph build, environment setup, and backend health before spending more Zep quota or debugging multiple scaling variables at once.

#### 2. Install Dependencies

```bash
# Recommended core install for graph/report/OpenAI-compatible backend usage
npm run setup:core

# Backward-compatible alias for the same core install path
npm run setup:all

# Install the optional OASIS runtime only if you need Step 3 / Step 5 simulations
npm run setup:backend:simulation
```

Or install step by step:

```bash
# Install Node dependencies (root + frontend)
npm run setup

# Install core Python dependencies (backend, auto-creates virtual environment)
npm run setup:backend

# Equivalent combined core install shortcut
npm run setup:core

# Install the optional OASIS simulation runtime
npm run setup:backend:simulation
```

`setup:core` / `setup:all` installs only the root package, frontend, and core graph/report/OpenAI-compatible backend dependencies. The upstream `oasis` runtime code used by Step 3 / Step 5 is now vendored directly under `backend/oasis`, and the optional simulation install keeps only the explicit runtime dependencies, so the default path no longer pulls the high-risk `camel-oasis -> unstructured==0.13.7` chain.

Known limitation: `npm run setup:backend:simulation` now fails fast on Python 3.13+ when Rust is not installed, because the current `camel-ai -> tiktoken==0.7.0` chain still falls back to a source build there. The core backend path is unaffected; for actual Step 3 / Step 5 simulation runs, use Python 3.11/3.12 or install Rust before running that command.

#### 3. Start Services

```bash
# Start both frontend and backend (run from project root)
npm run dev
```

**Service URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

If you use the default dual-port layout, the frontend auto-targets backend port `5001` on the same host. The backend root is API-only; use `http://localhost:5001/health` for a quick health check.

#### 3.1 FAQ

**Which models / APIs are supported?**

- The backend accepts any OpenAI-compatible API; it is not locked to one provider.
- Paths already validated and documented in this repo include OpenAI, Codex-compatible gateways, Alibaba DashScope compatible mode, Alibaba DashScope Coding Plan, and local OpenAI-compatible gateways such as LM Studio or Ollama.
- You can configure either the project-specific `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL_NAME` variables or the standard `OPENAI_API_KEY` / `OPENAI_API_BASE_URL` / `OPENAI_MODEL` aliases directly.

**What happens if I refresh the browser or close the page?**

- Refreshing the browser or closing the tab does not directly stop graph-building, simulation, or report jobs that are already running on the backend.
- Persisted data remains under `backend/uploads/`, and the homepage history view can reopen Step 1 (Graph Build), Step 2 (Environment Setup), and Step 4 (Report).
- Step 3 and Step 5 still depend on a live OASIS runtime session. If the backend process, container, or simulation environment has already been shut down, those live runtime stages cannot be replayed seamlessly and must be prepared or started again.

**Start Individually:**

```bash
npm run backend   # Start backend only
npm run frontend  # Start frontend only
```

#### 4. Lightweight Backend Validation

If `uv sync` or `uv run pytest` is blocked by heavyweight builds such as `tiktoken` requiring a Rust toolchain, run the fast targeted backend suite instead:

```bash
npm run test:backend:lite
```

This path creates `.tmp-test-venv/` on demand and installs only the packages needed for the current low-risk regression tests (`test_llm_client.py` and `test_graph_builder.py`).

### Option 2: Docker Deployment

```bash
# 1. Configure environment variables (same as source deployment)
cp .env.example .env

# 2. Optional: override the container image if GHCR is slow or blocked
# MIROFISH_IMAGE=ghcr.nju.edu.cn/666ghj/mirofish:latest

# 3. Pull image and start
docker compose up -d
```

Reads `.env` from root directory by default, maps ports `3000 (frontend) / 5001 (backend)`

If you deploy frontend and backend on different hosts or ports, set `VITE_API_BASE_URL` for the frontend explicitly.
You can also open the `Backend API` panel in the home screen or the Step 1 / Step 2 workbench header and persist a runtime backend URL in the browser without rebuilding the frontend.

For backend-side cross-origin control, you can also set `CORS_ALLOWED_ORIGINS` (comma-separated) plus optional `CORS_ALLOW_METHODS` / `CORS_ALLOW_HEADERS`. The default remains permissive (`*`) for backward compatibility, so these variables are only needed when you want to restrict which frontend origins may call `/api/*`.

`docker-compose.yml` now reads `MIROFISH_IMAGE`, so you can switch to a registry mirror or a private fork image through `.env` or a one-shot shell override instead of editing the compose file.

```bash
MIROFISH_IMAGE=ghcr.nju.edu.cn/666ghj/mirofish:latest docker compose up -d
```

## 📬 Join the Conversation

<div align="center">
<img src="./static/image/QQ群.png" alt="QQ Group" width="60%"/>
</div>

&nbsp;

The MiroFish team is recruiting full-time/internship positions. If you're interested in multi-agent simulation and LLM applications, feel free to send your resume to: **mirofish@shanda.com**

## 📄 Acknowledgments

**MiroFish has received strategic support and incubation from Shanda Group!**

MiroFish's simulation engine is powered by **[OASIS (Open Agent Social Interaction Simulations)](https://github.com/camel-ai/oasis)**, We sincerely thank the CAMEL-AI team for their open-source contributions!

## 📈 Project Statistics

<a href="https://www.star-history.com/#666ghj/MiroFish&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
 </picture>
</a>
