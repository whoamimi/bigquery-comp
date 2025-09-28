""" 
core/agent/orchestrator.py

Orchestrator module for managing and coordinating agent workflows.
NOTE: GPT-OSS cannot handle tools with ollama. 
TODO: Change DataProfiler to a decorator function and BackgroundTracker should <-> meet inherit from same parent class 
"""

import sys
import os

# Add the src directory to the system path to resolve imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, src_dir)

from gaby_agent.core.agent._utils import Toolkit
from gaby_agent.core.agent._core import GabyBasement, Instructor
from gaby_agent.core.agent.tools import statistical_methods as MissingClassifier 
from gaby_agent.core.agent.prompt import MISSING_TARGET_PROMPT, MISSING_TARGET_INPUT_TEMPLATE, BACKGROUND_TRACKER_INPUT_TEMPLATE, BACKGROUND_TRACKER_PROMPT

class BackgroundTracker(
    GabyBasement,
    prompt=Instructor(
        prompt=BACKGROUND_TRACKER_PROMPT,
        input_template=BACKGROUND_TRACKER_INPUT_TEMPLATE
    ),    
    model_name="thinking_agent"
):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.history = []
        self.max_steps = kwargs.get("max_steps", 5)
        # start as background task and steps / increments and appends to history every time an action is made in this workspace
        self.current_step = 0

class PromptCycleStopButton(
    GabyBasement,
    prompt=Instructor(
        prompt="""Reurn True or False if error captured from sandbox environment is critical to halt the current workflow i.e. surpassing max retries, invalid user input, or system failure. Otherwise return False.""",
        input_template="logger messages: {input_logs}"
    ),    
    model_name="thinking_agent"
):
    """Basically stops the workflow cycle if too many errors are encountered. The model caches are thene reset / flushed and the workflow is restarted from the beginning -> tracing to previous K steps."""
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.history = []
        self.max_steps = kwargs.get("max_steps", 5)
        # start as background task and steps / increments and appends to history every time an action is made in this workspace
        self.current_step = 0

class MissingDetection(
    GabyBasement,
    prompt=Instructor(
        prompt=MISSING_TARGET_PROMPT,
        input_template=MISSING_TARGET_INPUT_TEMPLATE
    ),
    model_name="base",
):
    def function_exists_in_missingclassifier(func_name: str) -> bool:
        """Check if a function by string name exists in MissingClassifier module."""
        return hasattr(MissingClassifier, func_name) and callable(getattr(MissingClassifier, func_name))

    def post_process(self, response) -> str:
        """ Post-process the model response to extract the tool name. """
        func_name = response.message.get('content', '').strip()
        if hasattr(MissingClassifier, func_name) and callable(getattr(MissingClassifier, func_name)):
            results = getattr(MissingClassifier, func_name)()
            print(results) 

            return {
                "tool_name": func_name,
                "tool_result": results
            }

class MissingEvaluation(
    GabyBasement,
    prompt=Instructor(
        prompt="""
        You are a senior data analyst. Based on the dataset’s fields and descriptive metadata, provide a concise summary (no more than 2 sentences) that highlights:
        •	the dataset’s key characteristics and notable features or patterns,
        •	potential modeling or analytical objectives it may support, and
        •	whether the dataset contains any unique identifiers.
        """,
        input_template="""
        Dataset descriptive labels: {task_objective},
        Evaluating Method Used: {tools_metadata}
        Results: 
        {tools_results}
        Dataset Subset:
        {data_field_summary}
        """
    ),
    model_name="base_agent"
):
    pass

if __name__ == "__main__":
    missing_detection = MissingDetection()
    print(missing_detection.model_name.model_id)
    
    output = missing_detection.run(
        input_data_field_summary="""
| Column Name | Data Type     | Missing Ratio |
|-------------|---------------|---------------|
| age         | numeric       | 0.02          |
| income      | numeric       | 0.15          |
| gender      | categorical   | 0.01          |
| region      | categorical   | 0.00          |
| purchase    | binary        | 0.10          |
""",
        input_target_col="income"
    )
    
    print(output)