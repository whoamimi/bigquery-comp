""" clean_stage_a.py """

import pandas as pd
from agent._core import GabyBasement, Instructor

class DatasetSummarizer(
    GabyBasement,
    prompt = Instructor(
        prompt="""
        You are a senior data analyst. Based on the dataset’s fields and descriptive metadata, provide a concise summary (no more than 2 sentences) that highlights:
        •	the dataset’s key characteristics and notable features or patterns,
        •	potential modeling or analytical objectives it may support, and
        •	whether the dataset contains any unique identifiers.
        """,
        input_template="""
        Dataset descriptive labels: {user_inputs},
        Dataset Subset:
        {data_table}
        """
    )
):
    pass

class DataFieldMetaDescription(
    GabyBasement,
    prompt = Instructor(
        prompt="You are a data analyst. Given the dataset description and a specific data field label, return a concise description of what the data field possibly means in the context of the dataset. Return your response in at most 1 sentence.",
        input_template="""
        Dataset Description: {data_description}
        Data Field Label: {data_label}
        Data Sample: {data_sample}
        """
    )
):
    def run_loop(self, data: pd.DataFrame, data_description: str) -> dict:
        """ Run the description for each data field in the dataframe. """

        descriptions = {}

        for column in data.columns:
            sample = data[column].dropna().unique()[:3].tolist()
            sample_str = ", ".join(map(str, sample))

            description = self.run(
                data_description=data_description,
                data_label=column,
                data_sample=sample_str
            )

            descriptions[column] = [
                {
                    'name': self.post_process(description),
                    'data_type': str(data[column].dtype),
                    'description': description
                }
            ]

        return descriptions
