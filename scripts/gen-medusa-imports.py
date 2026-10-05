#!/usr/bin/env python3
"""Generate Medusa recipe import YAMLs (vault + Mailpit + shared prod setups)."""

from pathlib import Path

RECIPES = Path("/Users/kristiyanvelkov/projects/zerops/recipes")
B2B_APP = Path("/Users/kristiyanvelkov/projects/zerops/medusa-b2b/.zerops-recipe")
DTC_APP = Path("/Users/kristiyanvelkov/projects/zerops/medusa-dtc/.zerops-recipe")

SENSITIVE = """
    COOKIE_SECRET:
      value: <@generateRandomString(<32>)>
      sensitive: true
    JWT_SECRET:
      value: <@generateRandomString(<32>)>
      sensitive: true
    SMTP_USER:
      value: ""
      sensitive: true
    SMTP_PASS:
      value: ""
      sensitive: true
    STRIPE_API_KEY:
      value: ""
      sensitive: true
    STRIPE_WEBHOOK_SECRET:
      value: ""
      sensitive: true
    RELOAD_SECRET:
      value: <@generateRandomString(<16>)>
      sensitive: true
    CHANNEL_PUBLISHABLE_KEY:
      value: ""
      sensitive: true"""

SHOWCASE_SENSITIVE_EXTRA = """
    GOOGLE_CLIENT_ID:
      value: ""
      sensitive: true
    GOOGLE_CLIENT_SECRET:
      value: ""
      sensitive: true
    GITHUB_CLIENT_ID:
      value: ""
      sensitive: true
    GITHUB_CLIENT_SECRET:
      value: ""
      sensitive: true
    POSTHOG_EVENTS_API_KEY:
      value: ""
      sensitive: true"""

SUPERADMIN = """    vault:
      SUPERADMIN_EMAIL: admin@example.com
      SUPERADMIN_PASSWORD:
        value: <@generateRandomString(<20>)>
        sensitive: true"""

MAILPIT = """
  - hostname: mailpit
    type: go@1
    buildFromGit: https://github.com/zerops-recipe-apps/mailpit-app
    enableSubdomainAccess: true
    priority: 10"""

SEARCH = """
  - hostname: search
    type: meilisearch@1.10
    enableSubdomainAccess: true
    priority: 10"""

SEARCH_HA = """
  # Single-node search — Meilisearch does not cluster on Zerops.
  # 1 GB floor absorbs a larger product index than the seed catalog.
  - hostname: search
    type: meilisearch@1.10
    enableSubdomainAccess: true
    priority: 10
    verticalAutoscaling:
      minRam: 1"""


def vault_urls(slug: str, kind: str, showcase: bool) -> str:
    if kind in ("agent", "remote"):
        app = f"https://nextstorestage-${{zeropsSubdomainHost}}-8000.prg1.zerops.app"
        api = f"https://medusastage-${{zeropsSubdomainHost}}-9000.prg1.zerops.app"
        dev_app = f"https://nextstoredev-${{zeropsSubdomainHost}}-8000.prg1.zerops.app"
        dev_api = f"https://medusadev-${{zeropsSubdomainHost}}-9000.prg1.zerops.app"
        medusa_host = "medusastage"
        nextstore_host = "nextstorestage"
    else:
        app = f"https://nextstore-${{zeropsSubdomainHost}}-8000.prg1.zerops.app"
        api = f"https://medusa-${{zeropsSubdomainHost}}-9000.prg1.zerops.app"
        dev_app = app
        dev_api = api
        medusa_host = "medusa"
        nextstore_host = "nextstore"

    search = f"https://search-${{zeropsSubdomainHost}}-7700.prg1.zerops.app"
    mailpit = kind in ("agent", "remote", "local")
    smtp_host = "mailpit" if mailpit else '""'
    smtp_port = '"1025"' if mailpit else '"587"'
    smtp_from = "medusa@localhost" if mailpit else '""'

    lines = [
        f"    APP_URL: {app}",
        f"    API_URL: {api}",
        f"    DEV_APP_URL: {dev_app}",
        f"    DEV_API_URL: {dev_api}",
        f"    SEARCH_URL: {search}",
        f"    MEDUSA_HOST: {medusa_host}",
        f"    NEXTSTORE_HOST: {nextstore_host}",
        f"    SMTP_HOST: {smtp_host}",
        f"    SMTP_PORT: {smtp_port}",
        f"    SMTP_FROM: {smtp_from}",
        '    SMTP_SECURE: "false"',
        '    STRIPE_PUBLISHABLE_KEY: ""',
    ]
    if showcase:
        lines.insert(4, f"    NEXT_STORE_URL: {app}")
        lines.insert(5, f"    MEDUSA_INSTANCE_URL: {api}")
        lines.append('    ANALOG_STORE_URL: ""')
        lines.append('    POSTHOG_HOST: ""')
    return "\n".join(lines)


def header(kind: str, name: str, showcase: bool) -> str:
    comments = {
        "agent": """# AI Agent environment — `*dev` workspaces plus `*stage`
# deploy targets that reuse the production `medusa` / `nextstore`
# setups. APP_URL / API_URL point at staged subdomains; DEV_* at
# the interactive medusadev / nextstoredev runtimes. Shared hobby
# data plane (one db / redis / search / storage) plus Mailpit.
#
# Project vault is the value store. Each app's zerops.yml maps:
#   APP_URL  → STOREFRONT_URL / NEXT_PUBLIC_BASE_URL / CORS
#   API_URL  → BACKEND_URL / ADMIN_CORS / MEDUSA_BACKEND_URL
#   SEARCH_URL → NEXT_PUBLIC_SEARCH_ENDPOINT
#   DEV_APP_URL / DEV_API_URL → workspace CORS + `yarn dev` URLs
#   MEDUSA_HOST / NEXTSTORE_HOST / CHANNEL_PUBLISHABLE_KEY →
#     hostname-agnostic publishable key + internal reload""",
        "remote": """# Remote (CDE) environment — same `*dev` + `*stage` pair as the
# agent project so a porter SSHs into medusadev / nextstoredev
# without a local data plane. `*stage` hostnames use the
# production `medusa` / `nextstore` setups. Mailpit for SMTP.
#
# Project vault is the value store. Each app's zerops.yml maps:
#   APP_URL  → STOREFRONT_URL / NEXT_PUBLIC_BASE_URL / CORS
#   API_URL  → BACKEND_URL / ADMIN_CORS / MEDUSA_BACKEND_URL
#   SEARCH_URL → NEXT_PUBLIC_SEARCH_ENDPOINT
#   DEV_APP_URL / DEV_API_URL → workspace CORS + `yarn dev` URLs
#   MEDUSA_HOST / NEXTSTORE_HOST / CHANNEL_PUBLISHABLE_KEY →
#     hostname-agnostic publishable key + internal reload""",
        "local": """# Local environment — staged production apps plus the managed
# data plane and Mailpit. Point a laptop `yarn develop` at db /
# redis / search / storage over zCLI VPN, or use the subdomain
# apps as the preview.
#
# Project vault is the value store. Each app's zerops.yml maps:
#   APP_URL  → STOREFRONT_URL / NEXT_PUBLIC_BASE_URL / CORS
#   API_URL  → BACKEND_URL / ADMIN_CORS / MEDUSA_BACKEND_URL
#   SEARCH_URL → NEXT_PUBLIC_SEARCH_ENDPOINT
#   MEDUSA_HOST / NEXTSTORE_HOST / CHANNEL_PUBLISHABLE_KEY →
#     hostname-agnostic publishable key + internal reload""",
        "stage": """# Stage environment — same topology as Small Production on cheaper
# data profiles (hobby Postgres + hobby Valkey). One container per
# app; app RAM stays at the Medusa / Next.js floors so QA does not
# OOM while still costing less than oltp-staging entry prod.
#
# Project vault is the value store. Each app's zerops.yml maps:
#   APP_URL  → STOREFRONT_URL / NEXT_PUBLIC_BASE_URL / CORS
#   API_URL  → BACKEND_URL / ADMIN_CORS / MEDUSA_BACKEND_URL
#   SEARCH_URL → NEXT_PUBLIC_SEARCH_ENDPOINT
#   MEDUSA_HOST / NEXTSTORE_HOST / CHANNEL_PUBLISHABLE_KEY →
#     hostname-agnostic publishable key + internal reload""",
        "small": """# Small Production — entry prod (~5 users). Postgres oltp-staging
# and Valkey staging (not hobby). Omit minContainers (default 1).
# App verticalAutoscaling is a documented exception: Medusa admin
# OOMs at the Node platform default (0.25 GB); floors come from
# research.md § Scaling.
#
# Project vault is the value store. Each app's zerops.yml maps:
#   APP_URL  → STOREFRONT_URL / NEXT_PUBLIC_BASE_URL / CORS
#   API_URL  → BACKEND_URL / ADMIN_CORS / MEDUSA_BACKEND_URL
#   SEARCH_URL → NEXT_PUBLIC_SEARCH_ENDPOINT
#   MEDUSA_HOST / NEXTSTORE_HOST / CHANNEL_PUBLISHABLE_KEY →
#     hostname-agnostic publishable key + internal reload""",
        "ha": """# Highly-available production — SERIOUS core required for `:ha@`
# managed services. Demo DB stays oltp-staging (not oltp-production
# ~4 GB). Meilisearch has no HA type — one search node. Shared CPU
# on the apps keeps the HA demo below dedicated-core showcase cost.
#
# Project vault is the value store. Each app's zerops.yml maps:
#   APP_URL  → STOREFRONT_URL / NEXT_PUBLIC_BASE_URL / CORS
#   API_URL  → BACKEND_URL / ADMIN_CORS / MEDUSA_BACKEND_URL
#   SEARCH_URL → NEXT_PUBLIC_SEARCH_ENDPOINT
#   MEDUSA_HOST / NEXTSTORE_HOST / CHANNEL_PUBLISHABLE_KEY →
#     hostname-agnostic publishable key + internal reload""",
    }
    extra = (
        "# Aliases NEXT_STORE_URL / MEDUSA_INSTANCE_URL match older recipe buttons.\n"
        if showcase
        else ""
    )
    core = "  corePackage: SERIOUS\n" if kind == "ha" else ""
    return f"""#zeropsPreprocessor=on
# yaml-language-server: $schema=https://api.app-prg1.zerops.io/api/rest/public/settings/import-project-yaml-json-schema.json

{comments[kind]}
{extra}project:
  name: {name}
{core}  vault:
"""


def data_plane(kind: str) -> str:
    if kind == "ha":
        db = """  - hostname: db
    type: postgresql:ha@17
    profile: oltp-staging
    priority: 10

  # HA Valkey — 3-node cluster; client ports stay on hostname
  # `redis` through failover. Profile only (no duplicate autoscaling).
  - hostname: redis
    type: valkey:ha@7.2
    profile: staging
    priority: 10"""
        storage_size = 10
        search = SEARCH_HA
    elif kind == "small":
        db = """  - hostname: db
    type: postgresql:single@17
    profile: oltp-staging
    priority: 10

  - hostname: redis
    type: valkey:single@7.2
    profile: staging
    priority: 10"""
        storage_size = 2
        search = SEARCH
    elif kind == "stage":
        db = """  - hostname: db
    type: postgresql:single@17
    # Rehearsal — oltp-hobby (~0.5 GB), lighter than small prod.
    profile: oltp-hobby
    priority: 10

  - hostname: redis
    type: valkey:single@7.2
    profile: hobby
    priority: 10"""
        storage_size = 2
        search = SEARCH
    else:
        db = """  - hostname: db
    type: postgresql:single@17
    profile: oltp-hobby
    priority: 10

  - hostname: redis
    type: valkey:single@7.2
    profile: hobby
    priority: 10"""
        storage_size = 2
        search = SEARCH

    mailpit = MAILPIT if kind in ("agent", "remote", "local") else ""
    return f"""{db}
{search}

  - hostname: storage
    type: object-storage
    objectStorageSize: {storage_size}
    objectStoragePolicy: public-read
    priority: 10
{mailpit}"""


def apps(kind: str, backend_git: str, frontend_git: str) -> str:
    ha = kind == "ha"
    medusa_min = """    verticalAutoscaling:
      minRam: 1
      minFreeRamGB: 0.5"""
    next_min = """    verticalAutoscaling:
      minRam: 0.5
      minFreeRamGB: 0.25"""
    ha_medusa = "    minContainers: 2\n" if ha else ""
    ha_next = "    minContainers: 2\n" if ha else ""

    if kind in ("agent", "remote"):
        return f"""
  # Idle workspace — deploy `./`, SSH in and run `yarn dev`.
  - hostname: medusadev
    type: nodejs@24
    priority: 6
    zeropsSetup: dev
    buildFromGit: {backend_git}
    enableSubdomainAccess: true
    verticalAutoscaling:
      minRam: 1

  # Staged prod setup. Seeds project CHANNEL_PUBLISHABLE_KEY for nextstorestage.
  - hostname: medusastage
    type: nodejs@24
    priority: 6
    zeropsSetup: prod
    buildFromGit: {backend_git}
    enableSubdomainAccess: true
    envIsolation: service service@nextstorestage service@nextstoredev
{SUPERADMIN}
{medusa_min}

  - hostname: nextstoredev
    type: nodejs@24
    priority: 5
    zeropsSetup: dev
    buildFromGit: {frontend_git}
    enableSubdomainAccess: true
    verticalAutoscaling:
      minRam: 1

  - hostname: nextstorestage
    type: nodejs@24
    priority: 5
    zeropsSetup: prod
    buildFromGit: {frontend_git}
    enableSubdomainAccess: true
{next_min}
"""

    floor_comment = (
        "  # Framework floor — not a hello-world platform default.\n"
        if kind == "small"
        else "  # Two backend replicas so rolling deploys keep /health and /app\n  # up. Shared CPU; RAM stays at the Medusa floor.\n"
        if ha
        else ""
    )
    return f"""
{floor_comment}  - hostname: medusa
    type: nodejs@24
    priority: 6
    zeropsSetup: prod
    buildFromGit: {backend_git}
    enableSubdomainAccess: true
{ha_medusa}    envIsolation: service service@nextstore
{SUPERADMIN}
{medusa_min}

  - hostname: nextstore
    type: nodejs@24
    priority: 5
    zeropsSetup: prod
    buildFromGit: {frontend_git}
    enableSubdomainAccess: true
{ha_next}{next_min}
"""


SPECS = {
    "showcase": {
        "git": "https://github.com/zerops-recipe-apps/medusa-showcase",
        "frontend_git": "https://github.com/zerops-recipe-apps/medusa-showcase-frontend",
        "names": {
            "agent": "medusa-showcase-agent",
            "remote": "medusa-showcase-remote",
            "local": "medusa-showcase-local",
            "stage": "medusa-showcase-stage",
            "small": "medusa-showcase-small-prod",
            "ha": "medusa-showcase-ha-prod",
        },
        "dirs": {
            "agent": "0 — AI Agent",
            "remote": "1 — Remote (CDE)",
            "local": "2 — Local",
            "stage": "3 — Stage",
            "small": "4 — Small Production",
            "ha": "5 — Highly-available Production",
        },
        "roots": [RECIPES / "medusa-showcase"],
        "showcase": True,
    },
    "b2b": {
        "git": "https://github.com/zerops-recipe-apps/medusa-b2b",
        "frontend_git": "https://github.com/zerops-recipe-apps/medusa-b2b-frontend",
        "names": {
            "agent": "medusa-b2b-agent",
            "remote": "medusa-b2b-remote",
            "local": "medusa-b2b-local",
            "stage": "medusa-b2b-stage",
            "small": "medusa-b2b-small-prod",
            "ha": "medusa-b2b-ha-prod",
        },
        "dirs": {
            "agent": "0 — AI Agent",
            "remote": "1 — Remote (CDE)",
            "local": "2 — Local",
            "stage": "3 — Stage",
            "small": "4 — Small Production",
            "ha": "5 — Highly-available Production",
        },
        "roots": [RECIPES / "medusa-b2b", B2B_APP],
        "showcase": False,
    },
    "dtc": {
        "git": "https://github.com/zerops-recipe-apps/medusa-dtc",
        "frontend_git": "https://github.com/zerops-recipe-apps/medusa-dtc-frontend",
        "names": {
            "agent": "medusa-dtc-agent",
            "remote": "medusa-dtc-remote",
            "local": "medusa-dtc-local",
            "stage": "medusa-dtc-stage",
            "small": "medusa-dtc-small-prod",
            "ha": "medusa-dtc-ha-prod",
        },
        "dirs": {
            "agent": "0 — AI Agent",
            "remote": "1 — Remote (CDE)",
            "local": "2 — Local",
            "stage": "3 — Stage",
            "small": "4 — Small Production",
            "ha": "5 — Highly-available Production",
        },
        "roots": [RECIPES / "medusa-dtc", DTC_APP],
        "showcase": False,
    },
}


def render(spec: dict, kind: str) -> str:
    showcase = spec["showcase"]
    sensitive = SENSITIVE + (SHOWCASE_SENSITIVE_EXTRA if showcase else "")
    return (
        header(kind, spec["names"][kind], showcase)
        + vault_urls(spec["names"][kind], kind, showcase)
        + sensitive
        + "\n\nservices:\n"
        + data_plane(kind)
        + apps(kind, spec["git"], spec["frontend_git"])
    )


def main() -> None:
    written = []
    for spec in SPECS.values():
        for kind, folder in spec["dirs"].items():
            body = render(spec, kind)
            for root in spec["roots"]:
                dest = root / folder / "import.yaml"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(body)
                written.append(str(dest))
    print("\n".join(written))


if __name__ == "__main__":
    main()
