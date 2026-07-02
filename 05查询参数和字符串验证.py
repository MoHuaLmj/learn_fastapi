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
# min_length 参数 : q: Annotated[str | None, Query(min_length=3, max_length=50)] = None
# 正则表达式 : q: Annotated[str | None, Query(min_length=3, max_length=50, pattern="^fixedquery$")] = None
# 需要在使用 Query 时声明一个值是必需的，你可以直接不声明默认值
@app.get("/itemsr/")
async def read_items(q: Annotated[str | None, Query(min_length=3)] = "fixedquery"):
    results = {
        "items" : [
            {"item_id" : "Foo"},
            {"item_id" : "Bar"}
        ]
    }
    if q:
        results.update({"q" : q})
    return results

# ============ 查询参数列表 / 多个值 ============
# 传入 https://:8000/iteml/?q=foo&q=bar
# 响应 {
    # "q": [
    #     "foo",
    #     "bar"
    # ]
    # }
@app.get("/itemsl/")
async def read_itemsl(q : Annotated[list[str] | None, Query()] = None):
    query_items = {"q" : q}
    return query_items


# ============ 声明更多元数据 ============

# 添加一个 title 和 description
# 参数别名 : q: Annotated[str | None, Query(alias="item-query")] = None
# 弃用参数 : q: Annotated[str | None, Query(deprecated=True),] = None
# 排除参数 : q: Annotated[str | None, Query(include_in_schema=False)] = None
@app.get("/itemst/")
async def read_itemst(
    q: Annotated[str | None, 
                 Query(title="Query string", 
                       min_length=3, 
                       description="Query string for the itemst",
                       deprecated=True,
                       include_in_schema=False)]
                         = None
                         ):
    return q

# ============ 自定义验证 ============
# 使用一个自定义验证器函数，它在常规验证之后（例如在验证值确实是 str 之后）执行。
# 你可以通过在 Annotated 中使用 Pydantic 的 AfterValidator 来实现。
# Pydantic 还有 BeforeValidator 等等。

# 例如，这个自定义验证器检查项目 ID 是否以 isbn- 开头（用于 ISBN 书号），或者以 imdb- 开头（用于 IMDB 电影 URL ID）
# 1.导入 AfterVlidator
from pydantic import AfterValidator

# 2. 定义验证函数
def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')

    return id

# 3.使用
@app.get("/itemsc/")
async def read_itemsc(
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
):
    return {"id": id}