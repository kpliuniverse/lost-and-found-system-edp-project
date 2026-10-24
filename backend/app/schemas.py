from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

Status = Literal["lost", "found"]


class ItemCreate(BaseModel):
    """What the browser sends when someone reports an item."""

    status: Status
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(default="", max_length=2000)
    category: str = Field(min_length=1, max_length=40)
    location: str = Field(min_length=2, max_length=160)
    event_date: date
    contact_name: str = Field(min_length=2, max_length=80)
    contact_info: str = Field(min_length=3, max_length=120)
    pin: str = Field(min_length=4, max_length=20)
    image_filenames: Optional[list[str]] = None

    @field_validator("image_filenames", mode="before")
    @classmethod
    def validate_image_input(cls, value):
        if value is not None and len(value) > 8:
            raise ValueError("Eight photo limit")
        return value
    @field_validator(
        "title", "description", "category", "location", "contact_name", "contact_info",
        mode="before",
    )
    @classmethod
    def trim_spaces(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("event_date")
    @classmethod
    def not_in_future(cls, value: date):
        if value > date.today():
            raise ValueError("Date cannot be in the future")
        return value

class ImageModel(BaseModel):
    """The image that is returned alongside ItemOut"""

    model_config = ConfigDict(from_attributes=True)

    id: int

class ItemOut(BaseModel):
    """What the browser gets back. The PIN is never included."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: Status
    title: str
    description: str
    category: str
    location: str
    event_date: date
    contact_name: str
    contact_info: str
    is_resolved: bool
    created_at: datetime
    image_filenames: list[ImageModel] = Field(validation_alias="images")
    
