"""
core/config.py

This module defines configuration dataclasses for running episodes of the agent's life.
TODO: Use Pydantic... the inheritance class is pissing me off

"""

import os
from dataclasses import dataclass
from typing import Optional

# BigQuery Model Configuration
BQ_MODEL_CONNECTION: Optional[str] = os.getenv("BQ_MODEL_CONNECTION")
BQ_MODEL_ENDPOINT: Optional[str] = os.getenv("BQ_MODEL_ENDPOINT")
BQ_MODEL_ID: Optional[str] = os.getenv("BQ_MODEL_ID")
DEFAULT_MODEL_TYPE: str = os.getenv("BQ_MODEL_TYPE", "gemini-2.5-flash")

# Default BigQuery Resource Names
DEFAULT_PROJECT_ID: Optional[str] = os.getenv("BQ_PROJECT_ID")
DEFAULT_DATASET_ID: str = os.getenv("BQ_DATASET_ID", "cleaning_service")
DEFAULT_TABLE_ID: str = os.getenv("BQ_TABLE_ID", "sample_dataset")

# Dataset Organization Constants
DATASET_OBSERVATION_ID: str = "observations"
DATASET_ACTION_ID: str = "cognitive"
DATASET_OUTPUT_ID: str = "cleaned_data"

# RL
BQ_STORE_INSIGHT_ID = "insights"
BQ_STORE_OBSERVATION_ID = "observations"
BQ_AGENT_MODEL_TRAJECTORY_WEEK = "model_trajectory_weekly"
BQ_AGENT_MODEL_TRAJECTORY_DAILY = "model_trajectory_daily"

@dataclass
class Config:
    # BIGQUERY MODEL STORED LOCS
    bq_model_connection: str | None = BQ_MODEL_CONNECTION
    bq_model_endpoint: str | None = BQ_MODEL_ENDPOINT
    bq_model_id: str | None = BQ_MODEL_ID
    # DEFAULT NAMES
    default_model_type: str | None = DEFAULT_MODEL_TYPE
    default_project_id: str | None = DEFAULT_PROJECT_ID
    default_dataset_id: str | None = DEFAULT_DATASET_ID
    default_table_id: str | None = DEFAULT_TABLE_ID

    def __post_init__(self):
        """ Post init to validate and validate configured workspace. """

        if any(i for i in [self.bq_model_connection, self.bq_model_endpoint, self.bq_model_id] if i is None):
            raise ValueError("BigQuery model configuration is incomplete. Please set BQ_MODEL_CONNECTION, BQ_MODEL_ENDPOINT, and BQ_MODEL_ID environment variables. Re-initiate these before starting the workflow.")

@dataclass
class EpisodeConfig:
    input_id: str
    summary_id: str | None = None
    dataset_id: str | None = None
    # BIGQUERY MODEL STORED LOCS
    bq_model_connection: str | None = None
    bq_model_endpoint: str | None = None
    bq_model_id: str | None = None
    # DEFAULT NAMES
    default_model_type: str | None = None
    default_project_id: str | None = None
    default_dataset_id: str | None = None
    default_table_id: str | None = None

    def __post_init__(self):
        """ Post init to validate and validate configured workspace. """

        config = Config()

        self.bq_model_connection = config.bq_model_connection
        self.bq_model_endpoint = config.bq_model_endpoint
        self.bq_model_id = config.bq_model_id
        self.default_model_type = config.default_model_type
        self.default_dataset_id = config.default_dataset_id
        self.default_table_id = config.default_table_id
        self.default_project_id = config.default_project_id

        self.dataset_id = f"{self.default_project_id}.{self.default_dataset_id}.{self.input_id}_{DATASET_ACTION_ID}"
        self.summary_id = f"{self.default_project_id}.{self.default_dataset_id}.{self.input_id}_{DATASET_OBSERVATION_ID}"

