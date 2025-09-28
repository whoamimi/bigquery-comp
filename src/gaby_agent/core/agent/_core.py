"""

src.gaby_agent.core.agent._core
Core classes and functions for the Gaby Agent system.
"""

import ollama
from abc import ABC
from threading import Lock
from dataclasses import dataclass, field
from ollama import Options, ChatResponse, ShowResponse

from ._utils import Toolkit
from ..config import LocalConfig


config = LocalConfig()

print(config)

DEFAULT_OPTIONS = Options(
    num_ctx=1024,         # shorter context → less overhead
    temperature=0.3,      # still stable, but a touch livelier
    top_p=0.9,            # good nucleus sampling
    top_k=40,             # typical safe default
    repeat_penalty=1.05,  # lighter repetition check → less compute
    num_predict=128,      # cap on tokens (speeds up response)
    num_thread=2,         # match physical CPU cores (adjust to your machine)
    num_gpu=1,            # offload to GPU if you have one
    low_vram=True,       # only True if you’re memory-starved
    f16_kv=True,          # faster key/value cache
    use_mmap=True,        # mmap the model for faster loading
    use_mlock=False,      # set True if you want to lock into RAM
    seed=None             # nondeterministic, so cache doesn’t collide
)


CHAT_CONFIG = dict(
    stream=False,
    # think='low',
    options=DEFAULT_OPTIONS.model_dump(),
    keep_alive='15m',
    # tools = FUNCTION CALLABLES
)

@dataclass
class Instructor:
    prompt: str
    input_template: str | None = None
    tools: list[Toolkit] = field(default_factory=list)
    
    def input_validator(self, **kwargs) -> str:
        """Fill in the input template with kwargs if provided, otherwise return kwargs as str."""

        if self.input_template:
            return self.input_template.format(**kwargs)

        return str(kwargs)

class GabyBasement(ABC):
    """Base class for creating thought chains using the Ollama LLM."""

    _lock = Lock()
    _instance = None
    client: ollama.Client = None
    config: LocalConfig = config 

    def __new__(cls, *args, **kwargs):
        """ Singleton pattern to ensure only one instance of the client exists. """
        
        if cls._instance is None:
            with cls._lock:
                cls._instance = super().__new__(cls, *args, **kwargs)
                try:
                    host_url = config.lightning_ollama if config.lightning_ollama != "" else config.local_ollama
                    print("Connecting to Ollama host:", host_url)
                    
                    cls._instance.client = ollama.Client(host_url)

                except Exception as e:
                    raise RuntimeError(f"Failed to init GabyBasement client: {e}")
                
        return cls._instance

    def __init_subclass__(cls, prompt: Instructor, model_name: str, **kwargs):
        super().__init_subclass__(**kwargs)
        
        cls.prompt = prompt 
        cls.name = cls.__qualname__
        cls.kwargs = CHAT_CONFIG.copy()
        cls.model_name = cls.config.get_model(model_name) 
    
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

        self.validate_model_exists(self.model_name.model_id)
        
        print(f"Running thought Chain: {self.name}")

        kwargs = self.pre_process(**kwargs)
        
        user_inputs = self.prompt.input_validator(**kwargs)

        if len(self.prompt.tools) > 0:
            self.kwargs['tools'] = [tool.meta for tool in self.prompt.tools if isinstance(tool, Toolkit)]
            
        response = self.client.chat(
            model=self.model_name.model_id,
            messages=self.system_prompt + [{"role": "user", "content": user_inputs}],
            **self.kwargs
        )
        print(f"Response from model {self.model_name.model_id}: {response}")
        return self.post_process(response)

    def validate_model_exists(self, model_id: str):
        try:
            m: ShowResponse = self.client.show(model_id)
        except ollama.ResponseError as e:
            print('Ollama Client Error while validating models existence', e)
            print(f'Current model: {self.client.list().models} \nPulling model...')
            self.client.pull(model_id)
            return self.validate_model_exists(model_id)
        except Exception as e:
            raise e 

if __name__ == "__main__":
    pass