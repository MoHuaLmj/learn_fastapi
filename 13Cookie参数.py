from fastapi import FastAPI

app = FastAPI()

# ============ Cookie 参数 ============
# 可以像定义 Query 和 Path 参数一样定义 Cookie 参数

# 1.导入 Cookie
from fastapi import Cookie
from typing import Annotated

# 2.声明 Cookie 参数
# 3.使用
@app.get("/items/")
async def read_items(ads_id: Annotated[str | None, Cookie()] = None):
    return {"ads_id": ads_id}