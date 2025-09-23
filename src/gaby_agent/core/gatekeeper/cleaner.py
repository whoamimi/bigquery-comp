"""
gatekeeper/cleaner.py

This module contains SQL templates and functions to interact with
Google BigQuery for data cleaning and assist generative models in making decisions.

"""

from ._wrapper import pandas_gatekeeper
from ..config import Config
from .prompt import SQL_DESCRIBE_DATA_FIELD_LABEL, SQL_DETECT_NUMERIC_FIELD

config = Config()

@pandas_gatekeeper
def describe_data_field(
    data_summary_id: str,
    connection_id: str | None = config.bq_model_connection,
    endpoint: str | None = config.default_model_type
):
    return SQL_DESCRIBE_DATA_FIELD_LABEL.format(
        data_summary_id=data_summary_id,
        connection_id=connection_id,
        endpoint=endpoint
    )

@pandas_gatekeeper
def detect_numeric_field(
    data_summary_id: str,
    connection_id: str | None = config.bq_model_connection,
    endpoint: str | None = config.default_model_type
):
    return SQL_DETECT_NUMERIC_FIELD.format(
        data_summary_id=data_summary_id,
        connection_id=connection_id,
        endpoint=endpoint
    )
