"""
schema.py

This script contains dataclass schemas used across the Gaby Agent application to be stored in BigQuery pre/post user sessions.

"""

import pandas as pd
from dataclasses import dataclass

@dataclass
class EntryReport:
    description: str | None = None
    data_field_summary: pd.DataFrame | None = None
    data_field_description: pd.DataFrame | None = None
    numeric_table: pd.DataFrame | None = None

@dataclass
class MissingDataReport:
    missing_pattern: str
    missing_count: float
    missing_perc: float
    data_field_type: str
