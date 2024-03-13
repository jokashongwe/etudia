from pydantic import Field
from backend.classes.object_id import PydanticObjectId
from typing import Optional
from backend.model import Model
from datetime import datetime

class CourseNote(Model):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    slug: Optional[str]
    file_hash: Optional[str]
    desc_text: str
    course: str
    promotion: str
    source: Optional[str]
    added_dt: Optional[datetime]
    userid: Optional[str]

    