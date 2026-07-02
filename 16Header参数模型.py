from fastapi import FastAPI

app = FastAPI()

# ============ Header 参数模型 ============
# 如果你有一组相关的 Header 参数，你可以创建一个 Pydantic 模型来声明它们
# 使用 Pydantic 模型的 Header 参数
from typing import Annotated

from fastapi import Header
from pydantic import BaseModel

app = FastAPI()


class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.get("/items/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
    return headers

# 禁止额外 Header
class CommonHeaders(BaseModel):
    model_config = {"extra": "forbid"}

    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.get("/items/")
async def read_items(headers: Annotated[CommonHeaders, Header()]):
    return headers

# 禁用下划线转换
# 与常规 Header 参数一样，当参数名称中包含下划线时，它们会自动转换为连字符。
# 例如，如果代码中有一个 Header 参数 save_data，
# 则预期的 HTTP Header 将是 save-data，它也会以这种形式出现在文档中。

class CommonHeaders(BaseModel):
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.get("/items/")
async def read_items(
    headers: Annotated[CommonHeaders, Header(convert_underscores=False)],
):
    return headers