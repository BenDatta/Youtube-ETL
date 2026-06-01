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

| Layer | Technology |
|-------|------------|
| Language | ![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white) |
| Orchestration | ![Airflow](https://img.shields.io/badge/Apache_Airflow-3.0-017CEE?style=flat-square&logo=apacheairflow&logoColor=white) |
| Executor / broker | ![Celery](https://img.shields.io/badge/Celery-Executor-37814A?style=flat-square&logo=celery&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-7.2-DC382D?style=flat-square&logo=redis&logoColor=white) |
| Database | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white) |
| Data source | ![YouTube API](https://img.shields.io/badge/YouTube_Data_API-v3-FF0000?style=flat-square&logo=youtube&logoColor=white) |
| Data quality | ![Soda](https://img.shields.io/badge/Soda_Core-Postgres-00B4D8?style=flat-square) |
| Containers | ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white) ![Docker Hub](https://img.shields.io/badge/Docker_Hub-Image-2496ED?style=flat-square&logo=docker&logoColor=white) |
| Testing | ![pytest](https://img.shields.io/badge/pytest-unit%20%2B%20integration-0A9EDC?style=flat-square&logo=pytest&logoColor=white) |
| CI/CD | ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=flat-square&logo=githubactions&logoColor=white) |

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
