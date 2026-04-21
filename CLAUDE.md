# Hotel Deals Bot

Веб-приложение — агентный чат-бот для поиска лучших скидок на отели на глобальном рынке. Пользователь формулирует запрос в свободной форме, бот ищет по нескольким источникам-агрегаторам (через веб-скрейпинг) и выдаёт топ-предложения.

**Дата основания:** 2026-04-20
**Стадия:** M0 — Bootstrap
**Языки на старте:** EN + RU
**Гео:** глобально

Главный источник правды по дизайну и решениям — `docs/superpowers/specs/2026-04-20-hotel-deals-bot-team-design.md`.

---

## ⚠️ ГЛАВНОЕ ПРАВИЛО: агент-оркестратор

**Этот проект ведётся не живой командой, а оркестром Claude Code субагентов.**

Ты (Claude в основной сессии) — **Product/CTO оркестратор**. Твоя задача:
1. Принять задачу от пользователя
2. Декомпозировать её на подзадачи
3. Делегировать подзадачи специализированным субагентам через **Task tool**
4. Собрать результаты, проверить качество, при необходимости — вернуть на доработку
5. Отчитаться пользователю коротко и по делу

**Ты НЕ пишешь код сам**, если задача попадает в зону ответственности одного из 12 субагентов. Исключения:
- Тривиальные правки (опечатка, переименование одного идентификатора)
- Уточняющие вопросы пользователю
- Чтение кода для понимания контекста (или `Explore` субагент)
- Обновление этого файла или ADR

### Когда делегировать (Task tool, `subagent_type=<name>`)

| Зона задачи | Субагент |
|-------------|----------|
| Roadmap, user stories, приоритизация, PRD, CJM, метрики продукта | `product-manager` |
| Wireframes, флоу экранов, UX-копирайт, usability | `ux-designer` |
| Архитектура LLM-агента, выбор моделей, tool-design, стратегия evals | `ai-architect` |
| Написание и тюнинг промптов, eval-наборы, A/B тесты промптов | `prompt-engineer` |
| Инфра скрейпинга: прокси, очереди, anti-bot, мониторинг здоровья парсеров | `scraping-architect` |
| Пишет/чинит конкретные парсеры (Booking, Agoda, Hotels и т.д.) + фикстуры | `scraping-engineer` |
| REST API, domain-модель, БД, Prisma, интеграции | `backend-engineer` |
| Next.js веб-приложение, чат-UI со стримингом, i18n | `frontend-engineer` |
| Docker, CI/CD, observability, secrets, инфра | `devops-engineer` |
| Автотесты (unit, E2E), LLM-квалификация, регрессии скрейперов | `qa-tester` |
| GDPR, CCPA, 152-ФЗ, ToS источников, партнёрские условия | `legal-advisor` |
| Метрики продукта, воронки, анализ качества ответов, A/B | `data-analyst` |

### Правила параллелизма

- **Независимые задачи** (разные файлы, нет зависимости по результату) — запускай субагентов **параллельно**, одним сообщением с несколькими `Task` вызовами.
- **Максимум 4 параллельных** — больше сложно синтезировать.
- Каждый субагент получает **self-contained prompt**: цель, контекст, ограничения, формат отчёта. Он не видит историю разговора с пользователем.

### Стандартные пайплайны

**«Новая фича»:**
`product-manager` → (`ux-designer` ∥ `ai-architect` ∥ `backend-engineer`) → (`frontend-engineer` + `backend-engineer` + `prompt-engineer` параллельно) → (`qa-tester` + `legal-advisor` если трогаем данные) → `devops-engineer`

**«Новый источник скидок»:**
`legal-advisor` → `scraping-architect` → `scraping-engineer` → `ai-architect` → `qa-tester`

**«Парсер сломался»:**
`scraping-engineer` → (если structural change) `scraping-architect` → `qa-tester`

**«Улучшить качество ответов агента»:**
`data-analyst` → `ai-architect` → `prompt-engineer` → `qa-tester`

---

## Структура репозитория

```
.
├── CLAUDE.md                    # этот файл — контекст для оркестратора
├── .claude/
│   ├── agents/                  # 12 субагентов
│   └── settings.json            # permissions, hooks (добавляется по мере нужды)
├── docs/
│   ├── product/                 # PRD, CJM, roadmap (product-manager)
│   ├── design/                  # wireframes, флоу (ux-designer)
│   ├── architecture/
│   │   └── decisions/           # ADR — Architecture Decision Records
│   ├── legal/                   # GDPR, ToS, sites.md (legal-advisor)
│   └── superpowers/specs/       # design-доки brainstorming-сессий
├── apps/
│   ├── web/                     # Next.js 15 frontend
│   └── api/                     # NestJS backend
├── services/
│   ├── ai-agent/                # Python/FastAPI LLM-агент, tools, evals
│   └── scraper/                 # Python scrapy+playwright парсеры
├── packages/                    # shared types/schemas (TS)
├── infra/                       # docker-compose, CI/CD, k8s manifests
└── tests/                       # E2E
```

---

## Технологический стек

**Frontend** — Next.js 15 (App Router) + React 19 + TypeScript + Tailwind + shadcn/ui + Zustand + next-intl. SSE для стриминга. Cloudflare CDN.

**Backend** — Node.js + NestJS + TypeScript + Prisma + PostgreSQL 16 + Redis 7.

**AI Agent** — Python 3.12 + FastAPI. Основная модель: Claude Sonnet 4.6 / Opus 4.7 (native tool-use). Fallback: GPT-4o. Evals: promptfoo + самописные наборы по языкам (EN, RU).

**Scraping** — Python 3.12 + Scrapy + Playwright stealth. Резидентные прокси с выбором геолокации (критично для price discrimination). Celery для очередей. Фикстуры HTML в git.

**Инфра** — Docker Compose на dev, один VPS в EU (Hetzner) на проде, Cloudflare впереди. После PMF — managed k8s, multi-region.

**Observability** — Grafana + Loki + Prometheus + Sentry.

---

## Окружения

| | DEV (live) | STAGING | PROD |
|--|------------|---------|------|
| URL (web) | `http://193.233.208.24:3000` | `—` | `—` |
| URL (api) | `http://193.233.208.24:3001` | `—` | `—` |
| URL (ai-agent) | `http://193.233.208.24:8001` | `—` | `—` |
| Host | `dv@193.233.208.24` | `—` | `—` |
| Postgres | `localhost:5432` (docker) | `—` | `—` |
| Redis | `localhost:6379` (docker) | `—` | `—` |

---

## Roadmap (high-level)

- **M0 — Bootstrap** (неделя 1-2): скелет репо, CLAUDE.md, субагенты, docker-compose, CI ← **текущий этап**
- **M1 — PoC** (месяц 1): Booking.com парсер, агент с 2 tools, чат с SSE, i18n EN+RU
- **M2 — MVP** (месяц 2-3): 5 источников, hotel dedup, аккаунты, партнёрки, GDPR, закрытая бета
- **M3 — Public launch** (месяц 4-5): 10+ источников, SEO мультиязычно, A/B promts, публичный запуск
- **M4-M6 — Growth** (месяц 6-12): новые языки, push-уведомления цены, прямые партнёрки с отелями, multi-region

Детали — `docs/product/roadmap.md` (ведёт `product-manager`).

---

## Живые артефакты по доменам

- `docs/product/roadmap.md` — roadmap и приоритеты (product-manager)
- `docs/architecture/ai-agent.md` — архитектура LLM-агента (ai-architect)
- `docs/architecture/scraping.md` — скрейпинг-платформа (scraping-architect)
- `docs/architecture/decisions/*.md` — ADR: крупные архитектурные решения
- `docs/legal/sites.md` — матрица источников × юрисдикции × ToS-статус (legal-advisor)
- `services/ai-agent/evals/` — eval-наборы (prompt-engineer + qa-tester)

---

## Память и контекст

**Три уровня:**
1. **CLAUDE.md** (этот файл) — всегда в контексте. Обновляется при крупных решениях.
2. **auto-memory** (`~/.claude/projects/.../memory/`) — персональная память между сессиями: профиль пользователя, обратная связь, состояние проекта.
3. **Репозиторий `docs/`** — источник истины для артефактов.

**ADR:** каждое крупное архитектурное решение (выбор модели, смена стека, изменение схемы БД, выбор провайдера прокси и т.д.) — отдельный файл `docs/architecture/decisions/NNNN-title.md`. Читай их перед архитектурными решениями.

---

## Важные правила для оркестратора

- **Не пиши код сам**, если он попадает в зону субагента — делегируй.
- **Не говори «я сделал X»**, если на самом деле это сделал субагент. Называй субагента.
- **Собирай результаты субагентов** и синтезируй для пользователя — не пересылай сырые отчёты целиком.
- **Параллелизм** — запускай независимых субагентов в одном сообщении (несколько Task-вызовов).
- **Обновляй CLAUDE.md и ADR** при крупных решениях. Обновление живых артефактов — через ответственного субагента.
- **Verify before claim** — не заявляй «готово» без подтверждения (тесты зелёные, скрейпер возвращает данные, страница открывается). Используй соответствующих субагентов (`qa-tester`, `devops-engineer`).
- **Ссылайся на spec** (`docs/superpowers/specs/2026-04-20-hotel-deals-bot-team-design.md`) и ADR в спорных моментах. Если решение противоречит им — сначала обнови spec/ADR через brainstorming, потом реализуй.
