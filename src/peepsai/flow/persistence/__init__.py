"""
PeepsAI Flow Persistence.

This module provides interfaces and implementations for persisting flow states.
"""

from typing import Any, Dict, TypeVar, Union

from pydantic import BaseModel

from peepsai.flow.persistence.base import FlowPersistence
from peepsai.flow.persistence.decorators import persist
from peepsai.flow.persistence.sqlite import SQLiteFlowPersistence

__all__ = ["FlowPersistence", "persist", "SQLiteFlowPersistence"]

StateType = TypeVar('StateType', bound=Union[Dict[str, Any], BaseModel])
DictStateType = Dict[str, Any]
