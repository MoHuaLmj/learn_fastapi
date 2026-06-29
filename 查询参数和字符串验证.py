from fastapi import FastAPI

app = FastAPI()


# 查询参数 q 的类型是 str | None，这意味着它是 str 类型，但也可以是 None
@app.get("/items/")
async def read_items(q: str | None = None):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# ============ 额外验证 ============

# 1. 导入 Query 和 Annotated
from typing import Annotated
from fastapi import Query


# 2.在 q 参数的类型中使用 Annotated —— 将 Query 放入 Annotated 中，并将 max_length 参数设置为 50
# Annotated[原始类型, 元数据1, 元数据2, ...]
# 在 Annotated 中使用 Query 时，你不能使用 Query 的 default 参数
@app.get("/itemsr/")
async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
    results = {
        "items" : [
            {"item_id" : "Foo"},
            {"item_id" : "Bar"}
        ]
    }
    if q:
        results.update({"q" : q})
    return results