"""

src.gaby_agent.core.agent._core
Core classes and functions for the Gaby Agent system.
"""

import os
import ollama
from abc import ABC
from threading import Lock
from dataclasses import dataclass

@dataclass
class Instructor:
    prompt: str
    input_template: str | None = None

    def input_validator(self, **kwargs) -> str:
        """Fill in the input template with kwargs if provided, otherwise return kwargs as str."""

        if self.input_template:
            return self.input_template.format(**kwargs)

        return str(kwargs)

class GabyBasement(ABC):
    """ Prompt Base Constructor. """

    _instance = None
    _lock = Lock()
    client = None
    base_model_id = os.getenv("BASE_GUFF_LLM_MODEL", "hf.co/bartowski/Llama-3.2-3B-Instruct-GGUF:Q3_K_XL")

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'client'):
            raise AttributeError("Ollama client is not initialized. Revise subclass / Base class structure design.")

    def __new__(cls, *args, **kwargs):
        # Double-checked locking for thread safety
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls, *args, **kwargs)
                try:
                    cls._instance.client = ollama.Client(os.getenv("OLLAMA_HOST_URL", "http://localhost:11434"))
                except Exception as e:
                    raise RuntimeError(f"Failed to init GabyBasement client: {e}")

            if len(cls._instance.client.list().models) == 0 or cls.base_model_id not in cls._instance.client.list().models  :
                cls._instance.client.pull(model=cls.base_model_id)
                print(f"Pulled model: {cls.base_model_id}")

        return cls._instance

    def __init_subclass__(cls, prompt: Instructor, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.prompt = getattr(cls, "prompt", prompt)  # don’t overwrite if re-init
        cls.name = cls.__qualname__

    @property
    def system_prompt(self):# -> list[dict[str, Any]]:
        text = self.prompt.prompt if isinstance(self.prompt, Instructor) else str(self.prompt)
        return [{"role": "system", "content": text}]

    def post_process(self, response) -> str:
        """ Post-processes the response from the LLM before returning to the user. Subclass can override this method to implement custom post-processing logic. """

        return response.message.get('content', None).strip()

    def pre_process(self, **kwargs) -> dict:
        """ Pre-processes the input arguments before sending to the LLM. Subclass can override this method to implement custom pre-processing logic. """

        return kwargs

    def run(self, **kwargs) -> str:
        """ Main method to execute the thought chain. """

        if not hasattr(self, "client") or self.client is None:
            raise RuntimeError("Ollama client is not initialized."
                               " Ensure Ollama is running and OLLAMA_HOST_URL is correct.")

        print(f"Running thought Chain: {self.name}")

        kwargs = self.pre_process(**kwargs)
        user_inputs = self.prompt.input_validator(**kwargs)

        response = self.client.chat(
            model=self.base_model_id,
            messages=self.system_prompt + [{"role": "user", "content": user_inputs}],
            stream=False,
            options={
                "max_tokens": 100,
                "num_ctx": 100
            }
        )

        return self.post_process(response)

if __name__ == "__main__":
    pass