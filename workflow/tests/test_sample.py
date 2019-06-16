import random

import airflow
import pytest

import workflow.dags.sample

# NOTE these are just intended to show how to get the tests up and running
# obviously you could improve the assertions and the coverage here with
# a little more effort.


def test_dag_is_valid():
    assert isinstance(workflow.dags.sample.dag, airflow.models.DAG)  # nosec


@pytest.mark.usefixtures("setup_airflow_test_context")
def test_move_to_storage(test_dag, mock_storage):
    task = workflow.dags.sample.MoveToStorageOperator(
        project_name="test_project",
        bucket_name="test_bucket",
        task_id="test",
        dag=test_dag,
    )

    test_dag.clear()
    ti = airflow.models.TaskInstance(task, execution_date=test_dag.start_date)
    ti.run()

    assert ti.duration


@pytest.mark.usefixtures("setup_airflow_test_context")
def test_select_filename_falsy_path(test_dag, monkeypatch, mock_storage):
    monkeypatch.setattr(random, "choice", lambda *args: None)
    task = airflow.operators.python_operator.ShortCircuitOperator(
        task_id="select_filename",
        python_callable=workflow.dags.sample.select_filename,
        provide_context=True,
        dag=test_dag,
    )

    test_dag.clear()
    ti = airflow.models.TaskInstance(task, execution_date=test_dag.start_date)
    ti.run()

    assert ti.duration


@pytest.mark.usefixtures("setup_airflow_test_context")
def test_select_filename_truthy_path(test_dag, monkeypatch, mock_storage):
    monkeypatch.setattr(random, "choice", lambda *args: "foo")
    task = airflow.operators.python_operator.ShortCircuitOperator(
        task_id="select_filename",
        python_callable=workflow.dags.sample.select_filename,
        provide_context=True,
        dag=test_dag,
    )

    test_dag.clear()
    ti = airflow.models.TaskInstance(task, execution_date=test_dag.start_date)
    ti.run()

    assert ti.duration
