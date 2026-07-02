from fastapi import FastAPI

app = FastAPI()

# ============ 请求体 - 嵌套模型 ============
# 使用 FastAPI，你可以定义、校验、记录并使用任意深度的嵌套模型（得益于 Pydantic）。

# Pydantic 模型的每个属性都有一个类型。
# 但该类型本身也可以是另一个 Pydantic 模型。
# 因此，你可以声明带有特定属性名称、类型和校验的深度嵌套 JSON “对象”。
# 所有这一切，都可以进行任意深度的嵌套。

from pydantic import BaseModel
# 1.定义子模型
class Image(BaseModel):
    url: str
    name: str
    
# 2.将子模型用作类型
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None
    
# 3.使用
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

# 这意味着 FastAPI 将期望收到类似如下的请求体：
{
    "name": "Foo",
    "description": "The pretender",
    "price": 42.0,
    "tax": 3.2,
    "tags": ["rock", "metal", "bar"],
    "image": {
        "url": "http://example.com/baz.jpg",
        "name": "The Foo live"
    }
}

# ============ 特殊类型 与 校验 ============
# 除了像 str、int、float 等常规单一类型外，还可以使用更复杂的单一类型。
# 要查看所有可用选项，请查阅 Pydantic 类型概述：https://docs.pydantic.org.cn/latest/concepts/types/
# 例如，在 Image 模型中我们有一个 url 字段，我们可以将其声明为 Pydantic 的 HttpUrl 实例，而不是 str：
from pydantic import HttpUrl

class Image(BaseModel):
    url: HttpUrl # 该字符串将被校验是否为有效的 URL，并记录在 JSON Schema / OpenAPI 中。
    name: str
    
# ============ 任意 dict 的请求体 ============
# 可以将请求体声明为 dict，并指定键和值的类型。
# 这样，你不必预先知道有效的字段/属性名称是什么（使用 Pydantic 模型则必须预先知道）。
# 这在需要接收未知键的情况下非常有用。
@app.post("/index-weights/")
async def create_index_weights(weights: dict):
    return weights