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
