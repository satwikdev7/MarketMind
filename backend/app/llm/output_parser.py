from __future__ import annotations

import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


class OutputParserError(ValueError):
    """Raised when LLM output cannot be repaired or validated."""


def extract_json_string(text: str) -> str:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate)
        candidate = re.sub(r"\s*```$", "", candidate)

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start != -1 and end != -1 and end > start:
        return candidate[start : end + 1]
    raise OutputParserError("No JSON object found in model output")


def repair_json_string(text: str) -> str:
    candidate = extract_json_string(text)
    open_braces = candidate.count("{")
    close_braces = candidate.count("}")
    open_brackets = candidate.count("[")
    close_brackets = candidate.count("]")

    if open_brackets > close_brackets:
        candidate += "]" * (open_brackets - close_brackets)
    if open_braces > close_braces:
        candidate += "}" * (open_braces - close_braces)
    return candidate


def parse_json_output(text: str) -> dict:
    candidate = repair_json_string(text)
    decoder = json.JSONDecoder()
    try:
        payload, _ = decoder.raw_decode(candidate)
        if not isinstance(payload, dict):
            raise OutputParserError("Model output did not decode to a JSON object")
        return payload
    except json.JSONDecodeError as exc:
        raise OutputParserError(f"Invalid JSON output: {exc}") from exc


def parse_structured_output(text: str, model_class: type[ModelT]) -> ModelT:
    payload = normalize_payload_for_model(parse_json_output(text), model_class)
    try:
        return model_class.model_validate(payload)
    except ValidationError as exc:
        raise OutputParserError(f"Schema validation failed: {exc}") from exc


def normalize_payload_for_model(payload: dict, model_class: type[BaseModel]) -> dict:
    if model_class.__name__ == "AnalysisResult":
        return _normalize_analysis_result_payload(payload)
    return payload


def _normalize_analysis_result_payload(payload: dict) -> dict:
    normalized = dict(payload)
    normalized["competitor_profiles"] = [
        item
        for item in normalized.get("competitor_profiles", [])
        if isinstance(item, dict) and item.get("name")
    ]

    normalized_signals: list[dict] = []
    for item in normalized.get("competitive_signals", []):
        if not isinstance(item, dict):
            continue
        if not item.get("company"):
            continue
        if not item.get("signal_type"):
            item["signal_type"] = "other"
        if not item.get("description"):
            item["description"] = ""
        if not item.get("impact"):
            item["impact"] = "Medium"
        if not item.get("source_url"):
            item["source_url"] = ""
        normalized_signals.append(item)
    normalized["competitive_signals"] = normalized_signals

    swot = normalized.get("swot_analysis") or {}
    if not isinstance(swot, dict):
        swot = {}
    swot.setdefault("target", "Unknown market")
    swot.setdefault("strengths", [])
    swot.setdefault("weaknesses", [])
    swot.setdefault("opportunities", [])
    swot.setdefault("threats", [])
    normalized["swot_analysis"] = swot

    return normalized
