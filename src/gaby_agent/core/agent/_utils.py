""" gaby_agent/core/agent/_utils.py"""

import inspect
import docstring_parser
from functools import wraps
from typing import get_type_hints
from dataclasses import dataclass, field

TOOLS_REGISTRY = {}

def agent_toolbox(func):
    """
    Decorator that registers a function as a tool, extracting:
      - name
      - docstring description
      - argument definitions (from type hints + docstring)
    """

    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    doc = func.__doc__ or "Unknown"
    parsed_doc = docstring_parser.parse(doc)

    # Map docstring arg descriptions
    doc_args = {p.arg_name: p.description for p in parsed_doc.params}

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        # Infer JSON schema type
        annotation = type_hints.get(name, str)
        if annotation in (int, "int"):
            arg_type = "integer"
        elif annotation in (float, "float"):
            arg_type = "number"
        elif annotation in (bool, "bool"):
            arg_type = "boolean"
        else:
            arg_type = "string"

        if param.default == inspect._empty:
            required.append(name)

        # Prefer docstring description if available
        desc = doc_args.get(name, f"Argument `{name}` of type {arg_type}")

        properties[name] = {
            "type": arg_type,
            "description": desc
        }

    tool_dict = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": parsed_doc.short_description or doc.strip(),
            "parameters": {
                "type": "object",
                "required": required,
                "properties": properties,
            },
        },
    }

    TOOLS_REGISTRY[func.__name__] = tool_dict

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


# ==== Example usage ====
@agent_toolbox
def subtract_two_numbers(a: int, b: int) -> int:
    """Subtract two numbers.

    Args:
        a (int): The first number to subtract from.
        b (int): The second number to subtract.

    Returns:
        int: The difference a - b.
    """
    return a - b


@dataclass 
class Toolkit:
    function: callable
    meta: dict = field(init=False) 
    
    def __post_init__(self):
        if self.function.__name__ not in TOOLS_REGISTRY:
            raise ValueError(f"Function {self.function.__name__} is not registered as a tool. Please use @agent_toolbox decorator.")
        
        self.meta = TOOLS_REGISTRY[self.function.__name__]
        