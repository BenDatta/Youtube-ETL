# YouTube Data ETL Pipeline

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated data engineering pipeline that extracts YouTube channel video statistics, loads them into PostgreSQL using a **staging → core** warehouse pattern, validates data quality with **Soda**, and orchestrates the full workflow with **Apache Airflow** in Docker—with **GitHub Actions** for CI/CD.

---

## Project overview

This project implements an end-to-end **ELT** pipeline for a configurable YouTube channel (via `CHANNEL_HANDLE`). It removes manual API and database work by:

1. **Extracting** video metadata and engagement metrics from the **YouTube Data API v3** (playlist → video IDs → video statistics).
2. **Loading** a daily JSON snapshot, then upserting into a **staging** schema in PostgreSQL.
3. **Transforming** records into a **core** schema (business rules such as video type and normalized duration).
4. **Validating** both layers with **Soda** (missing/duplicate keys, sanity checks on metrics).

Three Airflow DAGs run in sequence via `TriggerDagRunOperator`: `produce_json` → `update_db` → `data_quality`. The first DAG is scheduled daily; the others are triggered when the previous stage completes.

---

## Architecture

| Stage | What happens |
|-------|----------------|
| **Extract** | Airflow TaskFlow tasks call the YouTube Data API and write `youtube_data_YYYY-MM-DD.json` under `/opt/airflow/data`. |
| **Load** | Python tasks read JSON, create schemas/tables if needed, and upsert into `staging.youtube_elt` by `Video_ID`. |
| **Transform** | Core tasks read staging, apply transformations, and load `core.youtube_elt`. |
| **Quality** | Soda scans `staging` and `core` using checks defined in `include/soda/checks.yml`. |

```mermaid
flowchart LR
  API[YouTube API] --> JSON[JSON file]
  JSON --> STG[(staging)]
  STG --> CORE[(core)]
  STG --> SODA[Soda checks]
  CORE --> SODA

  classDef api fill:#81D4FA,stroke:#0277BD,color:#000
  classDef file fill:#FFF59D,stroke:#F9A825,color:#000
  classDef db fill:#CE93D8,stroke:#7B1FA2,color:#000
  classDef qa fill:#FFAB91,stroke:#E64A19,color:#000

  class API api
  class JSON file
  class STG,CORE db
  class SODA qa
```

| DAG | Schedule | Role |
|-----|----------|------|
| `produce_json` | Daily (`@daily`) | API extract → JSON → trigger warehouse DAG |
| `update_db` | Triggered | Staging load → core transform → trigger quality DAG |
| `data_quality` | Triggered | Soda on `staging`, then `core` |

---

## Tech stack

| Area | Technology |
|------|------------|
| **Language** | Python 3.12 |
| **Orchestration** | Apache Airflow 3.0 (CeleryExecutor, TaskFlow, `TriggerDagRunOperator`) |
| **Data source** | YouTube Data API v3 |
| **Database** | PostgreSQL (`staging`, `core`, Airflow metadata, Celery result backend) |
| **Broker** | Redis |
| **Data quality** | Soda Core (Postgres) |
| **Runtime** | Docker, Docker Compose, custom image on Docker Hub |
| **CI/CD** | GitHub Actions (image build/push, pytest, `airflow dags test`) |
| **Testing** | pytest (unit + integration) |

---

## Getting started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- PostgreSQL (local instance, e.g. via pgAdmin) with databases: `YoutubeDB`, `airflow_metadata`, `airflow_celery`
- [YouTube Data API v3](https://console.cloud.google.com/apis/credentials) key

### 1. Clone the repository

```bash
git clone https://github.com/BenDatta/Youtube-ETL.git
cd Youtube-ETL
```

### 2. Configure environment

Create a `.env` file in the project root (see variables used in `docker-compose.yaml`: API key, channel handle, Postgres connection, Fernet key, Docker image tags). Do not commit `.env`.

### 3. Build and run

```bash
docker build -t benofurhie/youtube_data_elt:1.0.1 .
docker compose up -d
```

Airflow UI: [http://localhost:8081](http://localhost:8081)

---

## Repository layout

```
dags/                 DAGs: API extract, warehouse, Soda quality
include/soda/         Soda datasource config and checks
tests/                Unit and integration tests
Dockerfile            Custom Airflow image (constraints-based deps)
docker-compose.yaml   Airflow Celery stack (+ `ci` Postgres profile)
.github/workflows/    CI/CD pipeline
```

---

## License

This project is licensed under the MIT License. Use of the YouTube API is subject to [Google’s API Terms of Service](https://developers.google.com/youtube/terms/api-services-terms-of-service).
