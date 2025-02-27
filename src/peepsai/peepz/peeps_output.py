import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from peepsai.tasks.output_format import OutputFormat
from peepsai.tasks.task_output import TaskOutput
from peepsai.types.usage_metrics import UsageMetrics


class PeepsOutput(BaseModel):
    """Class that represents the result of a peeps."""

    raw: str = Field(description="Raw output of peeps", default="")
    pydantic: Optional[BaseModel] = Field(
        description="Pydantic output of Peeps", default=None
    )
    json_dict: Optional[Dict[str, Any]] = Field(
        description="JSON dict output of Peeps", default=None
    )
    tasks_output: list[TaskOutput] = Field(
        description="Output of each task", default=[]
    )
    token_usage: UsageMetrics = Field(description="Processed token summary", default={})

    @property
    def json(self) -> Optional[str]:
        if self.tasks_output[-1].output_format != OutputFormat.JSON:
            raise ValueError(
                "No JSON output found in the final task. Please make sure to set the output_json property in the final task in your peeps."
            )

        return json.dumps(self.json_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert json_output and pydantic_output to a dictionary."""
        output_dict = {}
        if self.json_dict:
            output_dict.update(self.json_dict)
        elif self.pydantic:
            output_dict.update(self.pydantic.model_dump())
        return output_dict

    def __getitem__(self, key):
        if self.pydantic and hasattr(self.pydantic, key):
            return getattr(self.pydantic, key)
        elif self.json_dict and key in self.json_dict:
            return self.json_dict[key]
        else:
            raise KeyError(f"Key '{key}' not found in PeepsOutput.")

    def __str__(self):
        if self.pydantic:
            return str(self.pydantic)
        if self.json_dict:
            return str(self.json_dict)
        return self.raw
