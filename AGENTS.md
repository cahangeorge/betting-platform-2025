# Agent Instructions — `bet` workspace

Multi-project monorepo for football/sports betting analytics. Five independent sub-projects (separate venvs, separate package managers), but `betfront` orchestrates Python bridges at fixed paths.

**Default target: `betfront/`.** `frontbet/` is a distinct pre-existing project — do not touch unless explicitly told to.

## Sub-projects

| Project | Stack | Role | Install | Test |
|---|---|---|---|---|
| [betfront/](betfront/README.md) | Node >=22.12, pnpm, Astro 6 + React 19, Prisma + SQLite | Web UI + Python bridge orchestrator | `pnpm install && pnpm db:push` | `pnpm test` (Vitest) |
| [OddsHarvester/](OddsHarvester/CLAUDE.md) | Python >=3.12, uv, Playwright | CLI scraper for OddsPortal.com | `uv sync && uv run playwright install chromium` | `uv run pytest tests/ -q` |
| [penaltyblog/](penaltyblog/README.md) | Python >=3.10, setuptools + Cython | Football predictive models, scrapers, ratings | `pip install -e .` | `pytest` or `make test` |
| [soccerdata/](soccerdata/README.rst) | Python >=3.10, uv, Selenium | Multi-source football data scrapers | `uv sync` | `make test` |
| [flumine/](flumine/README.md) | Python >=3.9, pip | Betfair/Betdaq trading framework (standalone, not wired into betfront) | `pip install -e .` | `pytest` |

## `betfront` — commands & quirks

All `db:*` / `worker` scripts require `dotenv -e .env --` — `.env` is **not auto-loaded** by Prisma or tsx.

| Command | What |
|---|---|
| `pnpm dev` | `astro dev` on `0.0.0.0:3000` |
| `pnpm test` | `vitest run` (jsdom, no globals, pattern `src/**/*.test.{ts,tsx}`) |
| `pnpm test:watch` | `vitest` (interactive) |
| `pnpm test:e2e` | Playwright (Chromium, port 3100, fresh `e2e.db`) |
| `pnpm db:push` | Prisma schema → SQLite |
| `pnpm db:migrate` | Prisma migration dev |
| `pnpm worker` | Scheduled jobs runner (`src/server/jobs/worker.ts`) |

**Vitest**: env `jsdom`, `globals: false` (import `describe`/`it`/`expect`), alias `#` → `src/`.

**Playwright E2E**: tests in `tests/e2e/`, global setup wipes `prisma/e2e.db`, spins Astro on port 3100 with `ALLOW_DEV_USER=0` and `DATABASE_URL=file:./e2e.db`. Single worker, non-parallel, `reuseExistingServer: false`.

**Astro SSR**: output `server`, adapter `node/standalone`. Native modules (`better-sqlite3`, `@prisma/client`, `@prisma/adapter-better-sqlite3`) are `ssr.external` — must not be bundled.

**Prisma**: client output at `src/generated/prisma` (not default `node_modules/.prisma`).

**No lint script** defined in package.json. **No CI** workflows for betfront.

**Prediction engine** at `src/server/predict/` — has unit tests in `engine.test.ts`. Target modes: `future` (upcoming unplayed matches), `history` (backtest on past results), `matches` (specific IDs).

**Client actions** (Astro server actions): `src/lib/client-actions/` — jobs, account, soccerdata, penaltyblog, scraper, predictions, tickets, datasets. Not code-generated.

**Python bridges** (`src/server/penaltyblog.ts` etc.) resolve sibling venvs at hardcoded relative paths:
`../OddsHarvester/.venv`, `../penaltyblog/.venv`, `../soccerdata/.venv`. Renaming/moving a project breaks bridges.

## Lint / format per project

| Project | Command |
|---|---|
| betfront | (none defined; no lint script in package.json) |
| OddsHarvester | `uv run ruff format . && uv run ruff check --fix src/` |
| penaltyblog | `black .` |
| soccerdata | `make format && make lint && make mypy` |
| flumine | `black .` |

## Cross-project dataflow

```
soccerdata ──┐
             ├──► betfront (SQLite via Prisma) ──► UI / predictions
OddsHarvester┘                  ▲
                                │
penaltyblog (models) ───────────┘   (invoked via Python bridge from betfront)

flumine — standalone trading framework (not wired into betfront)
```

## Key constraints

- **One project at a time.** `cd` into the sub-project before running install/test/lint. Never install at root.
- **Do not unify package managers.** Each project uses its own (pnpm, uv, pip, setuptools). Use the right tool per project table.
- **Network scrapers** (OddsHarvester, soccerdata, penaltyblog/scrapers) hit live sites. Prefer mocked/VCR unit tests. Integration tests break on upstream HTML changes — fix selectors, do not skip.
- **Cython** in penaltyblog: rebuild after edits via `pip install -e .`.
- **Secrets** never commit: Betfair creds (flumine), `DATABASE_URL` (betfront), StatsBomb/Opta keys (penaltyblog). Cache dir: `SOCCERDATA_DIR` (soccerdata).
- **No monorepo CI** — each project has its own `.github/workflows/`.
- **OddsHarvester** has its own [CLAUDE.md](OddsHarvester/CLAUDE.md) with detailed architecture and release process — read before modifying.
