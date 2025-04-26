
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger()

from pydantic import BaseModel
def pydantic_model_to_custom_json_schema(model: type[BaseModel], name: str, strict: bool = True) -> dict:
    """
    Converts a Pydantic model to a custom JSON schema format.
    """
    schema = model.model_json_schema()
    custom_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "strict": str(strict).lower(),
            "schema": schema
        }
    }
    return custom_schema

def create(name: str, **kwargs):
    if name.startswith("gemini"):
        params = {
            "model": "gemini-2.0-flash-001",
            "temperature": 0,
            "max_tokens": None,
            "timeout": None,
            "max_retries": 2,
            "google_api_key": os.environ["GEMINI_API_KEY"]
        }
        params.update(kwargs)
        return ChatGoogleGenerativeAI(**params)
    elif name == "local":
        params = {
            "base_url":"http://localhost:1234/v1",
            "api_key":"lm-studio"
        }
        params.update(kwargs)
        llm = ChatOpenAI(**params)

        class LmStudioClient():
            def __init__(self, llm, model_name="mistral-nemo-instruct-2407"):
                self.llm = llm
                self.model_name = model_name
                self.invoke_param_decorator = lambda x: x
                self.response_decorator = lambda x: x

            def with_structured_output(self, model):
                def invoke_param_decorator(params):
                    params["response_format"] = pydantic_model_to_custom_json_schema(model, model.__name__, False)
                    return params

                def response_decorator(response):
                    return model.model_validate_json(response.content)

                new_llm = create(name, **kwargs)
                new_llm.invoke_param_decorator = invoke_param_decorator
                new_llm.response_decorator = response_decorator
                return new_llm

            def invoke(self, messages):
                params = {
                    "model": self.model_name,
                    "input": messages,
                }

                params = self.invoke_param_decorator(params)

                logger.debug(params)
                response = self.llm.invoke(**params)
                return self.response_decorator(response)

        return LmStudioClient(llm)
    else:
        raise NotImplementedError()
