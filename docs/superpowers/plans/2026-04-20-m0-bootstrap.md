# M0 Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bootstrap the Hotel Deals Bot monorepo with runnable skeletons of all four services (web, api, ai-agent, scraper), local dev infra (Postgres, Redis), and a CI pipeline that lints, typechecks, and tests each service.

**Architecture:** Monorepo with pnpm workspaces for TS services and independent Python `pyproject.toml` for Python services. One `docker-compose.yml` at the root spins up Postgres 16 + Redis 7 for local dev. Each service has a `/health` endpoint and a matching integration test. GitHub Actions workflow runs all tests on push.

**Tech Stack:** pnpm workspaces, Next.js 15, NestJS 11, FastAPI, Python 3.12, PostgreSQL 16, Redis 7, Docker Compose, GitHub Actions, vitest (TS), pytest (Python).

---

## File Structure

**Root:**
- Create `package.json` — root workspace, scripts
- Create `pnpm-workspace.yaml` — workspace globs
- Create `.nvmrc` — Node version
- Create `docker-compose.yml` — PG + Redis for dev
- Create `.env.example` — shared env vars reference
- Create `README.md` — quickstart for humans

**apps/api (NestJS):**
- Create `apps/api/package.json`
- Create `apps/api/tsconfig.json`
- Create `apps/api/nest-cli.json`
- Create `apps/api/src/main.ts`
- Create `apps/api/src/app.module.ts`
- Create `apps/api/src/health/health.controller.ts`
- Create `apps/api/test/health.e2e-spec.ts`

**apps/web (Next.js):**
- Create `apps/web/package.json`
- Create `apps/web/tsconfig.json`
- Create `apps/web/next.config.ts`
- Create `apps/web/src/app/layout.tsx`
- Create `apps/web/src/app/page.tsx`
- Create `apps/web/src/app/api/health/route.ts`
- Create `apps/web/tests/health.test.ts`

**services/ai-agent (Python/FastAPI):**
- Create `services/ai-agent/pyproject.toml`
- Create `services/ai-agent/src/ai_agent/__init__.py`
- Create `services/ai-agent/src/ai_agent/main.py`
- Create `services/ai-agent/tests/test_health.py`

**services/scraper (Python):**
- Create `services/scraper/pyproject.toml`
- Create `services/scraper/src/scraper/__init__.py`
- Create `services/scraper/src/scraper/health.py`
- Create `services/scraper/tests/test_health.py`

**CI:**
- Create `.github/workflows/ci.yml`

---

### Task 1: Monorepo skeleton

**Files:**
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `.nvmrc`
- Create: `README.md`

- [ ] **Step 1.1: Write root `package.json`**

Create `/Users/dmitry/TEST/package.json`:
```json
{
  "name": "hotel-deals-bot",
  "private": true,
  "packageManager": "pnpm@9.15.0",
  "engines": {
    "node": ">=20.11.0"
  },
  "scripts": {
    "typecheck": "pnpm -r typecheck",
    "test": "pnpm -r test",
    "build": "pnpm -r build",
    "dev:infra": "docker compose up -d postgres redis"
  }
}
```

- [ ] **Step 1.2: Write `pnpm-workspace.yaml`**

Create `/Users/dmitry/TEST/pnpm-workspace.yaml`:
```yaml
packages:
  - apps/*
  - packages/*
```

- [ ] **Step 1.3: Write `.nvmrc`**

Create `/Users/dmitry/TEST/.nvmrc`:
```
20.11.0
```

- [ ] **Step 1.4: Write `README.md`**

Create `/Users/dmitry/TEST/README.md`:
```markdown
# Hotel Deals Bot

Global hotel-discount chatbot. See `CLAUDE.md` for project overview and team structure.

## Quickstart (local dev)

Requirements: Node 20+, pnpm 9+, Python 3.12+, Docker.

```bash
# start infra
docker compose up -d postgres redis

# TS services
pnpm install
pnpm -r dev

# Python services
cd services/ai-agent && python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'
cd services/scraper && python -m venv .venv && source .venv/bin/activate && pip install -e '.[dev]'
```

## Tests

```bash
pnpm test                # TS workspaces
cd services/ai-agent && pytest
cd services/scraper && pytest
```

## Docs

- `CLAUDE.md` — project overview and orchestration rules
- `docs/superpowers/specs/` — design specs
- `docs/architecture/decisions/` — ADRs
```

- [ ] **Step 1.5: Verify pnpm installs cleanly**

Run: `cd /Users/dmitry/TEST && pnpm install`
Expected: creates `pnpm-lock.yaml` and `node_modules` without error. No package errors (workspace is currently empty).

- [ ] **Step 1.6: Commit**

```bash
git add package.json pnpm-workspace.yaml .nvmrc README.md pnpm-lock.yaml
git commit -m "feat(m0): monorepo skeleton with pnpm workspaces"
```

---

### Task 2: Local infra via docker-compose

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 2.1: Write `docker-compose.yml`**

Create `/Users/dmitry/TEST/docker-compose.yml`:
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: hotel
      POSTGRES_PASSWORD: hotel
      POSTGRES_DB: hotel_deals
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U hotel"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  pgdata:
  redisdata:
```

- [ ] **Step 2.2: Write `.env.example`**

Create `/Users/dmitry/TEST/.env.example`:
```env
# Database
DATABASE_URL=postgresql://hotel:hotel@localhost:5432/hotel_deals

# Redis
REDIS_URL=redis://localhost:6379

# API
API_PORT=3001
API_BASE_URL=http://localhost:3001

# Web
WEB_PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:3001

# AI Agent
AI_AGENT_PORT=8001
AI_AGENT_BASE_URL=http://localhost:8001
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Scraper
SCRAPER_PORT=8002
```

- [ ] **Step 2.3: Verify services start and become healthy**

Run: `cd /Users/dmitry/TEST && docker compose up -d postgres redis && sleep 8 && docker compose ps`
Expected: both services show `running (healthy)`.

- [ ] **Step 2.4: Verify Postgres accepts connections**

Run: `docker compose exec -T postgres psql -U hotel -d hotel_deals -c 'SELECT 1 AS ok;'`
Expected: output contains `ok` and `1`.

- [ ] **Step 2.5: Verify Redis responds**

Run: `docker compose exec -T redis redis-cli ping`
Expected: `PONG`.

- [ ] **Step 2.6: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "feat(m0): docker-compose with Postgres 16 + Redis 7"
```

---

### Task 3: NestJS API skeleton with /health endpoint (TDD)

**Files:**
- Create: `apps/api/package.json`
- Create: `apps/api/tsconfig.json`
- Create: `apps/api/nest-cli.json`
- Create: `apps/api/src/main.ts`
- Create: `apps/api/src/app.module.ts`
- Create: `apps/api/src/health/health.controller.ts`
- Create: `apps/api/test/health.e2e-spec.ts`
- Create: `apps/api/test/jest-e2e.json`

- [ ] **Step 3.1: Write `apps/api/package.json`**

Create `/Users/dmitry/TEST/apps/api/package.json`:
```json
{
  "name": "@hotel-deals/api",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "build": "nest build",
    "dev": "nest start --watch",
    "start": "node dist/main.js",
    "typecheck": "tsc --noEmit",
    "test": "jest --config test/jest-e2e.json"
  },
  "dependencies": {
    "@nestjs/common": "^11.0.0",
    "@nestjs/core": "^11.0.0",
    "@nestjs/platform-express": "^11.0.0",
    "reflect-metadata": "^0.2.2",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^11.0.0",
    "@nestjs/testing": "^11.0.0",
    "@types/express": "^5.0.0",
    "@types/jest": "^29.5.13",
    "@types/node": "^22.0.0",
    "@types/supertest": "^6.0.2",
    "jest": "^29.7.0",
    "supertest": "^7.0.0",
    "ts-jest": "^29.2.5",
    "typescript": "^5.6.0"
  }
}
```

- [ ] **Step 3.2: Write `apps/api/tsconfig.json`**

Create `/Users/dmitry/TEST/apps/api/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "moduleResolution": "node",
    "declaration": false,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "strict": true,
    "strictNullChecks": true
  },
  "include": ["src/**/*", "test/**/*"]
}
```

- [ ] **Step 3.3: Write `apps/api/nest-cli.json`**

Create `/Users/dmitry/TEST/apps/api/nest-cli.json`:
```json
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src"
}
```

- [ ] **Step 3.4: Write `apps/api/test/jest-e2e.json`**

Create `/Users/dmitry/TEST/apps/api/test/jest-e2e.json`:
```json
{
  "moduleFileExtensions": ["js", "json", "ts"],
  "rootDir": "..",
  "testRegex": ".e2e-spec\\.ts$",
  "transform": {
    "^.+\\.(t|j)s$": "ts-jest"
  },
  "testEnvironment": "node"
}
```

- [ ] **Step 3.5: Write the failing e2e test**

Create `/Users/dmitry/TEST/apps/api/test/health.e2e-spec.ts`:
```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Health endpoint', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('GET /health returns { status: "ok" }', async () => {
    const response = await request(app.getHttpServer()).get('/health');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: 'ok', service: 'api' });
  });
});
```

- [ ] **Step 3.6: Install deps and run test to verify it fails**

Run: `cd /Users/dmitry/TEST && pnpm install && pnpm --filter @hotel-deals/api test`
Expected: FAIL — `AppModule` not found (file doesn't exist yet).

- [ ] **Step 3.7: Write `apps/api/src/health/health.controller.ts`**

Create `/Users/dmitry/TEST/apps/api/src/health/health.controller.ts`:
```typescript
import { Controller, Get } from '@nestjs/common';

@Controller('health')
export class HealthController {
  @Get()
  get() {
    return { status: 'ok', service: 'api' };
  }
}
```

- [ ] **Step 3.8: Write `apps/api/src/app.module.ts`**

Create `/Users/dmitry/TEST/apps/api/src/app.module.ts`:
```typescript
import { Module } from '@nestjs/common';
import { HealthController } from './health/health.controller';

@Module({
  controllers: [HealthController],
})
export class AppModule {}
```

- [ ] **Step 3.9: Write `apps/api/src/main.ts`**

Create `/Users/dmitry/TEST/apps/api/src/main.ts`:
```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const port = Number(process.env.API_PORT ?? 3001);
  await app.listen(port);
  console.log(`api listening on :${port}`);
}
bootstrap();
```

- [ ] **Step 3.10: Run test to verify it passes**

Run: `cd /Users/dmitry/TEST && pnpm --filter @hotel-deals/api test`
Expected: PASS — `1 passed`.

- [ ] **Step 3.11: Run typecheck**

Run: `pnpm --filter @hotel-deals/api typecheck`
Expected: no errors.

- [ ] **Step 3.12: Commit**

```bash
git add apps/api pnpm-lock.yaml
git commit -m "feat(api): NestJS skeleton with /health endpoint + e2e test"
```

---

### Task 4: Next.js web skeleton with landing page and health route (TDD)

**Files:**
- Create: `apps/web/package.json`
- Create: `apps/web/tsconfig.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/src/app/layout.tsx`
- Create: `apps/web/src/app/page.tsx`
- Create: `apps/web/src/app/api/health/route.ts`
- Create: `apps/web/tests/health.test.ts`
- Create: `apps/web/vitest.config.ts`

- [ ] **Step 4.1: Write `apps/web/package.json`**

Create `/Users/dmitry/TEST/apps/web/package.json`:
```json
{
  "name": "@hotel-deals/web",
  "version": "0.0.1",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000",
    "typecheck": "tsc --noEmit",
    "test": "vitest run"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.6.0",
    "vitest": "^2.1.0"
  }
}
```

- [ ] **Step 4.2: Write `apps/web/tsconfig.json`**

Create `/Users/dmitry/TEST/apps/web/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "src/**/*.ts", "src/**/*.tsx", "tests/**/*.ts", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 4.3: Write `apps/web/next.config.ts`**

Create `/Users/dmitry/TEST/apps/web/next.config.ts`:
```typescript
import type { NextConfig } from 'next';

const config: NextConfig = {
  reactStrictMode: true,
};

export default config;
```

- [ ] **Step 4.4: Write `apps/web/vitest.config.ts`**

Create `/Users/dmitry/TEST/apps/web/vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
  },
});
```

- [ ] **Step 4.5: Write the failing test**

Create `/Users/dmitry/TEST/apps/web/tests/health.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';
import { GET } from '../src/app/api/health/route';

describe('GET /api/health', () => {
  it('returns { status: "ok", service: "web" }', async () => {
    const response = await GET();
    expect(response.status).toBe(200);
    const body = await response.json();
    expect(body).toEqual({ status: 'ok', service: 'web' });
  });
});
```

- [ ] **Step 4.6: Install deps and run test to verify it fails**

Run: `cd /Users/dmitry/TEST && pnpm install && pnpm --filter @hotel-deals/web test`
Expected: FAIL — module `../src/app/api/health/route` does not exist.

- [ ] **Step 4.7: Write `apps/web/src/app/api/health/route.ts`**

Create `/Users/dmitry/TEST/apps/web/src/app/api/health/route.ts`:
```typescript
export async function GET() {
  return Response.json({ status: 'ok', service: 'web' });
}
```

- [ ] **Step 4.8: Write `apps/web/src/app/layout.tsx`**

Create `/Users/dmitry/TEST/apps/web/src/app/layout.tsx`:
```tsx
export const metadata = {
  title: 'Hotel Deals Bot',
  description: 'Find the best hotel discounts with an AI chatbot.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

- [ ] **Step 4.9: Write `apps/web/src/app/page.tsx`**

Create `/Users/dmitry/TEST/apps/web/src/app/page.tsx`:
```tsx
export default function HomePage() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>Hotel Deals Bot</h1>
      <p>Coming soon. Find the best hotel discounts via AI chat.</p>
    </main>
  );
}
```

- [ ] **Step 4.10: Run test to verify it passes**

Run: `cd /Users/dmitry/TEST && pnpm --filter @hotel-deals/web test`
Expected: PASS — `1 passed`.

- [ ] **Step 4.11: Run typecheck**

Run: `pnpm --filter @hotel-deals/web typecheck`
Expected: no errors.

- [ ] **Step 4.12: Commit**

```bash
git add apps/web pnpm-lock.yaml
git commit -m "feat(web): Next.js 15 skeleton with landing + /api/health"
```

---

### Task 5: AI agent Python service skeleton (TDD)

**Files:**
- Create: `services/ai-agent/pyproject.toml`
- Create: `services/ai-agent/src/ai_agent/__init__.py`
- Create: `services/ai-agent/src/ai_agent/main.py`
- Create: `services/ai-agent/tests/__init__.py`
- Create: `services/ai-agent/tests/test_health.py`

- [ ] **Step 5.1: Write `services/ai-agent/pyproject.toml`**

Create `/Users/dmitry/TEST/services/ai-agent/pyproject.toml`:
```toml
[project]
name = "ai-agent"
version = "0.0.1"
description = "LLM agent service for Hotel Deals Bot"
requires-python = ">=3.12"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.30.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0.0",
  "httpx>=0.27.0",
  "ruff>=0.6.0",
  "mypy>=1.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/ai_agent"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 5.2: Write `services/ai-agent/src/ai_agent/__init__.py`**

Create `/Users/dmitry/TEST/services/ai-agent/src/ai_agent/__init__.py`:
```python
```

(Empty file.)

- [ ] **Step 5.3: Write `services/ai-agent/tests/__init__.py`**

Create `/Users/dmitry/TEST/services/ai-agent/tests/__init__.py`:
```python
```

(Empty file.)

- [ ] **Step 5.4: Write the failing test**

Create `/Users/dmitry/TEST/services/ai-agent/tests/test_health.py`:
```python
from fastapi.testclient import TestClient

from ai_agent.main import app


def test_health_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ai-agent"}
```

- [ ] **Step 5.5: Create venv, install, run test to verify it fails**

Run:
```bash
cd /Users/dmitry/TEST/services/ai-agent && \
  python3.12 -m venv .venv && \
  source .venv/bin/activate && \
  pip install -e '.[dev]' && \
  pytest
```
Expected: FAIL — `ModuleNotFoundError: No module named 'ai_agent.main'`.

- [ ] **Step 5.6: Write `services/ai-agent/src/ai_agent/main.py`**

Create `/Users/dmitry/TEST/services/ai-agent/src/ai_agent/main.py`:
```python
from fastapi import FastAPI

app = FastAPI(title="ai-agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-agent"}
```

- [ ] **Step 5.7: Run test to verify it passes**

Run: `cd /Users/dmitry/TEST/services/ai-agent && source .venv/bin/activate && pytest`
Expected: PASS — `1 passed`.

- [ ] **Step 5.8: Add `.venv/` to `.gitignore`**

Check `/Users/dmitry/TEST/.gitignore` already contains `.venv/` from the bootstrap commit. If not, add it.

Run: `grep -q '^.venv/' /Users/dmitry/TEST/.gitignore && echo OK || echo MISSING`
Expected: `OK`.

- [ ] **Step 5.9: Commit**

```bash
git add services/ai-agent/pyproject.toml services/ai-agent/src services/ai-agent/tests
git commit -m "feat(ai-agent): FastAPI skeleton with /health + pytest"
```

---

### Task 6: Scraper Python service skeleton (TDD)

**Files:**
- Create: `services/scraper/pyproject.toml`
- Create: `services/scraper/src/scraper/__init__.py`
- Create: `services/scraper/src/scraper/health.py`
- Create: `services/scraper/tests/__init__.py`
- Create: `services/scraper/tests/test_health.py`

- [ ] **Step 6.1: Write `services/scraper/pyproject.toml`**

Create `/Users/dmitry/TEST/services/scraper/pyproject.toml`:
```toml
[project]
name = "scraper"
version = "0.0.1"
description = "Hotel aggregator scraper service for Hotel Deals Bot"
requires-python = ">=3.12"
dependencies = [
  "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0.0",
  "ruff>=0.6.0",
  "mypy>=1.11.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/scraper"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 6.2: Write package init files**

Create `/Users/dmitry/TEST/services/scraper/src/scraper/__init__.py`:
```python
```

Create `/Users/dmitry/TEST/services/scraper/tests/__init__.py`:
```python
```

(Both empty.)

- [ ] **Step 6.3: Write the failing test**

Create `/Users/dmitry/TEST/services/scraper/tests/test_health.py`:
```python
from scraper.health import health


def test_health_returns_ok() -> None:
    assert health() == {"status": "ok", "service": "scraper"}
```

- [ ] **Step 6.4: Create venv, install, run test to verify it fails**

Run:
```bash
cd /Users/dmitry/TEST/services/scraper && \
  python3.12 -m venv .venv && \
  source .venv/bin/activate && \
  pip install -e '.[dev]' && \
  pytest
```
Expected: FAIL — `ModuleNotFoundError: No module named 'scraper.health'`.

- [ ] **Step 6.5: Write `services/scraper/src/scraper/health.py`**

Create `/Users/dmitry/TEST/services/scraper/src/scraper/health.py`:
```python
def health() -> dict[str, str]:
    return {"status": "ok", "service": "scraper"}
```

- [ ] **Step 6.6: Run test to verify it passes**

Run: `cd /Users/dmitry/TEST/services/scraper && source .venv/bin/activate && pytest`
Expected: PASS — `1 passed`.

- [ ] **Step 6.7: Commit**

```bash
git add services/scraper/pyproject.toml services/scraper/src services/scraper/tests
git commit -m "feat(scraper): Python package skeleton with health() + pytest"
```

---

### Task 7: GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 7.1: Write the workflow**

Create `/Users/dmitry/TEST/.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  ts:
    name: TS workspaces
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck
      - run: pnpm test

  ai-agent:
    name: Python ai-agent
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: services/ai-agent
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e '.[dev]'
      - run: ruff check .
      - run: pytest

  scraper:
    name: Python scraper
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: services/scraper
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e '.[dev]'
      - run: ruff check .
      - run: pytest
```

> TypeScript linting (ESLint) is intentionally deferred to M1, where we'll set up a shared `@hotel-deals/eslint-config` package in `packages/`. For M0 the TS quality gate is typecheck + test.

- [ ] **Step 7.2: Commit and push**

```bash
cd /Users/dmitry/TEST && \
  git add .github/workflows/ci.yml && \
  git commit -m "ci(m0): GitHub Actions workflow for TS + Python services" && \
  git push
```

- [ ] **Step 7.3: Verify CI passes on GitHub**

Open https://github.com/dvvolkovv/travel_bot/actions and confirm the `CI` workflow's three jobs (`ts`, `ai-agent`, `scraper`) all pass on the latest commit.

Expected: all three jobs green.

If any job fails, fix the underlying issue, commit, push, and recheck.

---

### Task 8: Post-bootstrap verification

**Files:** none created — this task runs the full stack locally end-to-end.

- [ ] **Step 8.1: Tear down and bring infra up cleanly**

Run:
```bash
cd /Users/dmitry/TEST && \
  docker compose down -v && \
  docker compose up -d postgres redis && \
  sleep 8 && \
  docker compose ps
```
Expected: both services `running (healthy)`.

- [ ] **Step 8.2: Start api in background, curl /health**

Run (in separate terminal, or background):
```bash
cd /Users/dmitry/TEST && \
  pnpm --filter @hotel-deals/api dev &
# wait ~8s for Nest to start
sleep 8 && \
curl -s http://localhost:3001/health
```
Expected: `{"status":"ok","service":"api"}`.

Stop the api: `kill %1` (or Ctrl-C in its terminal).

- [ ] **Step 8.3: Start web in background, curl /api/health**

Run:
```bash
cd /Users/dmitry/TEST && \
  pnpm --filter @hotel-deals/web dev &
sleep 10 && \
curl -s http://localhost:3000/api/health
```
Expected: `{"status":"ok","service":"web"}`.

Stop the web: `kill %1`.

- [ ] **Step 8.4: Start ai-agent via uvicorn, curl /health**

Run:
```bash
cd /Users/dmitry/TEST/services/ai-agent && \
  source .venv/bin/activate && \
  uvicorn ai_agent.main:app --port 8001 &
sleep 3 && \
curl -s http://localhost:8001/health
```
Expected: `{"status":"ok","service":"ai-agent"}`.

Stop the service: `kill %1`.

- [ ] **Step 8.5: Record verification in CLAUDE.md**

Update `/Users/dmitry/TEST/CLAUDE.md`, section `## Окружения`:

Change the empty DEV row to reflect the working local dev stack. Replace the table rows with:
```markdown
| | DEV (local) | STAGING | PROD |
|--|-------------|---------|------|
| URL (web) | `http://localhost:3000` | `—` | `—` |
| URL (api) | `http://localhost:3001` | `—` | `—` |
| URL (ai-agent) | `http://localhost:8001` | `—` | `—` |
| Postgres | `localhost:5432` (docker) | `—` | `—` |
| Redis | `localhost:6379` (docker) | `—` | `—` |
```

- [ ] **Step 8.6: Commit and push**

```bash
cd /Users/dmitry/TEST && \
  git add CLAUDE.md && \
  git commit -m "docs(m0): record local dev environment in CLAUDE.md" && \
  git push
```

M0 complete. Next plan: M1 — Booking.com parser + agent with 2 tools + chat UI with SSE + i18n EN/RU skeleton.
