from pydantic import BaseModel, ConfigDict
from typing import Generic, List, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

class BaseSchema(BaseModel):
    # model_config = ConfigDict(from_attributes=True) 是 Pydantic v2 中用于快速转换 ORM 对象到 Pydantic 模型的关键配置，
    # 解决了 “ORM 对象属性访问” 与 “Pydantic 字典式初始化” 之间的不匹配问题，极大简化了数据库查询结果到 API 响应模型的转换流程。
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")

class ListResponse(GenericModel, Generic[T]):
    list: List[T] = []
    total: int = 0
