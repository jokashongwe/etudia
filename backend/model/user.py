
from pydantic import Field
from backend.classes.object_id import PydanticObjectId
from typing import Optional
from backend.model import Model

class User(Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    phone: str
    fullname: str
    source: Optional[str]
    photo: Optional[str]

    