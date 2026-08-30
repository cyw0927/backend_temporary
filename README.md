# Cat Game Backend MVP

FastAPI + PostgreSQL + SQLAlchemy backend for the cat-game learning MVP.

## Implemented vertical slice

- `GET /health` and `GET /health/db`
- `GET /users/{user_id}`
- `GET /tasks` and `GET /tasks/{task_id}`
- `POST /tasks/{task_id}/submissions` -> creates `PENDING` attempt and returns HTTP 202
- `GET /attempts/{attempt_id}` -> polling endpoint
- correct attempts award the task's configured `reward_amount` once via `reward_ledger`
- `GET /shop/items`
- `POST /shop/items/{item_id}/purchase` -> atomic conditional balance deduction + inventory update
- `GET /users/{user_id}/housing`
- `PUT /users/{user_id}/housing/{slot}` -> only owned `furniture` items may be equipped

Prices and reward amounts are data stored on tasks/items. This repository does not invent product-policy values for them.

## Windows PowerShell local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Create a PostgreSQL database matching `DATABASE_URL` in `.env` (the example expects database `cat_game`), then run:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Useful URLs:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/health/db`
- `http://127.0.0.1:8000/docs`

Run tests:

```powershell
pytest -q
```

The tests use SQLite and do not require PostgreSQL or Docker.

## Grading boundary

The HTTP contract is asynchronous: submission commits a `PENDING` attempt first and returns 202, then a FastAPI background task grades it using a fresh DB session. No DB transaction is held while an external evaluator would run.

For this MVP, `DeterministicEvaluator` **does not execute submitted code**. It compares normalized source text to the task reference solution, which keeps tests deterministic and safe. The evaluator is isolated in `app/modules/grading/evaluator.py` so it can be replaced with a real sandbox adapter.

A production Docker evaluator should use a prebuilt image, no network, a read-only filesystem where practical, roughly 128 MB memory, roughly 0.5 CPU, and a hard timeout. Docker execution was not verified by this implementation, and importing `os` should not be described as blocked unless the sandbox actually enforces that separately.

FastAPI `BackgroundTasks` is also not a durable queue: work can be lost on process restart and is not coordinated across multiple workers. A process-local semaphore limits grading to four concurrent jobs, but it provides neither persistence nor cross-worker coordination. Replace it with a durable queue before production/multi-worker deployment.

## Explicitly still TBD / next phase

No values or behavior were invented for gacha cost/odds/pity, battle scoring, ranking rules, daily missions, proficiency formulas, hint policy, AI provider selection, or mileage meaning. Public housing visits, petting another user's cat, visit rewards, visitor read-only isolation, and idempotent social rewards remain confirmed next-phase functionality outside this vertical slice.
