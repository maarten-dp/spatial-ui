from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        copy_on_model_validation = False
        underscore_attrs_are_private = True
        arbitrary_types_allowed = True
