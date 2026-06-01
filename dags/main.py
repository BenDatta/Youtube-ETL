from airflow import DAG
from datetime import datetime, timedelta

from api.video_stat import (
    get_playlist_id,
    get_video_ids,
    extracted_video_data,
    save_to_json,
)

from datawarehouse.dwh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    "owner": "data_analytics_team",
    "retries": 3,
    "retry_delay": timedelta(minutes=10),
}

staging_schema = "staging"
core_schema = "core"

with DAG(
    dag_id="produce_json",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["data_engineering"],
) as dag:
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extract_data = extracted_video_data(video_ids)
    save_to_json_task = save_to_json(extract_data)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db",
    )

    playlist_id >> video_ids >> extract_data >> save_to_json_task >> trigger_update_db

with DAG(
    dag_id="update_db",
    default_args=default_args,
    description="DAG to process JSON file and insert data into both staging and core schemas",
    catchup=False,
    schedule=None,
) as dag_update:
    update_staging = staging_table()
    update_core = core_table()

    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality",
    )

    update_staging >> update_core >> trigger_data_quality

with DAG(
    dag_id="data_quality",
    default_args=default_args,
    description="DAG to check the data quality on both layers in the database",
    catchup=False,
    schedule=None,
) as dag_quality:
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    soda_validate_staging >> soda_validate_core
