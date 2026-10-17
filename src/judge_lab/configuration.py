"""Bounded JSON/YAML configuration; aliases, duplicate keys and executable tags reject."""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from judge_lab.contracts import ContractError, FrozenModel
from judge_lab.load import read_bounded
from judge_lab.serialization import MAX_RECORD_BYTES, canonical_bytes, decode_model


def _mapping(loader: Any, node: Any) -> dict[str, Any]:
    pairs = loader.construct_pairs(node, deep=True)
    result: dict[str, Any] = {}
    for key, value in pairs:
        if not isinstance(key, str) or key in result:
            raise ContractError("INVALID_INPUT")
        result[key] = value
    return result


def read_config[T: FrozenModel](model: type[T], path: Path) -> T:
    raw = read_bounded(path, MAX_RECORD_BYTES)
    if path.suffix.lower() not in (".yaml", ".yml"):
        return decode_model(model, raw)
    try:
        depth = 0
        for count, event in enumerate(yaml.parse(raw)):
            if isinstance(event, (yaml.MappingStartEvent, yaml.SequenceStartEvent)):
                depth += 1
            elif isinstance(event, (yaml.MappingEndEvent, yaml.SequenceEndEvent)):
                depth -= 1
            if isinstance(event, yaml.AliasEvent) or count > 10000 or depth > 32:
                raise ContractError("INVALID_INPUT")
        class UniqueLoader(yaml.SafeLoader):  # type: ignore[misc]
            pass
        UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)
        value = yaml.load(raw, Loader=UniqueLoader)
        return decode_model(model, canonical_bytes(value))
    except (yaml.YAMLError, UnicodeError, ValueError, TypeError, RecursionError):
        raise ContractError("INVALID_INPUT") from None
