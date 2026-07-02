from fastapi import FastAPI

app = FastAPI()

# ============ Cookie 参数模型 ============
# 如果你有一组相关的 Cookie，可以创建一个 Pydantic 模型来声明它们

# 在 Pydantic 模型中声明你需要的 Cookie 参数，然后将该参数声明为 Cookie 类型
from fastapi import Cookie
from pydantic import BaseModel
from typing import Annotated

class Cookies(BaseModel):
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies

# ============ 禁止多余的 Cookie ============
# 在某些特殊的使用场景中（可能不太常见），你可能希望限制所接收的 Cookie
# 你可以使用 Pydantic 的模型配置来 forbid 任何 extra 字段
class Cookies(BaseModel):
    model_config = {"extra": "forbid"}

    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get("/items/")
async def read_items(cookies: Annotated[Cookies, Cookie()]):
    return cookies