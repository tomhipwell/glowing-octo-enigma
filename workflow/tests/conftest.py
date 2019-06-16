import datetime
from unittest.mock import MagicMock

import airflow
import pytest
from google.cloud import storage


@pytest.fixture
def setup_airflow_test_context():
    airflow.configuration.load_test_config()
    airflow.utils.db.initdb()


@pytest.fixture
def mock_storage(monkeypatch):
    monkeypatch.setattr(storage, "Client", MagicMock())


@pytest.fixture
def test_dag():
    return airflow.models.DAG(
        "test_dag",
        start_date=datetime.datetime(2019, 6, 1),
        schedule_interval=datetime.timedelta(days=1),
    )
