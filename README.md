# YouTube ELT Pipeline

An end-to-end **extract–load–transform** pipeline for YouTube channel analytics. The project pulls video statistics from the YouTube Data API, lands them in PostgreSQL using a **staging → core** warehouse pattern, and validates both layers with **Soda**—all orchestrated by **Apache Airflow** in Docker, with automated testing in **GitHub Actions**.

## What I built

I designed three linked Airflow DAGs that run as a single logical pipeline. The first DAG runs on a daily schedule; the others are triggered when the previous stage finishes.

**1. Extract (`produce_json`)**  
TaskFlow tasks resolve the channel’s uploads playlist, paginate video IDs, call the Videos API for statistics (title, publish date, duration, views, likes, comments), and write a dated JSON file under `/opt/airflow/data`. A trigger starts the warehouse DAG.

**2. Load & transform (`update_db`)**  
Python tasks read the JSON file, create schemas and the `youtube_elt` table if needed, and upsert into **staging**. Rows are updated or inserted by `Video_ID`. The **core** layer applies business rules—such as classifying short vs long-form video type and normalizing duration—before data is promoted from staging. Another trigger starts quality checks.

**3. Data quality (`data_quality`)**  
Soda scans `staging.youtube_elt` and `core.youtube_elt` for missing or duplicate keys and for metrics that fail sanity rules (for example, likes or comments greater than views).

Infrastructure-wise, I packaged a **custom Airflow 3 image** (Celery executor, Redis broker, Postgres for metadata, Celery results, and the ELT database). I added **unit and integration tests** (mocked DAG integrity plus live API/DB checks) and a **CI/CD workflow** that builds the image, runs pytest inside the stack, and executes `airflow dags test` against an ephemeral Postgres instance.

## Pipeline flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontFamily': 'arial', 'fontSize': '14px'}}}%%
flowchart TB
    subgraph EXTRACT["① produce_json — daily extract"]
        direction TB
        T1["get_playlist_id"]
        T2["get_video_ids"]
        T3["extracted_video_data"]
        T4["save_to_json"]
        T1 --> T2 --> T3 --> T4
    end

    JSON[("youtube_data_YYYY-MM-DD.json")]
    T4 --> JSON

    subgraph LOAD["② update_db — load & transform"]
        direction TB
        T5["staging_table<br/>CREATE SCHEMA · upsert staging"]
        T6["core_table<br/>transform · load core"]
        T5 --> T6
    end

    JSON --> T5

    subgraph DWH["PostgreSQL — YoutubeDB"]
        direction LR
        STG[("staging.youtube_elt")]
        CORE[("core.youtube_elt")]
        STG -->|"transform & promote"| CORE
    end

    T5 --> STG
    T6 --> CORE

    subgraph QUALITY["③ data_quality — Soda scans"]
        direction TB
        T7["soda_test_staging"]
        T8["soda_test_core"]
        T7 --> T8
    end

    T6 -.->|trigger| T7
    STG --> T7
    CORE --> T8

    API(["YouTube Data API v3"])
    API --> T1

  classDef extract fill:#B3E5FC,stroke:#0277BD,stroke-width:2px,color:#0D47A1
  classDef file fill:#FFF9C4,stroke:#F9A825,stroke-width:2px,color:#E65100
  classDef load fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
  classDef db fill:#E1BEE7,stroke:#7B1FA2,stroke-width:2px,color:#4A148C
  classDef quality fill:#FFCCBC,stroke:#E64A19,stroke-width:2px,color:#BF360C
  classDef source fill:#80DEEA,stroke:#00838F,stroke-width:2px,color:#006064

  class T1,T2,T3,T4 extract
  class JSON file
  class T5,T6 load
  class STG,CORE db
  class T7,T8 quality
  class API source
```

| DAG | Schedule | Tasks (summary) |
|-----|----------|-----------------|
| `produce_json` | `@daily` | Playlist → video IDs → API extract → JSON file → trigger `update_db` |
| `update_db` | Triggered | Staging upsert → core transform → trigger `data_quality` |
| `data_quality` | Triggered | Soda on `staging`, then Soda on `core` |

## Data model

| Schema | Table | Contents |
|--------|-------|----------|
| `staging` | `youtube_elt` | Raw-aligned fields from JSON; insert/update by `Video_ID` |
| `core` | `youtube_elt` | Transformed attributes (e.g. `Video_Type`, `Duration` as `TIME`) |

Quality rules in `include/soda/checks.yml` enforce row-level integrity and business sanity on both tables.

## Tech stack

| Area | Tools |
|------|--------|
| Orchestration | Apache Airflow 3.0 (CeleryExecutor, TaskFlow API, `TriggerDagRunOperator`) |
| Language | Python 3.12 |
| Storage | PostgreSQL (`staging`, `core`, Airflow metadata, Celery backend) |
| Messaging | Redis (Celery broker) |
| Containers | Docker, Docker Compose, custom image on Docker Hub |
| Source API | YouTube Data API v3 |
| Data quality | Soda Core + Postgres adapter |
| CI/CD | GitHub Actions (path-based jobs, local image build in tests, pytest + DAG tests) |
| Testing | pytest (unit mocks + integration against API and Postgres) |

## Repository layout

```
dags/
  main.py              DAG definitions and cross-DAG triggers
  api/video_stat.py    YouTube extraction tasks
  datawarehouse/       Staging/core load, transforms, utilities
  dataquality/soda.py  Soda BashOperator wrappers
include/soda/          Datasource config and check definitions
tests/                 Unit and integration test suite
Dockerfile             Airflow image with constraints-based pip install
docker-compose.yaml    Celery Airflow stack (+ optional CI Postgres profile)
.github/workflows/     Build, push, and test pipeline
```
