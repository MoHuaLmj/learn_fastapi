from fastapi import FastAPI

app = FastAPI()

# GET 中使用请求体
# 要发送数据，你应该使用以下方法之一：POST（最常见）、PUT、DELETE 或 PATCH。
# 在 GET 请求中发送请求体在规范中定义不明，尽管如此，FastAPI 仍然支持它，仅用于非常复杂/极端的用例。
# 由于不推荐这样做，使用 GET 时，Swagger UI 的交互式文档不会显示请求体的文档，且中间代理服务器可能不支持。

from pydantic import BaseModel

# 1.创建数据模型 - 使用 pydantic
# 当模型属性具有默认值时，它不是必需的。否则，它是必需的。使用 None 可以使其成为可选。
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# 2.声明为参数 - 和 路径参数 与 查询参数 一样
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    return item_dict

# ============ 请求体 + 路径参数 + 查询参数 ============
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result