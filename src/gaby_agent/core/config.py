"""
core/config.py

This module defines configuration dataclasses for running episodes of the agent's life.
TODO: Use Pydantic... the inheritance class is pissing me off

"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Optional, Literal

load_dotenv('.env.local')

# Local Configs
LIGHTNING_OLLAMA_HOST_URL = os.getenv("LIGHTNING_OLLAMA_HOST_URL", "")
LOCAL_OLLAMA_HOST_URL = os.getenv("LOCAL_OLLAMA_HOST_URL", "")
AGENT_SANDBOX_URL = os.getenv("AGENT_SANDBOX_URL", "")
# BASE_GUFF_LLM_MODEL = os.getenv("BASE_GUFF_LLM_MODEL", "")
DEBUG_LEVEL = os.getenv("DEBUG", True)

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
    summary_id: str = field(init=False, default="")
    dataset_id: str = field(init=False, default="")

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

@dataclass
class ModelConfig:
    dev: Optional[str] = field(default=None, repr=False)
    prod: Optional[str] = field(default=None, repr=False)
    url: str = field(default="", repr=True)
    alt: list[str] = field(default_factory=list, repr=False)

    model_id: str = field(init=False, repr=True)
    source: Literal['dev', 'prod'] = field(default="dev", repr=False)

    def __post_init__(self):
        if self.source is None:
            raise AttributeError(
                f"Missing model id for workspace '{self.workspace}'. "
                "Please update the model configuration YAML ('config_models.yaml')."
            )
        else:
            self.model_id = self.dev if self.source == 'dev' else self.prod

def load_agent_stack():
    import yaml

    with open("config_models.yaml", "r") as f:
        for file in yaml.safe_load(f):
            yield {
                file.get('model_name'):
                    ModelConfig(
                        dev=file.get('model_id').get('dev', None) if file.get('model_id') else None,
                        prod=file.get('model_id').get('prod', None) if file.get('model_id') else None,
                        url=file.get('url', None),
                        alt=file.get('alt', None)
                    )
            }

@dataclass(frozen=True)
class LocalConfig:
    """ Endpoint Connection to exertanl servers. """
    lightning_ollama: str = LIGHTNING_OLLAMA_HOST_URL
    local_ollama: str = LOCAL_OLLAMA_HOST_URL
    agent_sandbox: str = AGENT_SANDBOX_URL

    @property
    def model_stack(self) -> list:
        return list(load_agent_stack())

    def get_model(self, model_name: str):
        """ Get the model config by name. Returns the first matched model name and its Model config. """
        
        for i in load_agent_stack():
            if model_name in i:
                return i.get(model_name)
        return None

def setup_dev_workspace(root_folder_name: str = 'gaby'):
    """ Call in files / notebooks if running workspace in sub-directory path. """

    if Path.cwd().stem == root_folder_name:
        print(f'Path already set to default root directory: {Path.cwd()}')
        return
    else:
        print('Initialized workspace currently at directory:', Path.cwd())

    current = Path().resolve()
    for parent in [current, *current.parents]:
        if parent.name == root_folder_name:
            os.chdir(parent)  # change working directory
            print(f"📂 Working directory set to: {parent}")
            return # Exit after changing directory

    raise FileNotFoundError(f"Root folder '{root_folder_name}' not found.")


if __name__ == "__main__":
    config = LocalConfig()
    print(config.get_model('base'))