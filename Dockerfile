ARG AIRFLOW_VERSION=3.0.6
ARG PYTHON_MAJOR_MINOR=3.12

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_MAJOR_MINOR}

ENV AIRFLOW_HOME=/opt/airflow
ENV PATH="/home/airflow/.local/bin:${PATH}"

COPY requirements.txt /

# Base image already pins Airflow; constraints conflict with soda-core-postgres (ruamel.yaml).
RUN pip install --no-cache-dir -r /requirements.txt
