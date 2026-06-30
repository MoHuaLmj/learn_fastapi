from fastapi import FastAPI

app = FastAPI()

# ============ 查询参数模型 ============
# 如果你有一组相关的查询参数，你可以创建一个 Pydantic 模型来声明它们。
# 这样你就可以在多个地方重用该模型，并且可以一次性声明所有参数的验证和元数据

# 1. 使用 pydantic 模型的查询参数
from pydantic import BaseModel, Field
from fastapi import Query
from typing import Annotated, Literal

class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=1000)
    offset: float = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []
    
# 2. 使用
@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query

# ============ 禁止额外的查询参数 ============
# 可以使用 Pydantic 的模型配置来 forbid 任何 extra 字段, 用于限制所接收的查询参数。
# 即除了 FilterParams 中定义的字段，禁止前端发送任何其余字段

# 1.使用 pydantic 的 模型配置 禁止 extra 字段
class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}
    
    limit: int = Field(100, gt=0, le=1000)
    offset: float = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []
    
# 2.使用
@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query