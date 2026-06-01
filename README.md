# YouTube Data ETL Pipeline

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ELT pipeline for YouTube channel video stats: **API → JSON → PostgreSQL (staging → core) → Soda**, orchestrated with **Apache Airflow** in Docker. Includes **pytest** coverage and a **GitHub Actions** CI/CD workflow.

---

## Overview

Configurable channel handle → daily extract from **YouTube Data API v3** → load/upsert **staging** → transform **core** → **Soda** quality checks on both schemas.

Three DAGs, chained with `TriggerDagRunOperator`: **`produce_json`** (daily) → **`update_db`** → **`data_quality`**.

```mermaid
flowchart LR
  A["① Extract<br/>YouTube API"] --> B["② JSON"]
  B --> C["③ staging"]
  C --> D["④ core"]
  C --> E["⑤ Soda"]
  D --> E

  style A fill:#4FC3F7,stroke:#0277BD,stroke-width:2px,color:#000
  style B fill:#FFF176,stroke:#F9A825,stroke-width:2px,color:#000
  style C fill:#CE93D8,stroke:#6A1B9A,stroke-width:2px,color:#000
  style D fill:#B39DDB,stroke:#4527A0,stroke-width:2px,color:#000
  style E fill:#FF8A65,stroke:#D84315,stroke-width:2px,color:#000
```

| DAG | Role |
|-----|------|
| `produce_json` | API → daily JSON file |
| `update_db` | Staging upsert → core transform |
| `data_quality` | Soda on `staging`, then `core` |

---

## Tech stack

Python 3.12 · Apache Airflow 3 (Celery, Redis) · PostgreSQL · YouTube Data API v3 · Soda Core · Docker / Compose · Docker Hub · **pytest** · **GitHub Actions**

---

## Testing

| Layer | What runs |
|-------|-----------|
| **Unit** | DAG import integrity, mocked Airflow variables and Postgres connection (`tests/test_unit.py`) |
| **Integration** | Live YouTube API response and Postgres `SELECT 1` (`tests/test_integration.py`) |

Tests run locally with `pytest tests/ -v` or inside the Airflow worker container after `docker compose up`.

---

## CI/CD

Workflow: [`.github/workflows/ci-cd-elt.yaml`](.github/workflows/ci-cd-elt.yaml)

```mermaid
flowchart LR
  P[Push / PR] --> B[Build image]
  B --> H[Push Docker Hub]
  P --> T[Test job]
  T --> D[docker compose --profile ci]
  D --> PY[pytest]
  D --> E2E[airflow dags test]

  style P fill:#E3F2FD,stroke:#1565C0,color:#000
  style B fill:#C8E6C9,stroke:#2E7D32,color:#000
  style H fill:#C8E6C9,stroke:#2E7D32,color:#000
  style T fill:#FFF9C4,stroke:#F9A825,color:#000
  style D fill:#FFE0B2,stroke:#EF6C00,color:#000
  style PY fill:#F8BBD0,stroke:#C2185B,color:#000
  style E2E fill:#F8BBD0,stroke:#C2185B,color:#000
```

| Job | Purpose |
|-----|---------|
| **build-and-push-image** | Build custom Airflow image; push `:latest` and `:$SHA` to Docker Hub |
| **unit-and-integration-and-e2e-tests** | Build image on runner, start stack with CI Postgres, run **pytest** and **`airflow dags test`** on all three DAGs |

Path filters skip jobs when unrelated files change. Secrets and variables in GitHub mirror `.env` (API key, DB credentials, Fernet key, Docker Hub).

---

## Repository

`dags/` · `include/soda/` · `tests/` · `Dockerfile` · `docker-compose.yaml` · `.github/workflows/`

---

## License

MIT · YouTube API use subject to [Google’s terms](https://developers.google.com/youtube/terms/api-services-terms-of-service).
