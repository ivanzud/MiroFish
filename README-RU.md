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

## Обзор

**MiroFish** — это мультиагентный движок прогнозирования, который строит высокодетализированный цифровой мир из исходных материалов: новостей, проектов политик, исследований или длинных текстов. Внутри этого мира множество агентов с памятью и поведенческими правилами взаимодействуют, развиваются и создают симуляцию, которую затем можно изучать через отчёты и прямой чат.

Этот `README` на русском языке — безопасный репо-нативный поднабор документации, выделенный из upstream PR `#147`. Он описывает текущее состояние этой ветки без переноса крупной переработки фронтенда и бэкенда из того PR.

## Что потребуется

- Node.js `18+`
- Python `3.11+`
- `uv`
- API-ключ Zep
- OpenAI-compatible LLM endpoint

## Быстрый старт

```bash
cp .env.example .env
npm run setup:core
npm run dev
```

`npm run setup:all` по-прежнему доступен как обратно совместимый алиас для того же базового пути установки. `npm run setup:backend:simulation` нужен только тогда, когда вам действительно требуется опциональный рантайм симуляции для Step 3 / Step 5.

Если нужен самый прямой путь запуска только бэкенда с тем же предварительным config-check, используйте `npm run backend:local`. Эта команда сначала выполняет `npm run check:backend-config` и запускает Flask только после того, как текущие алиасы `LLM_*` / `OPENAI_*` успешно разобраны.

Сервисы:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

## OpenAI-Compatible Бэкенды

MiroFish может работать с любым бэкендом, который поддерживает OpenAI-compatible API `chat/completions`. Для настройки можно использовать либо репо-нативные переменные `LLM_*`, либо стандартные алиасы `OPENAI_*`.

Пример:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini

ZEP_API_KEY=your_zep_key
```

Эквивалентный вариант через `LLM_*`:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4.1
```

Бэкенд принимает как проектные переменные `LLM_*`, так и стандартные алиасы `OPENAI_*`, поэтому MiroFish можно напрямую подключить к OpenAI, Codex-compatible шлюзам, LM Studio, Ollama, DashScope или любому другому OpenAI-compatible бэкенду без дополнительных изменений кода и без отдельного флага `LLM_PROVIDER`.

Часто используемые примеры совместимых бэкендов:

```env
# OpenAI / Codex-compatible шлюз
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini

# Alibaba DashScope Coding Plan
OPENAI_API_KEY=your_dashscope_key
OPENAI_API_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
OPENAI_MODEL=qwen3.5-plus
```

Как проверить, что MiroFish распознал прямой OpenAI-compatible путь:

- Откройте `http://localhost:5001/health`, чтобы убедиться, что бэкенд запущен.
- Или выполните `npm run check:backend-config`, чтобы вывести тот же не содержащий секретов JSON `config-status`, не поднимая сервер.
- Если нужен самый прямой путь запуска только бэкенда, используйте `npm run backend:local`. Он применяет тот же preflight, поэтому MiroFish не запустит Flask с некорректной конфигурацией `LLM_*` / `OPENAI_*`.
- Затем откройте `http://localhost:5001/api/graph/config/status`. В JSON-ответе значение `llm.backend_mode` должно быть `openai_compatible`.
- Поле `summary.llm.sources` показывает, были ли использованы переменные `LLM_*` или `OPENAI_*`, а также какой именно base URL победил: `OPENAI_BASE_URL` или `OPENAI_API_BASE_URL`. Это самый быстрый способ проверить, что Codex/OpenAI-compatible шлюз определился корректно без добавления `LLM_PROVIDER`.
- То же `config-status` теперь содержит `summary.capabilities`, где явно разделены состояния «прямой LLM уже готов» и «какие шаги всё ещё зависят от Zep»: `direct_llm` отвечает за прямой путь Codex/OpenAI-compatible, `graph_build` и `graph_report_tools` соответствуют Step 1 / Step 4, а `existing_simulation_interaction` показывает, можно ли продолжить Step 5, если окружение симуляции из Step 2/3 уже существует.
- Если в том же `config-status` всё ещё указано `ZEP_API_KEY is not configured`, это не означает, что прямое OpenAI-compatible LLM-подключение сломано. Это лишь означает, что Step 1 по-прежнему требует Zep, пока в репозитории не появился альтернативный графовый бэкенд.
- Если во время локальной проверки `SECRET_KEY` не задан, предупреждение о временно сгенерированном ключе ожидаемо и не означает, что прямой путь через `OPENAI_*` не работает.

Если `http://localhost:5001` возвращает `404`, это обычно не означает, что бэкенд не запустился. Корневой путь бэкенда обслуживает только API, поэтому для проверки состояния используйте `http://localhost:5001/health`.

Если Step 5 при одиночном диалоге, пакетных опросах или интервью со всеми агентами часто упирается в timeout, увеличьте и фронтендовый таймаут `VITE_API_TIMEOUT` (миллисекунды), и backend-параметры `INTERVIEW_AGENT_TIMEOUT_SECONDS`, `INTERVIEW_BATCH_TIMEOUT_SECONDS`, `INTERVIEW_ALL_TIMEOUT_SECONDS` (секунды).

Для первого запуска лучше брать PDF / Markdown / TXT примерно до 10k слов и держать симуляцию около 30 раундов. Так проще сначала подтвердить сборку графа, настройку окружения и здоровье бэкенда, не тратя лишнюю квоту Zep и не отлаживая сразу несколько масштабных переменных.

## Установка зависимостей

```bash
# Рекомендуемый базовый путь для графа / отчётов / OpenAI-compatible backend
npm run setup:core

# Обратно совместимый алиас для того же базового пути
npm run setup:all

# Ставьте OASIS runtime только если нужен Step 3 / Step 5
npm run setup:backend:simulation
```

Или по шагам:

```bash
# Node-зависимости (root + frontend)
npm run setup

# Основные Python-зависимости backend
npm run setup:backend

# Эквивалентная сокращённая команда
npm run setup:core

# Опциональный simulation runtime
npm run setup:backend:simulation
```

`setup:core` / `setup:all` устанавливает только root-пакет, frontend и основные backend-зависимости для графа, отчётов и прямого OpenAI-compatible подключения. Vendored-код `backend/oasis` уже лежит в репозитории, а дополнительная simulation-установка подтягивает только явные runtime-зависимости.

Известное ограничение: `npm run setup:backend:simulation` может завершиться ошибкой на Python `3.13+`, если в системе нет Rust, потому что текущая цепочка `camel-ai -> tiktoken==0.7.0` всё ещё иногда переходит к source build. Базовый backend-путь это не затрагивает; для реальных Step 3 / Step 5 прогонов лучше использовать Python `3.11`/`3.12` или заранее установить Rust.

## Запуск сервисов

```bash
# Запустить frontend и backend вместе
npm run dev

# Или только backend с preflight-проверкой OpenAI-compatible конфигурации
npm run backend:local
```

Если используется стандартная схема с двумя портами, frontend по умолчанию обращается к backend на `5001` на том же хосте.

## FAQ

**Какие модели и API поддерживаются?**

- Backend принимает любой OpenAI-compatible API и не привязан к одному вендору.
- В текущей ветке уже проверялись OpenAI, Codex-compatible шлюзы, Alibaba DashScope compatible mode, Alibaba DashScope Coding Plan, а также локальные OpenAI-compatible gateway вроде LM Studio и Ollama.
- Можно использовать либо репо-нативные `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL_NAME`, либо стандартные `OPENAI_API_KEY` / `OPENAI_API_BASE_URL` / `OPENAI_MODEL`.

**Что будет, если обновить страницу или закрыть вкладку?**

- Обновление страницы или закрытие вкладки не останавливает уже запущенные backend-задачи графа, симуляции или отчёта.
- Сохранённые данные остаются в `backend/uploads/`, а история на главной странице может снова открыть Step 1, Step 2 и Step 4.
- Step 3 и Step 5 всё ещё зависят от живой OASIS runtime-сессии. Если backend-процесс, контейнер или среда симуляции уже остановлены, эти этапы нельзя бесшовно воспроизвести, их нужно подготавливать или запускать заново.

**Как потом проверить, совпал ли прогноз с реальными событиями?**

- В MiroFish пока нет встроенного загрузчика ground-truth-данных или автоматического скоринга точности, но ручную цепочку проверки уже можно сохранить.
- В Step 4 сохраните `report_id`, а в истории на главной странице удерживайте связанный `simulation_id`. Эти идентификаторы привязывают последующую проверку к одному и тому же графу, окружению и артефактам отчёта.
- Для офлайн-архива можно экспортировать Markdown-отчёт из Step 4 или сохранить файлы из `backend/uploads/reports/<report_id>/full_report.md` и соседний JSON с метаданными.
- Когда у реального события появится продолжение, снова откройте Step 4 из истории и сверяйте ключевые выводы, таймлайн и допущения отчёта с тем, что произошло на самом деле. При необходимости можно параллельно пересмотреть исходный материал и настройки из Step 1 / Step 2.
- Если среда симуляции ещё работает, в Step 5 можно дополнительно спросить Report Agent или отдельных ролей, какие предпосылки подтвердились, а какие нет. Если runtime-сессия уже завершена, текущий поток остаётся ручным: сохранение артефактов Step 4 и последующее сравнение без автоматического backtesting.

## Быстрая backend-проверка

Если `uv sync` или `uv run pytest` блокируются тяжёлыми сборками вроде `tiktoken`, которым нужен Rust toolchain, используйте встроенный лёгкий backend-набор:

```bash
npm run test:backend:lite
```

## Рабочий процесс

1. Построить граф из исходного материала.
2. Сгенерировать конфигурацию окружения и персон.
3. Запустить симуляцию.
4. Сгенерировать отчёт.
5. Взаимодействовать с симулированным миром.

## Полная документация

- Руководство на английском: [README-EN.md](./README-EN.md)
- Руководство на китайском: [README.md](./README.md)
- Шаблон переменных окружения: [`.env.example`](./.env.example)
- Руководство по внесению изменений: [CONTRIBUTING.md](./CONTRIBUTING.md)

## Примечания

- Интерфейс продукта в этой ветке по-прежнему в основном остаётся китайско-английским.
- Upstream PR `#147` содержит гораздо более крупную попытку русской локализации, но безопасно cherry-pick'нуть его целиком нельзя: он заменяет большие части репозитория и удаляет текущие локальные проверки и tooling.
