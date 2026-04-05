from __future__ import annotations

import time
from typing import Literal, TypeVar

from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.config import get_settings
from app.llm.output_parser import OutputParserError, parse_structured_output


Role = Literal["researcher", "analyst", "writer"]
ModelT = TypeVar("ModelT", bound=BaseModel)
MAX_RETRIES = 3


def get_llm(role: Role) -> ChatGroq:
    settings = get_settings()
    model_name = settings.llm_primary_model if role == "writer" else settings.llm_secondary_model
    max_tokens = settings.llm_max_tokens if role == "writer" else min(settings.llm_max_tokens, 2048)
    return ChatGroq(
        model=model_name,
        api_key=settings.groq_api_key,
        temperature=settings.llm_temperature,
        max_tokens=max_tokens,
    )


def invoke_text(prompt: str, role: Role) -> str:
    llm = get_llm(role)
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = llm.invoke(prompt)
            return str(response.content)
        except Exception as exc:
            last_error = exc
            if attempt == MAX_RETRIES - 1:
                break
            time.sleep(2**attempt)
    raise RuntimeError(f"Groq invocation failed after {MAX_RETRIES} attempts: {last_error}")


def invoke_structured(prompt: str, role: Role, model_class: type[ModelT]) -> ModelT:
    last_error: Exception | None = None
    retry_prompt = prompt
    for attempt in range(MAX_RETRIES):
        raw_output = invoke_text(retry_prompt, role=role)
        try:
            return parse_structured_output(raw_output, model_class)
        except OutputParserError as exc:
            last_error = exc
            retry_prompt = (
                f"{prompt}\n\n"
                "Your previous response was invalid. Return valid JSON only and satisfy the schema.\n"
                f"Validation issue: {exc}"
            )
            if attempt == MAX_RETRIES - 1:
                break
    raise RuntimeError(f"Structured Groq invocation failed after {MAX_RETRIES} attempts: {last_error}")
