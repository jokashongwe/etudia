
from pydantic import Field
from backend.classes.object_id import PydanticObjectId
from typing import Optional
from ..model import Model
from datetime import datetime

class User(Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    phone: str
    fullname: str
    otp: Optional[str]
    source: Optional[str]
    photo: Optional[str]
    added_dt: Optional[datetime]
    