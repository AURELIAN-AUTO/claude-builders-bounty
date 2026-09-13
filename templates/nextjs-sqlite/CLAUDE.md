# CLAUDE.md — Next.js 15 + SQLite SaaS Template

This repository is a production SaaS application built with **Next.js 15 (App Router)** and **SQLite (better-sqlite3 / Turso libSQL)** with **Drizzle ORM**.

---

## 1. Stack & Versions

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | Next.js (App Router) | `15.1.x` | React 19 Server Components, Server Actions |
| **Language** | TypeScript | `5.6.x` | Strict type safety (`strict: true`) |
| **Database** | SQLite / Turso libSQL | `@libsql/client` / `better-sqlite3` | Zero-latency embedded or edge SQL |
| **ORM** | Drizzle ORM | `drizzle-orm 0.38+` | Lightweight, zero-overhead type-safe SQL |
| **Migrations** | Drizzle Kit | `drizzle-kit 0.30+` | Declarative SQL migration generator |
| **Styling** | Tailwind CSS | `v4.x` | Modern utility styling |
| **Validation** | Zod | `3.23.x` | Schema validation for all inputs and actions |
| **Package Mgr**| pnpm | `9.x` | Deterministic, fast workspace package manager |

---

## 2. Dev Commands

```bash
# Development
pnpm install                 # Install dependencies
pnpm dev                     # Start development server at http://localhost:3000
pnpm build                   # Production build
pnpm start                   # Start production server
pnpm lint                    # ESLint check
pnpm typecheck               # Run tsc --noEmit

# Database & Migrations
pnpm db:generate             # Generate SQL migrations from src/db/schema.ts
pnpm db:migrate              # Apply pending migrations to local SQLite database
pnpm db:push                 # Push schema changes directly (dev prototyping only)
pnpm db:studio               # Launch Drizzle Studio UI at https://local.drizzle.team
pnpm db:seed                 # Run local database seed script (src/db/seed.ts)
```

---

## 3. Project & Folder Structure

```
my-saas-app/
├── CLAUDE.md                        # This project guide (authoritative context)
├── drizzle.config.ts                # Drizzle configuration
├── next.config.ts                   # Next.js 15 configuration
├── package.json
├── tsconfig.json
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── (auth)/                  # Auth route group: login, signup, reset-password
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── (dashboard)/             # Protected dashboard route group
│   │   │   ├── layout.tsx           # Dashboard shell with sidebar and user menu
│   │   │   ├── page.tsx             # Dashboard home
│   │   │   └── settings/page.tsx    # Org & account settings
│   │   ├── api/                     # Webhook endpoints (e.g. Stripe webhooks)
│   │   │   └── webhooks/stripe/route.ts
│   │   ├── layout.tsx               # Root HTML layout with providers
│   │   └── page.tsx                 # Public marketing landing page
│   ├── components/
│   │   ├── ui/                      # Primitive design components (Button, Input, Card)
│   │   └── features/                # Domain-specific components (BillingCard, UserTable)
│   ├── db/                          # Database layer
│   │   ├── index.ts                 # Database client singleton with connection pooling
│   │   ├── schema.ts                # Authoritative Drizzle schema definitions
│   │   ├── migrations/              # Generated SQL migrations (never edit manually)
│   │   └── seed.ts                  # Development seed data
│   ├── actions/                     # Server Actions (collocated business logic)
│   │   ├── auth.ts                  # Authentication mutations
│   │   ├── organization.ts          # Org & member management
│   │   └── billing.ts               # Stripe subscription & checkout mutations
│   └── lib/                         # Shared utilities
│       ├── auth.ts                  # Session resolution & auth guards
│       ├── safe-action.ts           # Type-safe Server Action wrapper with Zod
│       └── utils.ts                 # Classname merge (cn) and formatting helpers
```

---

## 4. SQL & Migration Conventions

### 4.1 SQLite PRAGMAs (Mandatory Initialization)
Every SQLite connection **must** execute the following PRAGMAs upon connection in `src/db/index.ts`:

```typescript
// Enforce WAL mode and foreign key constraints
db.run(sql`PRAGMA journal_mode = WAL;`);
db.run(sql`PRAGMA foreign_keys = ON;`);
db.run(sql`PRAGMA busy_timeout = 5000;`);
db.run(sql`PRAGMA synchronous = NORMAL;`);
```

* **`journal_mode = WAL`**: Allows concurrent readers and single writer without blocking.
* **`foreign_keys = ON`**: SQLite disables foreign key enforcement by default; this ensures referential integrity.
* **`busy_timeout = 5000`**: Retries for up to 5 seconds if a write lock is active instead of immediately throwing `SQLITE_BUSY`.

### 4.2 Schema Conventions (`src/db/schema.ts`)
1. **Primary Keys**: Always use string UUIDs (`text('id').primaryKey().$defaultFn(() => crypto.randomUUID())`).
2. **Timestamps**: Always define `createdAt` and `updatedAt` in integer milliseconds or ISO8601 UTC strings (`integer('created_at', { mode: 'timestamp_ms' })`).
3. **Monetary Values**: Never store currency as floats. Always store in integer minor units (e.g. cents, pence) as `integer('amount_cents').notNull()`.
4. **Indexes**: Every foreign key column (`user_id`, `org_id`) must have an explicit index defined.

---

## 5. Component & Architecture Patterns

### 5.1 Server Components by Default
* All components in `src/app/` are **Server Components** by default.
* Fetch data directly in Server Components using async/await and Drizzle queries:
  ```typescript
  // src/app/(dashboard)/page.tsx
  export default async function DashboardPage() {
    const session = await auth();
    const org = await db.query.organizations.findFirst({
      where: eq(organizations.id, session.orgId),
    });
    return <DashboardView org={org} />;
  }
  ```

### 5.2 Client Components
* Use `"use client"` **only** at the interactive leaves of the component tree (e.g., a modal trigger, an interactive form, a dropdown toggle).
* Never make an entire page or layout a Client Component.

### 5.3 Server Actions with Zod Validation
* Every mutation must be a Server Action wrapped with input validation:
  ```typescript
  "use server";

  import { z } from "zod";
  import { db } from "@/db";
  import { organizations } from "@/db/schema";
  import { auth } from "@/lib/auth";

  const UpdateOrgSchema = z.object({
    name: z.string().min(2).max(50),
  });

  export async function updateOrganization(formData: unknown) {
    const session = await auth();
    if (!session) throw new Error("Unauthorized");

    const validated = UpdateOrgSchema.parse(formData);
    await db.update(organizations)
      .set({ name: validated.name, updatedAt: new Date() })
      .where(eq(organizations.id, session.orgId));
  }
  ```

---

## 6. What We Don't Do (And Why)

1. **❌ NO Raw String SQL Interpolation**
   * *Rule:* Never use template string interpolation in queries: `db.run(`SELECT * FROM users WHERE id = '${id}'`)`.
   * *Why:* Critical SQL injection vulnerability. Always use Drizzle query builders or parameterized `sql` tag: `sql`SELECT * FROM users WHERE id = ${id}``.

2. **❌ NO Heavy ORM Runtimes (e.g., Prisma with binary engine)**
   * *Rule:* We use Drizzle ORM exclusively.
   * *Why:* Heavy binary query engines introduce cold-start latency in serverless edge deployments and cause file-lock conflicts with SQLite.

3. **❌ NO Client-Side Direct Database Access**
   * *Rule:* Never import `@/db` in files with `"use client"`.
   * *Why:* Database connection credentials, file handles, and schema internals must never leak to the browser bundle.

4. **❌ NO Floating Point Numbers for Financial Calculations**
   * *Rule:* Store all prices, billing items, and ledger balances in integer cents (`amount_cents: integer`).
   * *Why:* Floating point math (`0.1 + 0.2 = 0.30000000000000004`) causes rounding drift and billing discrepancies.

5. **❌ NO Default Component Exports**
   * *Rule:* Use named exports for all components and utility functions: `export function UserCard()`. (Pages and layouts are the only exception where Next.js requires `export default`).
   * *Why:* Named exports ensure consistent refactoring, auto-import discovery, and prevent re-export naming drift.

6. **❌ NO `useEffect` for Data Fetching**
   * *Rule:* Never use `useEffect` + `fetch()` to load page data.
   * *Why:* Introduces client waterfall requests and layout shift. Load data on the server in Server Components.

---

## 7. Operational Guidelines for Claude Code

When writing or modifying code in this codebase:
1. Always check `src/db/schema.ts` before writing queries to ensure column names and types match.
2. If schema changes are needed, update `src/db/schema.ts`, run `pnpm db:generate`, and verify the resulting SQL migration.
3. Keep changes minimal and isolated; do not refactor unrelated files.
4. Ensure all newly introduced Server Actions include explicit Zod input validation and auth checks.
