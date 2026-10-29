# Detection heuristics — signals → tiers, and the edge vocabulary

Use these to turn a token-budgeted scan (file tree + manifests + entry points) into the intermediate model. Match on the *cheap* signals first (manifest dependency names, config filenames, directory names); only open a source file when you need to confirm a wiring (a route, a DB client, an outbound call).

## Frameworks → layer

| Layer | Signals (deps / files / dirs) |
|---|---|
| **frontend** | `react`, `vue`, `svelte`, `@angular/*`, `solid-js` in package.json; `vite.config.*`, `next.config.*`, `nuxt.config.*`, `astro.config.*`, `angular.json`; `src/components`, `src/routes`, `src/pages`, `public/index.html`, `index.html` + a bundler; Tailwind/CSS config |
| **backend** | `fastapi`/`flask`/`django`/`starlette`/`uvicorn` (Python); `express`/`koa`/`fastify`/`@nestjs/*`/`hapi` (Node); `gin`/`echo`/`fiber`/`net/http` (Go); `actix`/`axum`/`rocket` (Rust); `spring-boot` (Java); `rails`/`sinatra` (Ruby); `laravel`/`symfony` (PHP); dirs like `app/`, `api/`, `routes/`, `controllers/`, `services/`, `handlers/`, `cmd/` |
| **data** | `postgres`/`pg`/`psycopg`/`asyncpg`, `mysql`, `sqlite`, `mongodb`/`mongoose`, `redis`/`ioredis`, `prisma` (`schema.prisma`), `sqlalchemy`/`alembic`, `drizzle`, `typeorm`, `supabase`; `docker-compose.yml` services named db/postgres/redis/mongo; `*.sql`, `migrations/` |
| **external** | HTTP/SDK clients to third parties: `@anthropic-ai/sdk`/`anthropic`, `openai`, `stripe`, `twilio`, `@aws-sdk/*`/`boto3`, `googleapis`, `sendgrid`, `axios`/`httpx`/`requests`/`fetch` calling a non-local base URL; `.env.example` keys like `*_API_KEY`, `*_BASE_URL` |
| **mcp** | `@modelcontextprotocol/sdk`, `mcp`/`fastmcp` (Python), a `Server(...)`/`FastMCP(...)` entry, an `mcp.json` / server manifest, tool/`@tool` registrations, a `tools/` dir exposed over MCP |
| **infra / queue** (optional tier) | `celery`, `bullmq`, `sidekiq`, `rabbitmq`/`amqp`, `kafka`, cron/worker entrypoints, `*.tf`, k8s manifests — model as a `backend`-tinted container or its own node only if it matters to the story |

A monorepo can have several frontend/backend containers (e.g. `apps/web`, `apps/admin`, `services/api`). Use the workspace layout (`pnpm-workspace.yaml`, `turbo.json`, `apps/`, `packages/`, `services/`) to split containers.

## Components inside a container — group by responsibility
Read the container's top-level dirs and name a chip per responsibility, not per file:
- frontend: **Routes/Pages**, **Stores/State**, **Hooks**, **API client**, **UI components**, **Auth**.
- backend: **Routes/Controllers** (`/api/...`), **Services/Use-cases**, **Auth/Middleware**, **Models/ORM**, **Schemas/DTOs**, **Workers/Jobs**, **Config**.
- mcp server: **Tools**, **Resources**, **Prompts**, **Transport**.
Put the real glob/paths in each chip's `data-files`.

## Edges — find real relationships, label with the protocol
Only draw an edge you can point at in the code. Common ones and where they show up:

| Edge | How to detect | Label |
|---|---|---|
| frontend → backend | API client base URL, `fetch`/`axios` to `/api`, generated client, proxy config | `HTTP` / `REST` / `GraphQL` |
| frontend ↔ backend (live) | `socket.io`, `WebSocket`, SSE endpoint | `WebSocket` / `SSE` |
| backend → database | ORM/driver init, model definitions, repository/DAO calls | `SQL` / `query` |
| backend → cache/queue | redis client, queue producer/consumer | `cache` / `queue` |
| backend → external | third-party SDK/client call site | `HTTPS` / `calls` |
| backend → MCP server | MCP client/transport wiring | `MCP` |
| service ↔ service | inter-service HTTP/gRPC, shared bus | `HTTP` / `gRPC` / `events` |
| module → module | a meaningful cross-package import (only if it tells the story) | `import` |

`from`/`to` can be a container id (whole-tier relationship) or a specific component/node id (e.g. `cmp-services → n-postgres`) when you know the exact owner of the call. Prefer the specific component when the code makes it clear; fall back to the container when it doesn't.

## Keep it honest and readable
- 3–7 containers, a readable handful of edges. This is the Container level, not a function call graph.
- If you can't tell whether an edge exists, leave it out and say so at the review gate — don't guess a wire.
- If detection is ambiguous (e.g. a dir that could be frontend or backend), surface the question at the review gate rather than silently picking.
