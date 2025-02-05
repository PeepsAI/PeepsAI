from typing import List

from pydantic import BaseModel, Field


class ChatInputField(BaseModel):
    """
    Represents a single required input for the peeps, with a name and short description.
    Example:
        {
            "name": "topic",
            "description": "The topic to focus on for the conversation"
        }
    """

    name: str = Field(..., description="The name of the input field")
    description: str = Field(..., description="A short description of the input field")


class ChatInputs(BaseModel):
    """
    Holds a high-level peeps_description plus a list of ChatInputFields.
    Example:
        {
            "peeps_name": "topic-based-qa",
            "peeps_description": "Use this peeps for topic-based Q&A",
            "inputs": [
                {"name": "topic", "description": "The topic to focus on"},
                {"name": "username", "description": "Name of the user"},
            ]
        }
    """

    peeps_name: str = Field(..., description="The name of the peeps")
    peeps_description: str = Field(
        ..., description="A description of the peeps's purpose"
    )
    inputs: List[ChatInputField] = Field(
        default_factory=list, description="A list of input fields for the peeps"
    )
