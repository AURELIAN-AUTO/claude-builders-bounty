# Next.js 15 + SQLite SaaS Template

> Opinionated, production-ready `CLAUDE.md` template for SaaS applications built with Next.js 15 App Router and SQLite (better-sqlite3 / Turso libSQL).

Built for **Issue #2** on [Claude Builders Bounty](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/2).

---

## What is this?

This template provides an authoritative, zero-clarification project manual (`CLAUDE.md`) that gives Claude Code (and other AI coding agents) complete architectural and convention context on a greenfield Next.js 15 + SQLite SaaS project.

## How to use

1. Copy [`CLAUDE.md`](./CLAUDE.md) into the root of your new Next.js SaaS project:
   ```bash
   cp templates/nextjs-sqlite/CLAUDE.md /path/to/my-saas/CLAUDE.md
   ```
2. Open Claude Code in your project directory:
   ```bash
   claude
   ```
3. Claude Code will automatically ingest `CLAUDE.md` and adhere to the project structure, SQLite PRAGMA rules, Server Component conventions, and anti-patterns without asking setup questions.

---

## Key Covered Pillars

- ✅ **Stack & Versions:** Next.js 15, React 19, TypeScript 5.6+, SQLite/Turso, Drizzle ORM.
- ✅ **Dev Commands:** One-line runnable scripts for migrations, studio, linting, and testing.
- ✅ **Folder Structure:** Route-grouped App Router architecture (`(auth)`, `(dashboard)`).
- ✅ **SQLite PRAGMAs:** Enforces `WAL` mode, foreign keys, and `busy_timeout`.
- ✅ **Component Patterns:** Server Components by default, minimal client leaves, Zod-validated Server Actions.
- ✅ **What We Don't Do (And Why):** 6 explicit anti-patterns with rationales (no raw string SQL, no float currency, etc.).
