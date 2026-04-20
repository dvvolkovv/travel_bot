# ADR 0001: Claude Code sub-agents as the dream team

**Date:** 2026-04-20
**Status:** Accepted

## Context

We are starting Hotel Deals Bot — a global chatbot for hotel discount search. The design spec (`docs/superpowers/specs/2026-04-20-hotel-deals-bot-team-design.md`) calls for a ~12-person product org covering product, design, AI, scraping, backend, frontend, DevOps, QA, legal, analytics.

The operator of this project is a solo founder working through Claude Code. Hiring a real 12-person team is neither feasible nor the goal. The question is how to structure the work so it scales beyond what one person can hold in their head.

## Decision

**Use Claude Code sub-agents as the team.** The main Claude Code session acts as a Product/CTO orchestrator. Twelve specialized sub-agents (defined in `.claude/agents/*.md`) do the specialized work.

- The orchestrator receives tasks from the user, decomposes them, delegates via the `Task` tool, and synthesizes results.
- Each sub-agent has a narrow role, a tight tool permission set, a system prompt with responsibilities and constraints, and a defined output format.
- The orchestrator itself does NOT do specialized work; it only does cross-cutting coordination, trivial edits, and clarifying questions.

Sub-agents: `product-manager`, `ux-designer`, `ai-architect`, `prompt-engineer`, `scraping-architect`, `scraping-engineer`, `backend-engineer`, `frontend-engineer`, `devops-engineer`, `qa-tester`, `legal-advisor`, `data-analyst`.

## Rationale

- **Context preservation.** Each sub-agent runs in its own context. The orchestrator only sees summary reports, not every file the sub-agent reads. This keeps the orchestrator's context usable across a long session.
- **Specialization.** Each role has different priorities, constraints, and «how they think». A single prompt trying to cover all roles dilutes all of them. Twelve focused prompts each do one thing well.
- **Parallelism.** Independent tasks (e.g., scraper + frontend + legal review) run concurrently via multiple `Task` invocations in one orchestrator message.
- **Tool scoping.** `legal-advisor` doesn't need `Bash`; `prompt-engineer` doesn't need `WebFetch`. Narrow tool sets reduce surface area for mistakes.
- **Documentation as code.** Each sub-agent's role is a versioned markdown file. Changing responsibilities means editing a file and committing — auditable, diffable.

## Consequences

**Positive:**
- One solo operator gets ~12-person-team coverage in decision-making quality.
- Work is traceable: every specialized task ran through a specific sub-agent with a specific prompt.
- Onboarding a real human to any role later is easier — the sub-agent definition is the job description.

**Negative:**
- The orchestrator must correctly route tasks. A misrouted task produces lower-quality output (e.g., `backend-engineer` doing `prompt-engineer`'s job).
- Cross-agent handoffs happen via the orchestrator, not direct. Some friction compared to two humans chatting.
- Sub-agents don't share context. The orchestrator must package enough context in each `Task` prompt. If it under-specifies, the sub-agent does wrong work.
- Sub-agent prompts will evolve. Every change needs to be committed and is effectively a team-process change.

## Alternatives considered

1. **Single all-purpose Claude session.** Rejected: context overload, role priorities conflict, no parallelism.
2. **Real 12-person team.** Rejected: not feasible for solo founder; moot here.
3. **Fewer, broader sub-agents (e.g., 4: PM, Engineer, DevOps, Data).** Rejected: loses specialization benefits — `scraping-engineer` and `prompt-engineer` think very differently and benefit from separate constraints.

## Revisit when

- A real human joins the project and replaces a sub-agent. Archive that sub-agent's file to `docs/archive/agents/` and update CLAUDE.md.
- Sub-agent output quality drops systematically for a role — revise the prompt, write a new ADR if the change is structural (e.g., splitting a role).
- Claude Code changes sub-agent mechanics materially (e.g., shared context, different dispatch model) — re-evaluate.
