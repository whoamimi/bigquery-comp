import pytest

from src.gaby_agent.core.agent._core import GabyBasement, Instructor, CHAT_CONFIG
from src.gaby_agent.core.config import LocalConfig


config = LocalConfig()
MODEL_CONFIG = config.model_stack

def test_init_subclass_overwrites_attributes(monkeypatch):
    print("Starting test: test_init_subclass_overwrites_attributes")

    # Stub out get_model to return a dummy object with a model_id
    class DummyModel:
        def __init__(self, model_id):
            self.model_id = model_id

    # Replace the method at the class level instead of the instance level
    monkeypatch.setattr(
        LocalConfig,
        "get_model",
        lambda self, name="model_name": DummyModel("thinking_agent"),
    )
    print("Monkeypatch applied to LocalConfig.get_model")

    # Define a new subclass with a custom prompt + model_name
    class DatasetSummarizer(
        GabyBasement,
        prompt=Instructor(
            prompt="Summarize dataset",
            input_template="Dataset: {user_inputs}",
        ),
        model_name="thinking_agent",
    ):
        pass

    print("DatasetSummarizer subclass created")

    # ---- Assertions ----
    # 1. Subclass should get its own .prompt
    assert isinstance(DatasetSummarizer.prompt, Instructor)
    print("Assertion passed: DatasetSummarizer.prompt is an instance of Instructor")
    assert DatasetSummarizer.prompt.prompt == "Summarize dataset"
    assert DatasetSummarizer.prompt.input_template == "Dataset: {user_inputs}"

    # 2. Subclass should have its .name set from __qualname__
    assert "DatasetSummarizer" in DatasetSummarizer.name
    print("Assertion passed: DatasetSummarizer.name contains 'DatasetSummarizer'")

    # 3. Subclass should get its own CHAT_CONFIG copy
    assert DatasetSummarizer.kwargs == CHAT_CONFIG
    assert DatasetSummarizer.kwargs is not CHAT_CONFIG  # different object
    print("Assertion passed: DatasetSummarizer.kwargs is a copy of CHAT_CONFIG")

    # 4. Subclass should have a model_name assigned from stubbed get_model
    assert hasattr(DatasetSummarizer, "model_name")
    assert isinstance(DatasetSummarizer.model_name, DummyModel)
    assert DatasetSummarizer.model_name.model_id == "thinking_agent"
    print("Assertion passed: DatasetSummarizer.model_name is correctly assigned")

    # 5. Base class is unaffected
    assert not hasattr(GabyBasement, "prompt") or GabyBasement.prompt is not DatasetSummarizer.prompt
    print("Assertion passed: GabyBasement is unaffected by DatasetSummarizer changes")

    print("Test completed successfully")
