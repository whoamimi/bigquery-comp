"""
schema.py

This script contains dataclass schemas used across the Gaby Agent application to be stored in BigQuery post user sessions.

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

@dataclass 
class Stage:
    """ Data cleaning stage checklists to assist agents' project management. """
    id: str
    label: str 
    description: str
    stages: dict[list] = {}
    
    @property 
    def list_stages(self):
        yield from self.stages.keys()
    
@dataclass 
class Workflow:
    """ All available Workflow services. """
    data_cleaning: list[Stage] = []
    data_analysis: list[Stage] = []
    data_quality_assessment: list[Stage] = []
    business_insights: list[Stage] = []
    business_dashboard: list[Stage] = []
    model_building: list[Stage] = []
    model_researching: list[Stage] = []
    model_evaluation: list[Stage] = []

    def add_stage(self, service: str, id: str, label: str, description: str):
        """ Add a new stage to the specified service category. """
        
        if hasattr(self, service):
            getattr(self, service).append(Stage(id=id, label=label, description=description))
        else:
            raise ValueError(f"Category {service} does not exist in Workflow.")
