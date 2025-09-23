""" pipeline.py """

import pandas as pd
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass
from agent.cleaner import DatasetSummarizer, DataFieldMetaDescription
from gatekeeper._wrapper import upload_dataframe_to_bq
from config import EpisodeConfig
from schemas.episode import EntryReport

@dataclass
class DataProfiler:
    # User Inputs
    data: pd.DataFrame
    user_input_tags: str | list | None = None

    # Defining the dataset
    description: str | None = None # Describing the dataset in natural language
    data_field_summary: pd.DataFrame | None = None # Data field summary table
    data_field_description: pd.DataFrame | None = None # Data field summary table with description columns
    numeric_table: pd.DataFrame | None = None # Data field summary table with description columns

    _send_to_gatekeeper: bool = False
    # Episode ID & Configuration
    episode_id: str = uuid4().hex
    timestamp: str = datetime.now().isoformat()
    config: EpisodeConfig | None = None

    def __post_init__(self):
        try:
            self.define_dataset(self._send_to_gatekeeper)
            # the EpisodeConfig stored dataset id for the input dataset is set to self.episode_id-self.tiemstamp in prod
            # self.config = EpisodeConfig(
            #    input_dataset_id=f"{self.episode_id}-{self.timestamp}",
            #    summary_table_id=f"{self.episode_id}-{BQ_TABLE_SUMMARY_ID}"
            #)
            self.config = EpisodeConfig(
                input_id=self.episode_id,
            )

        except Exception as e:
            print(f"❌ Error during dataset definition: {e}")
            raise e

    @staticmethod
    def summarize_dataframe(df: pd.DataFrame):
        for col in df.columns:
            total_count = len(df)
            missing_count = df[col].isna().sum()
            data_type = df[col].dtype

            # Check if continuous: numeric with many unique values
            if pd.api.types.is_numeric_dtype(df[col]) and df[col].nunique() > 20:
                unique_vals = "continuous"
            else:
                unique_vals = df[col].nunique()

            yield {
                "data_field_name": col,
                "missing_count": missing_count,
                "total_count": total_count,
                "data_type": str(data_type),
                "unique_values": unique_vals
            }

    def define_dataset(self, upload_summary: bool = False):
        if self.data.shape[0] == 0 or self.user_input_tags is None:
            raise ValueError("The provided DataFrame is empty or data origin is not specified. Both these are required to start the workflow.")

        # assuming have loaded the model and returned it
        self.data_field_summary = pd.DataFrame.from_records(list(summarize_dataframe(self.data)))

        print(f"✅ Dataset defined with {self.data.shape[0]} rows and {self.data.shape[1]} columns.")

        if upload_summary is True:
            upload_dataframe_to_bq(self.data, self.config.bq_model_connection, self.config.bq_dataset_id, self.config.default_table_id)
            upload_dataframe_to_bq(self.data_field_summary, self.config.bq_model_connection, self.config.bq_dataset_id, self.config.default_dataset_id)

        print(f"Completed profiling for dataset id: {self.episode_id} and uploaded to BQ.")

    @property
    def end_cleaning_report(self) -> EntryReport:
        return EntryReport(
            description=self.description,
            data_field_summary=self.data_field_summary,
            data_field_description=self.data_field_description
        )

    def episode_recap(self):
        context_prompt = f"--- Data Summary ---"

        end_cleaning_report = self.end_cleaning_report

        context_prompt += f"\nDataset Description: {end_cleaning_report.description}\n" if end_cleaning_report.description is not None else "\nNo dataset description available.\n"
        context_prompt += f"\nData Field Summary:\n{end_cleaning_report.data_field_summary.to_markdown(index=False)}\n" if end_cleaning_report.data_field_summary is not None else ""
        context_prompt += f"\nData Field Description:\n{end_cleaning_report.data_field_description.to_markdown(index=False)}\n" if end_cleaning_report.data_field_description is not None else ""

        return context_prompt

    def data_cleaning_pipeline(report: DataProfiler) -> DataProfiler:
        """ Main function to run the data cleaning pipeline. """

        report.description = DatasetSummarizer().run(
            user_inputs=report.user_input,
            data_table=report.data.head(3).to_string(index=False)
        )

        try:
            report.data_field_description = describe_data_field(
                connection_id=report.config.bq_model_connection,
                model_endpoint=report.config.default_model_type,
            )

            report.numeric_table = detect_numeric_field(
                connection_id=report.config.bq_model_connection,
                endpoint=report.config.default_model_type,
                data_summary_id=report.config.summary_id
            )
        except Exception as e:
            print("Error using GCP model, falling back to local model (takes longer to run):", e)

            report.data_field_description = DataFieldMetaDescription().run_loop(
                data=report.data,
                data_description=report.description
            )
            report.numeric_table = None

        return report
