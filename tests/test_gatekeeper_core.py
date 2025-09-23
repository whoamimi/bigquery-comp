import os
import pandas as pd
import importlib
import pytest
from unittest import mock


# Minimal dummy credentials and client to keep tests focused and small
class DummyCredentials:
    def __init__(self, project_id="dummy-project"):
        self.project_id = project_id


class DummyClient:
    def __init__(self, project="dummy-project"):
        self.project = project

    def query(self, q):
        class Result:
            def to_dataframe(self):
                return pd.DataFrame({"col1": [1]})
        return Result()

    def load_table_from_dataframe(self, df, table_id, job_config=None):
        class Job:
            output_rows = len(df)
            def result(self):
                return None
        return Job()

    def load_table_from_file(self, source_file, table_id, job_config=None):
        class Job:
            output_rows = 1
            def result(self):
                return None
        return Job()

    def get_table(self, table_id):
        class Tbl:
            schema = []
            _properties = []
        return Tbl()

    def list_datasets(self):
        return [mock.Mock(dataset_id="dummy_ds")]


@pytest.fixture(autouse=True)
def mock_google(monkeypatch):
    """Provide minimal google mocks for the module under test."""
    mock_service_account = mock.MagicMock()
    mock_service_account.Credentials.from_service_account_file.return_value = DummyCredentials()

    mock_bq = mock.MagicMock()
    mock_bq.Client.side_effect = lambda credentials, project=None: DummyClient(project=credentials.project_id)
    mock_bq.LoadJobConfig = mock.MagicMock()
    mock_bq.SourceFormat = mock.MagicMock()
    mock_bq.WriteDisposition = mock.MagicMock()

    import sys
    sys.modules['google'] = mock.MagicMock()
    sys.modules['google.cloud'] = mock.MagicMock()
    sys.modules['google.cloud.bigquery'] = mock_bq
    sys.modules['google.oauth2'] = mock.MagicMock()
    sys.modules['google.oauth2.service_account'] = mock_service_account

    # Ensure env var points to some path; tests will monkeypatch isfile as needed
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/nonexistent_credentials.json'

    yield


def reload_module():
    return importlib.reload(importlib.import_module('gaby_agent.core.gatekeeper._core'))


def test_init_and_client(monkeypatch):
    # Make isfile True so GateKeeper picks up credentials
    monkeypatch.setattr(os.path, 'isfile', lambda p: True)
    module = reload_module()
    gk = module.GateKeeper()
    assert gk.bf is not None
    assert hasattr(gk.bf, 'project')


def test_load_table(monkeypatch):
    monkeypatch.setattr(os.path, 'isfile', lambda p: True)
    module = reload_module()
    gk = module.GateKeeper()
    df = module.GateKeeper.load_table('proj.db.table', gk.bf)
    assert isinstance(df, pd.DataFrame)


def test_upload_from_dataframe(monkeypatch):
    monkeypatch.setattr(os.path, 'isfile', lambda p: True)
    module = reload_module()
    gk = module.GateKeeper()
    df = pd.DataFrame({"a": [1, 2]})
    res = module.GateKeeper.upload_dataset(db_id='db', dataset_id='table', client=gk.bf, df=df)
    assert isinstance(res, pd.DataFrame)

