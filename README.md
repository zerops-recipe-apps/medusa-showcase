# Medusa Showcase Recipe App

<!-- #ZEROPS_EXTRACT_START:intro# -->
[Medusa](https://medusajs.com) v2.19 showcase API and admin at the repository root — B2C and B2B sales channels, Meilisearch indexing, optional OAuth and analytics hooks. Pairs with [medusa-showcase-frontend](https://github.com/zerops-recipe-apps/medusa-showcase-frontend). First deploy migrates, seeds demo data, and writes a publishable key the storefront reads at runtime. Part of the [Medusa Showcase recipe](https://app.zerops.io/recipes/medusa-showcase) on [Zerops](https://zerops.io).
<!-- #ZEROPS_EXTRACT_END:intro# -->

Used within [Medusa Showcase recipe](https://app.zerops.io/recipes/medusa-showcase) for the Zerops platform.

⬇️ **Full recipe page and deploy with one-click**

[![Deploy on Zerops](https://github.com/zeropsio/recipe-shared-assets/blob/main/deploy-button/light/deploy-button.svg)](https://app.zerops.io/recipes/medusa-showcase?environment=small-production)

![cover](https://github.com/zeropsio/recipe-shared-assets/blob/main/covers/svg/cover-nextjs.svg)

## Repositories

| Repo | Role |
| --- | --- |
| [medusa-showcase](https://github.com/zerops-recipe-apps/medusa-showcase) (this repo) | Medusa backend + admin (`/app`) |
| [medusa-showcase-frontend](https://github.com/zerops-recipe-apps/medusa-showcase-frontend) | Optional Next.js storefront |

This repository is **backend only** (no `backend/` or `nextstore/` folders). Optional `ANALOG_STORE_URL` in CORS supports a separate Analog storefront recipe.

Imports: [`zeropsio/recipes/medusa-showcase`](https://github.com/zeropsio/recipes/tree/main/medusa-showcase) and [`.zerops-recipe/`](.zerops-recipe/).

## Local development

```bash
yarn install
cp .env.template .env
yarn dev                # http://localhost:9000 — admin at /app
```

Optional storefront:

```bash
cd ../medusa-showcase-frontend
cp .env.template .env.local
yarn install && yarn dev   # http://localhost:8000
```

## Integration Guide

<!-- #ZEROPS_EXTRACT_START:integration-guide# -->

### 1. Adding `zerops.yml`

`prod` copies seed assets into `.medusa/server` when present; `dev` deploys the full tree for git-connected agents.

```yaml
zerops:
  - setup: prod
    build:
      base: nodejs@24
      buildCommands:
        - yarn
        - yarn build
        - cp -f package.json tsconfig.json .medusa/server/
        # showcase: optional seed-files copy — see zerops.yml in this repo
      deployFiles:
        - .medusa/server/~
        - ~node_modules
    run:
      initCommands:
        - zsc execOnce ${appVersionId}_migration -- yarn migrate
        - yarn setInitialPublishableKey
        - yarn reloadNextstoreEnv
        # … superadmin, seed, search index — see zerops.yml
      ports:
        - port: 9000
          httpSupport: true

  - setup: dev
    build:
      deployFiles: ./
```

Meilisearch is an in-repo module (not the Rok Mohar plugin). OAuth/PostHog keys live in the project vault on recipe imports.

<!-- #ZEROPS_EXTRACT_END:integration-guide# -->
