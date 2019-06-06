import logging
from datetime import datetime, timedelta
from random import choice
from string import ascii_lowercase
from tempfile import NamedTemporaryFile
from typing import Dict

from airflow.models import DAG, BaseOperator, TaskInstance, Variable
from airflow.operators.python_operator import (
    BranchPythonOperator,
    PythonOperator,
    ShortCircuitOperator,
)
from airflow.utils.decorators import apply_defaults
from google.cloud import storage

seven_days_ago = datetime.combine(
    datetime.today() - timedelta(7), datetime.min.time()
)

default_args = {
    "owner": "Airflow",
    # arbitrary in most cases
    # https://airflow.apache.org/faq.html#what-s-the-deal-with-start-date
    "start_date": seven_days_ago,
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


class MoveToStorageOperator(BaseOperator):
    """Simple operator which writes to Cloud Storage.

    :bucket_name: Name of the gcs bucket in which to deposit the files.
    """

    @apply_defaults
    def __init__(self, project_name: str, bucket_name: str, *args, **kwargs):
        super(MoveToStorageOperator, self).__init__(*args, **kwargs)
        self.project = project_name
        self.bucket = bucket_name

    def execute(self, context: Dict[str, TaskInstance]) -> None:
        """ Overload the execute method to demonstrate python operators. """
        bucket = storage.Client(project=self.project).bucket(self.bucket)
        ti = context["ti"]
        filename = ti.xcom_pull(key="filename", task_ids="select_filename")
        bit_of_entropy = "".join(
            choice(ascii_lowercase) for _ in range(4)  # nosec prg usage
        )
        qualified_filename = f"{filename}_{bit_of_entropy}.txt"
        logging.info(f"Working with file: {qualified_filename}")
        with NamedTemporaryFile("w") as tf:
            tf.write("Hello World!")
            tf.flush()
            blob = bucket.blob(f"landed/{qualified_filename}")
            blob.upload_from_filename(tf.name)
        logging.info(f"File uploaded to url: {blob.public_url}")
        ti.xcom_push(key="blob_name", value=blob.name)


def select_filename(**kwargs: TaskInstance) -> bool:
    """Choose a name for our file (or None), demonstrate xcom push."""
    filename = choice(["foo", "bar", None])  # nosec for prg usage.
    if filename is not None:
        ti = kwargs["ti"]
        logging.info(f"Pushing file to workflow: {filename}")
        ti.xcom_push(key="filename", value=filename)
    else:
        logging.info("Chose to skip the downstream.")
    return True if filename else False


def classify_file(bucket_name: str, **kwargs: TaskInstance) -> str:
    """ Classify the file and optionally select a downstream task. """
    ti = kwargs["ti"]
    blob_name = ti.xcom_pull(key="blob_name", task_ids="move_to_storage")
    if blob_name.startswith("landed/foo"):
        ti.xcom_push(key="foo", value=blob_name)
        return "foo_task"
    else:
        ti.xcom_push(key="bar", value=blob_name)
        return "bar_task"


def select_foo(
    project_name: str, bucket_name: str, **kwargs: TaskInstance
) -> str:
    """ Pull the blob name, read the blob contents. """
    ti = kwargs["ti"]
    blob_name = ti.xcom_pull(key="foo", task_ids="classify_file")
    bucket = storage.Client(project=project_name).bucket(bucket_name)
    blob = bucket.blob(blob_name)
    logging.info(
        f"Blob {blob_name} downloaded, \
    contents: {blob.download_as_string()}"
    )
    return "Select foo task completed."


def delete_bar(
    project_name: str, bucket_name: str, **kwargs: TaskInstance
) -> str:
    """ Pull the blob name and delete from cloud storage. """
    ti = kwargs["ti"]
    blob_name = ti.xcom_pull(key="bar", task_ids="classify_file")
    bucket = storage.Client(project=project_name).bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    return f"Delete bar file: {blob_name} complete."


dag = DAG(
    dag_id="sample",
    description="Sample airflow DAG written to demonstrate coupling \
              together some different operator types.",
    default_args=default_args,
    schedule_interval=None,
)

with dag:
    choose_filename = ShortCircuitOperator(
        task_id="select_filename",
        python_callable=select_filename,
        provide_context=True,
    )

    move_to_storage = MoveToStorageOperator(
        task_id="move_to_storage",
        project_name=Variable.get(
            "airflow_project", default_var="my-gcp-project"
        ),
        bucket_name=Variable.get(
            "airflow_bucket", default_var="my-gcs-bucket"
        ),
    )

    classify_task = BranchPythonOperator(
        task_id="classify_file",
        python_callable=classify_file,
        op_kwargs={
            "project_name": Variable.get(
                "airflow_project", default_var="my-gcp-project"
            ),
            "bucket_name": Variable.get(
                "airflow_bucket", default_var="my-gcs-bucket"
            ),
        },
        provide_context=True,
    )

    foo_task = PythonOperator(
        task_id="foo_task",
        provide_context=True,
        python_callable=select_foo,
        op_kwargs={
            "project_name": Variable.get(
                "airflow_project", default_var="my-gcp-project"
            ),
            "bucket_name": Variable.get(
                "airflow_bucket", default_var="my-gcs-bucket"
            ),
        },
        dag=dag,
    )

    bar_task = PythonOperator(
        task_id="bar_task",
        provide_context=True,
        python_callable=delete_bar,
        op_kwargs={
            "project_name": Variable.get(
                "airflow_project", default_var="my-gcp-project"
            ),
            "bucket_name": Variable.get(
                "airflow_bucket", default_var="my-gcs-bucket"
            ),
        },
        dag=dag,
    )

    choose_filename >> move_to_storage
    move_to_storage >> classify_task
    classify_task >> foo_task
    classify_task >> bar_task
