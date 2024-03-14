
from pydantic import Field
from backend.classes.object_id import PydanticObjectId
from typing import Optional
from ..model import Model
from datetime import datetime

class UserNote(Model):
    user_id: str
    note_id: str
    added_dt: datetime
    views : int 

    