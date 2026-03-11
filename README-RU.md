<div align="center">

<img src="./static/image/MiroFish_logo_compressed.jpeg" alt="MiroFish Logo" width="75%"/>

<a href="https://trendshift.io/repositories/16144" target="_blank"><img src="https://trendshift.io/api/badge/repositories/16144" alt="666ghj%2FMiroFish | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

Простой и универсальный движок коллективного интеллекта для прогнозирования чего угодно
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

## Overview

**MiroFish** is a multi-agent prediction engine that builds a high-fidelity digital world from seed materials such as news, policy drafts, research, or long-form narratives. Inside that world, many agents with memory and behavioral rules interact, evolve, and produce a simulation that can be inspected through reports and direct chat.

This Russian README is a safe repo-native documentation subset extracted from upstream PR `#147`. It documents the current branch without importing that PR's large frontend/backend rewrite.

## What You Need

- Node.js `18+`
- Python `3.11+`
- `uv`
- A Zep API key
- An OpenAI-compatible LLM endpoint

## Quick Start

```bash
cp .env.example .env
npm run setup:all
npm run dev
```

Services:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

## OpenAI-Compatible Backends

MiroFish can use any backend that speaks the OpenAI-compatible chat/completions API. You can configure it with either the repo-native `LLM_*` variables or the alias `OPENAI_*` variables.

Example:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1

ZEP_API_KEY=your_zep_key
```

Equivalent `LLM_*` form:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4.1
```

This also works with OpenAI-compatible gateways such as DashScope, LM Studio, Ollama, or self-hosted proxies if they expose the same API surface.

## Workflow

1. Build the graph from source material.
2. Generate environment/persona configuration.
3. Run the simulation.
4. Generate the report.
5. Interact with the simulated world.

## Full Documentation

- English guide: [README-EN.md](./README-EN.md)
- Chinese guide: [README.md](./README.md)
- Environment template: [`.env.example`](./.env.example)
- Contribution guide: [CONTRIBUTING.md](./CONTRIBUTING.md)

## Notes

- The current product UI is still primarily Chinese/English on this branch.
- Upstream PR `#147` contains a much larger Russian localization attempt, but that branch is not safe to cherry-pick wholesale because it replaces large parts of the repo and removes current local validation/tooling work.
