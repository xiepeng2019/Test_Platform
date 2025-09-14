from pydantic import BaseModel, ConfigDict
from typing import Generic, List, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")

class ListResponse(GenericModel, Generic[T]):
    list: List[T] = []
    total: int = 0
