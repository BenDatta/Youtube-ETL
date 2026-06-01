ARG AIRFLOW_VERSION=3.0.6
ARG PYTHON_MAJOR_MINOR=3.12

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_MAJOR_MINOR}

ARG AIRFLOW_VERSION
ARG PYTHON_MAJOR_MINOR

ENV AIRFLOW_HOME=/opt/airflow
ENV PATH="/home/airflow/.local/bin:${PATH}"

COPY requirements.txt /

RUN curl -fsSL \
      "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_MAJOR_MINOR}.txt" \
      -o /dev/null \
  && pip install --no-cache-dir \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_MAJOR_MINOR}.txt" \
      -r /requirements.txt
