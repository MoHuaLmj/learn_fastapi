from fastapi import FastAPI

app = FastAPI()

# ============ 混合使用 Path、Query 和请求体参数 ============
from typing import Annotated

from fastapi import Path
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.put("/items/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(title="The ID of the item to get", ge=0, le=1000)],
    q: str | None = None,
    item: Item | None = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results

# ============ 多个请求体参数 ============
# 可以声明多个请求体参数

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None
    
@app.put("/itemsa/{item_id}")
async def update_itema(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

# 这种情况下，FastAPI 会注意到函数中有不止一个请求体参数
# 它会将参数名作为请求体中的键（字段名），并期望请求体格式如下：
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    },
    "user": {
        "username": "dave",
        "full_name": "Dave Grohl"
    }
}

# ============ 请求体中的单个值 ============
# 就像 Query 和 Path，FastAPI 也提供了等效的 Body。
# 例如，扩展之前的模型，你可能决定除了 item 和 user 之外，还想在同一个请求体中增加另一个键 importance。
# 如果你直接声明它，因为这是一个单个值，FastAPI 会默认将其视为查询参数。
# 但你可以使用 Body 指示 FastAPI 将其视为另一个请求体键：
from fastapi import Body

@app.put("/itemsp/{item_id}")
async def update_item(
    item_id: int, item: Item, user: User, importance: Annotated[int, Body()]
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

# 在这种情况下，FastAPI 会期望请求体格式如下：
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    },
    "user": {
        "username": "dave",
        "full_name": "Dave Grohl"
    },
    "importance": 5
}

# ============ 多个请求体参数与查询参数 ============
# 除了任何请求体参数外，还可以根据需要随时声明额外的查询参数。
# 由于单个值默认被解释为查询参数，你无需显式添加 Query，可以直接这样写：
q: str | None = None

# 例如:
@app.put("/itemsq/{item_id}")
async def update_itemq(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body(gt=0)],
    q: str | None = None,
):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results


# ============ 嵌入单个请求体参数 ============
# 假设你只有一个来自 Pydantic 模型 Item 的 item 请求体参数。
# 默认情况下，FastAPI 会直接期望请求体本身。
# 但如果你希望它期望一个带有 item 键的 JSON，并且其内容是模型数据（就像你声明多个请求体参数时那样），
# 你可以使用 Body 的特殊参数 embed：
item: Annotated[Item, Body(embed=True)]

# 例如:
@app.put("/itemsb/{item_id}")
async def update_itemb(item_id: int, item: Annotated[Item, Body(embed=True)]):
    results = {"item_id": item_id, "item": item}
    return results

# 在这种情况下，FastAPI 会期望请求体格式如下：
{
    "item": {
        "name": "Foo",
        "description": "The pretender",
        "price": 42.0,
        "tax": 3.2
    }
}