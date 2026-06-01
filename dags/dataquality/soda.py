from airflow.operators.bash import BashOperator

SODA_PATH = "/opt/airflow/include/soda"
DATASOURCE = "pg_datasource"


def yt_elt_data_quality(schema: str) -> BashOperator:
    # Do not set BashOperator env= — it replaces the container env and breaks ${POSTGRES_CONN_HOST_LOCAL} in configuration.yml
    return BashOperator(
        task_id=f"soda_test_{schema}",
        bash_command=(
            'export PATH="/home/airflow/.local/bin:$PATH" && '
            f"export SCHEMA={schema} && "
            f"soda scan -d {DATASOURCE} "
            f"-c {SODA_PATH}/configuration.yml "
            f"-v SCHEMA={schema} "
            f"{SODA_PATH}/checks.yml"
        ),
    )
