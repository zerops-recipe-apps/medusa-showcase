# medusa-showcase

Medusa v2.19 **backend** on Zerops (`nodejs@24`). Storefront: [medusa-showcase-nextstore](https://github.com/zerops-recipe-apps/medusa-showcase-nextstore).

## Layout

| Path | Zerops | Port |
| --- | --- | --- |
| `backend/` | `dev` / `prod` | 9000 |
| `nextstore/` | local compose only | 8000 |

Root [`zerops.yml`](zerops.yml) — only `dev` and `prod`. Imports: [`.zerops-recipe/`](.zerops-recipe/) and [`zeropsio/recipes/medusa-showcase`](https://github.com/zeropsio/recipes/tree/main/medusa-showcase).

## Notes

- Pin `@medusajs/*` to **2.19.0**.
- Project **vault**; OAuth / PostHog keys in import `vault` where needed.
- Analog storefront is a separate recipe — keep `ANALOG_STORE_URL` in backend CORS.
- No Turbo/Nx. `dev` deploys `./`; `prod` flattens `backend/.medusa/server`.
