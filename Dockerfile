ARG AIRFLOW_VERSION=3.0.6
ARG PYTHON_VERSION=3.12

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ENV AIRFLOW_HOME=/opt/airflow
ENV PATH="/home/airflow/.local/bin:${PATH}"

COPY requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt
