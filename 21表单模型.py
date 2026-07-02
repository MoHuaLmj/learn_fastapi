from fastapi import FastAPI

app = FastAPI()

# ============ 表单模型 ============
# 你可以使用 Pydantic 模型 在 FastAPI 中声明 表单字段

# 你只需要定义一个 Pydantic 模型，其中包含你希望作为 表单字段 接收的字段，然后将该参数声明为 Form
from typing import Annotated
from fastapi import Form
from pydantic import BaseModel

class FormData(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data

# FastAPI 将会从请求的 表单数据 中 提取 每个字段 的数据，并为你提供你所定义的 Pydantic 模型。



# 禁止额外的表单字段
# 在某些特殊的使用场景下（可能不太常见），你可能希望 限制 表单字段，
# 只允许接收 Pydantic 模型中声明的字段，并 禁止 任何 额外 的字段
# 可以使用 Pydantic 的模型配置来 forbid 任何 extra 字段
class FormData(BaseModel):
    username: str
    password: str
    model_config = {
        "extra" : "forbid"
    }

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data