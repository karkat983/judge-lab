"""Bounded, duplicate-key-free JSON and versioned canonical UTF-8 encoding."""

import hashlib
import json
import math
from typing import Any

from pydantic import ValidationError

from judge_lab.contracts import ContractError, FrozenModel

MAX_RECORD_BYTES = 256 * 1024
MAX_DOCUMENT_BYTES = 16 * 1024 * 1024
MAX_DEPTH = 32


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("INVALID_INPUT")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ContractError("INVALID_INPUT")


def _normalize(value: Any, depth: int = 0) -> Any:
    if depth > MAX_DEPTH:
        raise ContractError("INVALID_INPUT")
    if isinstance(value, str):
        value.encode("utf-8", errors="strict")
        return value.replace("\r\n", "\n").replace("\r", "\n")
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is float and math.isfinite(value):
        return value
    if isinstance(value, (tuple, list)):
        return [_normalize(item, depth + 1) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractError("INVALID_INPUT")
            normalized_key = _normalize(key, depth + 1)
            if normalized_key in result:
                raise ContractError("INVALID_INPUT")
            result[normalized_key] = _normalize(item, depth + 1)
        return result
    raise ContractError("INVALID_INPUT")


def canonical_bytes(value: Any) -> bytes:
    """JL canonical JSON v1: sorted keys, LF strings, preserved array order, finite numbers.

    Not RFC 8785. No Unicode compatibility normalization or coercion of numbers/strings.
    Full serialization is for private inputs/provenance, not default reporting.
    """
    try:
        if isinstance(value, FrozenModel):
            value = value.model_dump(mode="json")
        normalized = _normalize(value)
        return json.dumps(normalized, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise ContractError("INVALID_INPUT") from None


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def parse_json(raw: bytes | str, *, max_bytes: int = MAX_RECORD_BYTES) -> Any:
    try:
        data = raw.encode("utf-8") if isinstance(raw, str) else raw
        if len(data) > max_bytes:
            raise ContractError("INPUT_TOO_LARGE")
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_object,
                           parse_constant=_invalid_constant)
        _normalize(value)  # Bound nesting and reject invalid Unicode/overflowed floats.
        return value
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise ContractError("INVALID_INPUT") from None


def decode_model[T: FrozenModel](model: type[T], raw: bytes | str,
                                *, max_bytes: int = MAX_RECORD_BYTES) -> T:
    value = parse_json(raw, max_bytes=max_bytes)
    try:
        # JSON strict mode accepts JSON arrays for immutable tuples and ISO timestamps.
        return model.model_validate_json(canonical_bytes(value), strict=True)
    except ValidationError:
        raise ContractError("INVALID_INPUT") from None
