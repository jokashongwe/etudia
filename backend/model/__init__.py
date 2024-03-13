from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder


class Model(BaseModel):
    def to_json(self):
        return jsonable_encoder(self, exclude_none=True, exclude=["desc_text"])

    def to_bson(self):
        data = self.model_dump(by_alias=True, exclude_none=True)
        if data["_id"] is None:
            data.pop("_id")
        return data