# medusa-showcase

Medusa v2.19 backend + Next.js 16 storefront monorepo on Zerops (`nodejs@24`). App repo for the [Medusa recipe](https://app.zerops.io/recipes/medusa-showcase).

## Layout

| Path | `zeropsSetup` | Port | Notes |
| --- | --- | --- | --- |
| `backend/` | `medusa` / `medusa-stage` / `medusa-dev` | 9000 | Yarn 1, admin at `/app`; `*-dev` is idle (`zsc noop`) |
| `nextstore/` | `nextstore` / `nextstore-stage` / `nextstore-dev` | 8000 | Yarn 3 Berry; `*-dev` is idle |

Root [`zerops.yml`](zerops.yml). Local / Stage / Small / HA use `medusa` + `nextstore`. AI Agent / Remote use `medusadev` + `nextstoredev` and `medusastage` + `nextstorestage`. **Import YAMLs live in** [`zeropsio/recipes/medusa-showcase`](https://github.com/zeropsio/recipes/tree/main/medusa-showcase) — not in this repo.

## Siblings (Zerops project)

- `db` — PostgreSQL 17 — `DATABASE_URL`
- `redis` — Valkey 7.2 — `REDIS_URL`, cache/events/workflow/locking URLs
- `search` — Meilisearch — `MEILISEARCH_*` / `NEXT_PUBLIC_SEARCH_*`
- `storage` — MinIO — `MINIO_*` / `OBJECT_STORAGE_API_URL`
- `nextstore` — this repo, `nextstore` setup

## Dev commands

```bash
cd backend && yarn dev    # http://localhost:9000
cd nextstore && yarn dev    # http://localhost:8000
```

## Zerops ops

All platform operations go through Zerops MCP (`zcp`) tools — not raw `zcli`.

## Notes

- Pin `@medusajs/*` to **2.19.0** in `backend/`. Pin `@medusajs/js-sdk` / `@medusajs/types` to **2.19.0** in `nextstore/`.
- Project `RELOAD_SECRET` — medusa init POSTs nextstore `/api/internal/reload-env` after syncing publishable key.
- Value store: `APP_URL` / `API_URL` in import; map to framework keys in `zerops.yml` only.
- Analog storefront is a separate recipe — keep `ANALOG_STORE_URL` in backend CORS.
- Do not commit `.env`, `.env.local`, `.medusa/`, `.next/`.
