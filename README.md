# Medusa Showcase (backend)

<!-- #ZEROPS_EXTRACT_START:intro# -->
Medusa v2.19 backend and admin on [Zerops](https://zerops.io). Storefront: [medusa-showcase-nextstore](https://github.com/zerops-recipe-apps/medusa-showcase-nextstore). PostgreSQL, Valkey, Meilisearch, MinIO, Mailpit on dev envs.
<!-- #ZEROPS_EXTRACT_END:intro# -->

## Repos

| Repo | Role |
| --- | --- |
| **This repo** | Medusa API + admin (`zerops.yml` → `dev` / `prod`) |
| [medusa-showcase-nextstore](https://github.com/zerops-recipe-apps/medusa-showcase-nextstore) | Next.js 16 storefront |

[`nextstore/`](nextstore/) is for **local dev** only.

Imports: [`.zerops-recipe/`](.zerops-recipe/) and [`zeropsio/recipes/medusa-showcase`](https://github.com/zeropsio/recipes/tree/main/medusa-showcase).

## Local dev

```bash
cd backend && yarn dev
cd nextstore && yarn dev
```
