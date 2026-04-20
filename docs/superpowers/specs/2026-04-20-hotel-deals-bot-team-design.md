# Hotel Deals Bot — Dream Team Design

**Дата:** 2026-04-20
**Статус:** Draft → User Review
**Автор:** brainstorming session (оркестратор + dvvolkovv@gmail.com)

## Контекст и цели

**Продукт:** веб-приложение — чат-бот для поиска лучших скидок на отели на глобальном рынке.

**Ключевые свойства:**
- Пользователь формулирует запрос в свободной форме («Barcelona for 5 nights in June under €600», «хочу в Сочи на майские до 50к»)
- Бот находит лучшие предложения по нескольким источникам и выдаёт топ
- Поиск через веб-скрейпинг агрегаторов (не официальные API)
- Ядро — агентный LLM: сам оркестрирует tools (скрейперы, ранжирование, калькуляторы)
- **Языки на старте: EN + RU** (архитектурно мультиязычно с первого дня, другие языки — после PMF)
- **Гео-охват:** глобальный (Booking.com, Agoda, Hotels.com как основа + локальные агрегаторы по регионам)
- Горизонт: 6-12 месяцев до зрелого продукта

**Уникальность подхода:** это не живая команда из людей. Это **оркестр Claude Code субагентов**. Главный агент (оркестратор в основной сессии) выступает как CTO/Product lead и делегирует задачи 12 специализированным субагентам через Task tool.

## Архитектура команды

### Оркестратор (главный агент)

Работает в основной Claude Code сессии в корне репозитория. Не субагент — это «я», который получает задачи от пользователя напрямую.

**Ответственность:**
- Принимает задачи от пользователя на человеческом языке
- Декомпозирует на подзадачи, выбирает нужных субагентов
- Запускает субагентов через Task tool (параллельно где возможно)
- Собирает результаты, проверяет качество, при необходимости возвращает на доработку
- Отчитывается пользователю, ведёт roadmap и память проекта
- Делает тривиальные правки сам (опечатки, мелкий рефакторинг) — без субагентов

### 12 субагентов

Каждый субагент — файл в `.claude/agents/<name>.md` с YAML frontmatter (`name`, `description`, `tools`) и system prompt.

| # | Агент | Зона ответственности |
|---|-------|----------------------|
| 1 | `product-manager` | Backlog, user stories, приоритизация, CJM, метрики, PRD |
| 2 | `ux-designer` | Wireframes (HTML/текстовые), флоу экранов, UX-копирайт |
| 3 | `ai-architect` | Архитектура LLM-агента: выбор моделей, tools, eval-стратегия |
| 4 | `prompt-engineer` | Пишет/тюнит промпты и tools, строит eval-наборы |
| 5 | `scraping-architect` | Инфра скрейпинга: прокси-пул, очереди, anti-bot, мониторинг |
| 6 | `scraping-engineer` | Пишет и чинит парсеры конкретных сайтов |
| 7 | `backend-engineer` | API, domain-модель, БД, интеграции |
| 8 | `frontend-engineer` | Next.js веб-приложение, чат-UI со стримингом |
| 9 | `devops-engineer` | Docker, CI/CD, observability, secrets, инфра |
| 10 | `qa-tester` | Автотесты (E2E, unit), тесты качества LLM, регрессии скрейперов |
| 11 | `legal-advisor` | GDPR, CCPA, 152-ФЗ, ToS, риски скрейпинга, партнёрские условия, cookie law |
| 12 | `data-analyst` | Метрики, воронки, оценка качества ответов, A/B |

**Пример заголовка субагента:**

```markdown
---
name: scraping-engineer
description: Use when writing or fixing scrapers for hotel aggregators (Booking.com, Agoda, Hotels.com, Ostrovok, regional sites). Input: target site + fields needed. Output: parser code + test fixtures.
tools: Read, Write, Edit, Grep, Glob, Bash
---

You are a senior web scraping engineer specializing in global travel aggregators.
...
```

Полные промпты каждого агента генерируются на этапе реализации.

### Tool permissions по ролям

Каждый субагент получает узкий набор инструментов — принцип минимальных привилегий.

| Агент | Разрешённые tools |
|-------|-------------------|
| product-manager | Read, Write, Edit, Grep, Glob |
| ux-designer | Read, Write, Edit, Grep, Glob |
| ai-architect | Read, Write, Edit, Grep, Glob, Bash, WebFetch |
| prompt-engineer | Read, Write, Edit, Grep, Glob, Bash |
| scraping-architect | Read, Write, Edit, Grep, Glob, Bash, WebFetch |
| scraping-engineer | Read, Write, Edit, Grep, Glob, Bash, WebFetch |
| backend-engineer | Read, Write, Edit, Grep, Glob, Bash |
| frontend-engineer | Read, Write, Edit, Grep, Glob, Bash |
| devops-engineer | Read, Write, Edit, Grep, Glob, Bash |
| qa-tester | Read, Write, Edit, Grep, Glob, Bash |
| legal-advisor | Read, Write, Edit, Grep, Glob, WebFetch |
| data-analyst | Read, Write, Edit, Grep, Glob, Bash |

## Workflow оркестратора

### Базовый цикл

```
Пользователь → Оркестратор:
  1. Понимает задачу, уточняет если неясно
  2. Классифицирует: research / design / implementation / bugfix / ops
  3. Декомпозирует на подзадачи
  4. Строит DAG зависимостей (что параллельно, что последовательно)
  5. Запускает субагентов через Task tool
  6. Собирает результаты, проверяет, при необходимости — доработка
  7. Отчёт пользователю + обновление памяти проекта
```

### Стандартные пайплайны

**Пайплайн A — «Новая фича»**
```
product-manager → ux-designer ∥ ai-architect ∥ backend-engineer
                → frontend-engineer + backend-engineer + prompt-engineer (parallel)
                → qa-tester + legal-advisor (if user data / new source)
                → devops-engineer (deploy)
```

**Пайплайн B — «Добавить новый источник скидок»**
```
legal-advisor → scraping-architect → scraping-engineer → ai-architect → qa-tester
```

**Пайплайн C — «Парсер сломался»**
```
scraping-engineer → (if structural change) scraping-architect → qa-tester
```

**Пайплайн D — «Улучшить качество ответов агента»**
```
data-analyst → ai-architect → prompt-engineer → qa-tester
```

### Правила параллелизма

- Независимые задачи (разные файлы, нет зависимости по результату) — один message, несколько Task-вызовов
- Максимум 4 параллельных субагента — иначе синтез результата становится ненадёжным
- Каждый субагент получает self-contained prompt (цель, контекст, ограничения, формат отчёта) — не видит историю разговора с пользователем

### Когда оркестратор НЕ делегирует

- Тривиальные правки (опечатка, переименование) — делает сам
- Уточняющие вопросы пользователю — сам
- Чтение кода для понимания — сам (или Explore-агент)

## Структура проекта

```
TEST/
├── CLAUDE.md                    # главный документ — контекст проекта
├── .claude/
│   ├── agents/                  # 12 субагентов
│   │   ├── product-manager.md
│   │   ├── ux-designer.md
│   │   ├── ai-architect.md
│   │   ├── prompt-engineer.md
│   │   ├── scraping-architect.md
│   │   ├── scraping-engineer.md
│   │   ├── backend-engineer.md
│   │   ├── frontend-engineer.md
│   │   ├── devops-engineer.md
│   │   ├── qa-tester.md
│   │   ├── legal-advisor.md
│   │   └── data-analyst.md
│   └── settings.json            # permissions, hooks
├── docs/
│   ├── product/                 # PRD, CJM, roadmap (product-manager)
│   ├── design/                  # wireframes, флоу (ux-designer)
│   ├── architecture/            # AI-агент, скрейпинг, backend
│   │   └── decisions/           # ADR
│   ├── legal/                   # ToS, политики
│   │   └── sites.md             # список источников + их ToS/robots.txt статус
│   └── superpowers/specs/       # design-доки brainstorming-сессий
├── apps/
│   ├── web/                     # Next.js frontend
│   └── api/                     # NestJS backend
├── services/
│   ├── ai-agent/                # LLM-агент, tools, evals (Python/FastAPI)
│   │   └── evals/               # eval-наборы
│   └── scraper/                 # скрейпинг-платформа и парсеры (Python)
├── packages/                    # shared types/schemas
├── infra/                       # docker-compose, CI/CD, k8s-manifests
└── tests/                       # E2E-тесты
```

## Технологический стек

### Frontend (apps/web)
- Next.js 15 (App Router) — SSR для SEO
- React 19 + TypeScript
- Tailwind CSS + shadcn/ui
- Zustand — клиентский state
- Server-Sent Events для стриминга ответов LLM
- **i18n:** next-intl, роутинг `/<locale>/...`, языки на старте: `en`, `ru`; fallback → `en`
- **CDN:** Cloudflare (статика + edge-кеш SEO-страниц)

### Backend (apps/api)
- Node.js + NestJS + TypeScript
- PostgreSQL 16 (Prisma ORM)
- Redis 7 — сессии, кеш, очереди (BullMQ)
- SSE для стриминга от AI-агента к фронту

### AI Agent (services/ai-agent)
- Python 3.12 + FastAPI
- Основная модель: Claude Sonnet 4.6 / Opus 4.7 (сильно в агентных сценариях на EN и RU)
- Fallback: GPT-4o (на случай лимитов Anthropic и как дублирующая оценка)
- Native tool-use API
- Промпты мультиязычные: system prompt на EN, пользовательский язык детектится и агент отвечает на нём
- Валюта и единицы: tools конвертируют цены в валюту пользователя (ECB / открытые курсы)
- promptfoo + самописные evals (eval-наборы для каждого поддерживаемого языка)

### Scraping (services/scraper)
- Python 3.12
- Scrapy — структурные парсеры
- Playwright (headless Chromium) — JS-heavy сайты и anti-bot обход
- **Гео-прокси:** резидентные (Bright Data / Smartproxy) с выбором страны — критично, цены на отелях зависят от гео-локации юзера (см. Booking.com price discrimination)
- + дата-центр прокси как дешёвый пул для некритичных запросов
- Captcha: 2Captcha / CapMonster как fallback
- Celery (Python) — очередь задач (сервис на Python, логично)
- Фикстуры HTML в git для регрессий
- **Нормализация валют:** все цены хранятся в базовой (USD) + оригинал; конверсия на лету для юзера

### Инфраструктура
- Docker + docker-compose для dev
- Production старт: один VPS в EU (Hetzner — Falkenstein / Helsinki) — оптимальная latency для EU+US+RU юзеров
- Cloudflare перед всем — CDN, DDoS-защита, edge-кеш, глобальный охват статики
- После PMF: managed Kubernetes, multi-region (US + EU как минимум)
- CI/CD: GitHub Actions
- Observability: Grafana + Loki + Prometheus + Sentry
- Secrets: Doppler / Infisical

### Модели данных (основные)
`User` (+ preferred locale, currency), `Session`, `SearchQuery`, `Hotel` (кеш, глобальный по `hotel_id` + source_ids mapping), `Offer` (цена в базовой валюте + оригинал + источник), `Booking` (редирект на партнёра), `ChatThread`, `ChatMessage`, `AgentTrace` (логи работы агента), `LocaleContent` (i18n контент отелей, если скрейпим описания).

### YAGNI — чего намеренно НЕТ на старте
- Микросервисы (монорепо + несколько apps/services достаточно)
- GraphQL (REST + типизированные клиенты)
- Kubernetes (только после PMF)
- Собственная LLM (используем API)
- Mobile apps (только web + адаптивный дизайн)

## Roadmap

### M0 — Bootstrap (неделя 1-2)
- Скелет репо, CLAUDE.md, 12 субагентов
- docker-compose с PG + Redis
- Базовые Next.js + NestJS hello-world
- CI (lint, typecheck, test)

### M1 — Proof of concept (месяц 1)
- Парсер 1 глобального источника (Booking.com) с фикстурами и гео-прокси (проверка price discrimination)
- LLM-агент с 2 tools: `search_hotels`, `get_hotel_details`
- Чат-интерфейс: юзер пишет (EN или RU) → получает топ-5 с ценами в своей валюте
- i18n-скелет (next-intl) с двумя локалями
- Ответы через SSE со стримингом

### M2 — MVP (месяц 2-3)
- 5 источников скрейпинга (Booking.com, Agoda, Hotels.com, Expedia, Ostrovok) + health monitoring
- Hotel deduplication по геокоординатам + fuzzy match названия (один и тот же отель в разных источниках → один `Hotel`)
- Агент: уточняющие вопросы, ранжирование по предпочтениям, конверсия валют
- Аккаунты, история поисков, сохранённые отели
- Реферальные ссылки + трекинг конверсий (партнёрки Booking.com, Agoda)
- GDPR cookie consent + privacy policy
- Закрытая бета (~50 юзеров — EN + RU)

### M3 — Public launch (месяц 4-5)
- 10+ источников с региональным покрытием (добавить Trip.com для Азии, латам-агрегаторы)
- Автоматический fallback при поломке источника
- Персонализация на основе истории
- A/B тесты промптов через eval-наборы (отдельные eval-наборы для EN и RU)
- SEO-страницы (города, отели, направления) — мультиязычно, `hreflang`
- Публичный запуск + маркетинг (SEO + performance-маркетинг)

### M4-M6 — Growth (месяц 6-12)
- Добавить 3-4 новых языка (DE, ES, FR, ZH) по данным трафика и конверсии
- Прямые партнёрки с отелями (эксклюзивные скидки)
- Push-уведомления о снижении цены на сохранённый отель
- Email-дайджесты
- Multi-region инфра (US + EU)

## Стратегия памяти и контекста

Три уровня:

1. **CLAUDE.md** (корень) — всегда в контексте. Описывает проект, команду, стек, деплой, окружения. Обновляется при крупных решениях.
2. **auto-memory** (`~/.claude/projects/.../memory/`) — персональная память между сессиями: профиль пользователя, обратная связь, состояние проекта.
3. **Репозиторий (`docs/`)** — источник истины для артефактов: ADR, PRD, дизайн-доки, eval-результаты.

### ADR (Architecture Decision Records)
Каждое крупное решение (выбор модели, смена стека, схема БД) — отдельный файл `docs/architecture/decisions/NNNN-title.md`. Оркестратор читает ADR перед архитектурными решениями.

### Живые артефакты по агентам
- `docs/product/roadmap.md` — product-manager
- `docs/architecture/ai-agent.md` — ai-architect
- `docs/architecture/scraping.md` — scraping-architect
- `docs/legal/sites.md` — legal-advisor (источники + их ToS/robots.txt статус)
- `services/ai-agent/evals/` — prompt-engineer + qa-tester

### Старт работы
Пользователь приходит → оркестратор читает CLAUDE.md и auto-memory → понимает текущий этап → предлагает следующий шаг или принимает задачу.

## Известные риски

| Риск | Митигация |
|------|-----------|
| Скрейпинг юридически серый (GDPR, CCPA, 152-ФЗ, ToS Booking/Agoda) | legal-advisor на старте готовит матрицу источник × юрисдикция; приоритет тем, кто разрешает public-data scraping; партнёрские API (Booking Affiliate, Expedia EPS) как «белый» путь при росте |
| Парсеры часто ломаются | Фикстуры HTML в git, health monitoring, быстрый пайплайн починки (C), scraping-engineer как dedicated роль |
| Качество LLM-ответов деградирует | Eval-наборы с регрессиями по каждому языку, data-analyst мониторит прод, prompt-engineer тюнит без потери стабильности |
| Anti-bot на глобальных агрегаторах сильнее, чем на RU-сайтах | Резидентные прокси с нужной геолокацией + ротация + Playwright со stealth-режимом; scraping-architect владеет стратегией |
| Rate limits LLM API | Fallback на GPT-4o, кеширование частых запросов, батчинг |
| Price discrimination по гео (Booking показывает разные цены из US/EU/Asia) | scraping-architect: policy — скрейпить из гео пользователя через резидентный прокси; кешировать по ключу `(hotel, dates, user_country)` |
| Валютные колебания между скрейпом и бронированием | Показываем курс на момент запроса + явная пометка «курс на HH:MM»; при клике на партнёра — пересчёт на их валюту |
| Локализация контента отелей (описания, amenities) | Скрейпить описания на нескольких языках где возможно; fallback — переводить описание на лету через LLM |
| GDPR compliance | legal-advisor на старте: cookie consent, DSR endpoints (право на забвение, экспорт), DPA, privacy policy — выполнены до public launch (M3) |

## Следующие шаги (после апрува spec)

1. Создать `CLAUDE.md` в корне проекта
2. Создать 12 субагентов в `.claude/agents/`
3. Инициализировать структуру директорий `docs/`, `apps/`, `services/`, `infra/`
4. Первый ADR: «Using Claude Code sub-agents as dream team»
5. Перейти к writing-plans skill для плана M0 Bootstrap

## Open questions (к пользователю)

Ничего критичного на уровне спеки — все ключевые выборы зафиксированы. Детали решаются в ADR на этапе реализации:
- Выбор провайдера резидентных прокси (Bright Data vs Smartproxy vs Oxylabs)
- Точные модели LLM на проде (Sonnet 4.6 vs Opus 4.7 — по eval-скору и цене)
- Хостинг (Hetzner vs Vercel + Railway vs AWS) — зависит от GDPR и бюджета
- Партнёрские программы для монетизации (Booking Affiliate vs Impact/Awin vs прямые)
