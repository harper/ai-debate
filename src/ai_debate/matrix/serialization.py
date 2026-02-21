"""JSON serialization for matrix tournament results."""

import json
from dataclasses import asdict
from datetime import datetime

from .types import MatrixResult


def _default_serializer(obj: object) -> object:
    """Custom JSON serializer for types not handled by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def matrix_result_to_json(result: MatrixResult) -> str:
    """Serialize a MatrixResult to a JSON string."""
    data = asdict(result)
    # Add computed properties
    data["duration_seconds"] = result.duration_seconds
    return json.dumps(data, indent=2, default=_default_serializer)
