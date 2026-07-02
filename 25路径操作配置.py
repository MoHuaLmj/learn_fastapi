from fastapi import FastAPI

app = FastAPI()

# ============ 路径操作配置 ============
# 你可以向路径操作装饰器传递多个参数来对其进行配置
# 这些参数是直接传递给路径操作装饰器的，而不是传递给你的路径操作函数


# ============ 响应状态码 ============
# 你可以定义在路径操作的响应中使用的 (HTTP) status_code
# 该状态码将被用于响应中，并添加到 OpenAPI 模式中
from fastapi import status
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item) -> Item:
    return item



# ============ 标签 ============
# 你可以通过传递包含 str 的 list 参数 tags（通常只有一个 str）为路径操作添加标签
# 它们将被添加到 OpenAPI 模式中，并被自动文档界面所使用
@app.post("/items/", tags=["items"])
async def create_item(item: Item) -> Item:
    return item

@app.get("/items/", tags=["items"])
async def read_items():
    return [{"name": "Foo", "price": 42}]

@app.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "johndoe"}]

# 使用枚举的标签

# 如果你的应用程序很大，最终可能会积累多个标签，你可能希望确保相关路径操作始终使用相同的标签。
# 在这种情况下，将标签存储在 Enum 中是很有意义的。
# FastAPI 对此的支持方式与使用普通字符串一样。
from enum import Enum

class Tags(Enum):
    items = "items"
    users = "users"

@app.get("/items/", tags=[Tags.items])
async def get_items():
    return ["Portal gun", "Plumbus"]

@app.get("/users/", tags=[Tags.users])
async def read_users():
    return ["Rick", "Morty"]


# ============ 摘要和描述 ============
# 你可以添加 summary（摘要）和 description（描述）
@app.post(
    "/itemsd/",
    summary="Create an item",
    description="Create an item with all the information, name, description, price, tax and a set of unique tags",
)
async def create_item(item: Item) -> Item:
    return item



# ============ 从文档字符串中获取描述 ============
# 由于描述往往很长且包含多行，你可以在函数的 
# docstring 中声明路径操作的描述，FastAPI 会从那里读取它。

# 你可以在文档字符串中编写 Markdown，
# 它会被正确解析并显示（会考虑文档字符串的缩进）
@app.post("/items/", summary="Create an item")
async def create_item(item: Item) -> Item:
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item


# ============ 响应描述 ============
# 你可以通过参数 response_description 指定响应描述
@app.post(
    "/itemsa/",
    summary="Create an item",
    response_description="The created item",
)
async def create_itema(item: Item) -> Item:
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return item

# OpenAPI 规定每个路径操作都需要一个响应描述。

# 因此，如果你没有提供，FastAPI 会自动生成一个“Successful response”（成功响应）。



# ============ 弃用路径操作 ============
# 如果你需要将某个路径操作标记为 弃用 (deprecated)，
# 但又不想将其删除，请传递参数 deprecated=True
@app.get("/elements/", tags=["items"], deprecated=True)
async def read_elements():
    return [{"item_id": "Foo"}]