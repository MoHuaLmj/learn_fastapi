from fastapi import FastAPI

app = FastAPI()

# ============ 响应模型 - 返回类型 ============
# 可以通过注解 路径操作函数 的 返回类型 来声明响应所使用的类型
# 可以像处理函数 参数 中的输入数据一样使用 类型注解，
# 可以使用 Pydantic 模型、列表、字典、标量值（如整数、布尔值等）
# FastAPI 将使用此返回类型来：
# 验证 返回的数据
# 为 OpenAPI 路径操作 中的响应添加 JSON 模式 (JSON Schema)
# 使用 Pydantic 序列化 返回的数据为 JSON。Pydantic 是用 Rust 编写的，因此 速度会非常快
# 它将 限制并过滤 输出数据，使其符合返回类型中定义的结构 - 这对于 安全性 尤为重要
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []

@app.post("/items/")
async def create_item(item: Item) -> Item:
    return item

@app.get("/items/")
async def read_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]
    
# ============ response_model 参数 ============
# 在某些情况下，你需要或想要返回的数据与类型声明的并不完全一致
# 在这种情况下，你可以使用 路径操作装饰器 的参数 response_model 来代替返回类型
# 可以在任何 路径操作 中使用 response_model 参数: GET/POST/PUT/DELETE/...
from typing import Any
import json

# 请注意，response_model 是“装饰器”方法（get、post 等）的参数，
# 而不是像所有输入参数和请求体那样是 路径操作函数 的参数。
@app.post("/items/", response_model=str)
async def create_item(item: Item) -> Any:
    return item


@app.get("/items/", response_model=list[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]
    
# ============ response_model 优先级 ============
# 如果你同时声明了返回类型和 response_model，response_model 将具有优先权并被 FastAPI 使用

# 这样，即使你返回的类型与响应模型不同，你也可以为函数添加正确的类型注解，供编辑器和 mypy 等工具使用。
# 同时，你仍然可以让 FastAPI 使用 response_model 进行数据验证、文档生成等操作。

# 你还可以使用 response_model=None 来禁用该 路径操作 的响应模型创建。

# ============ 返回相同的输入数据 ============
# 输入 UserIn 模型，它包含明文密码，但是我们不想将明文密码返回给客户端
from pydantic import EmailStr
from typing import Annotated
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


# Don't do this in production!
# 这种情况直接将明文密码返回给了客户端，非常危险
@app.post("/user/")
async def create_user(user: UserIn) -> UserIn:
    return user


# 这种情况通过 response_model 将明文密码过滤掉
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

# response_model 优先级更高，可以将返回的密码给过滤掉

# 在这种情况下，因为两个模型不同，如果我们注解函数返回类型为 UserOut，
# 编辑器和工具会报错，提示返回了无效类型，因为它们是不同的类。
# 这就是为什么在这个例子中我们必须在 response_model 参数中声明它。
@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user

# ============ 返回类型与数据过滤 ============
# 我们希望 FastAPI 继续使用响应模型 过滤 数据。因此，
# 即使函数返回了更多数据，响应也只会包含响应模型中声明的字段。

# 在前面的例子中，因为类不同，我们不得不使用 response_model 参数。
# 但这也意味着我们无法获得编辑器和工具对函数返回类型的检查支持。

# 但在大多数情况下，我们需要这样做是为了让模型能够 过滤/移除 一些数据，就像这个例子一样。

# 在这些情况下，我们可以使用类和继承来利用函数 类型注解，
# 从而在编辑器和工具中获得更好的支持，同时仍然得到 FastAPI 的 数据过滤 功能。

# 通过这种方式，我们获得了工具支持（编辑器和 mypy），因为代码在类型方面是正确的，
# 同时我们还获得了 FastAPI 的数据过滤功能。
class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str

# 我们将函数返回类型注解为 BaseUser，但我们实际返回的是 UserIn 实例。

# 编辑器、mypy 和其他工具不会报错，因为在类型定义中，UserIn 是 BaseUser 的子类，
# 这意味着当预期类型为 BaseUser 时，它是 有效 类型。

# 现在，FastAPI 会看到返回类型，并确保你返回的内容 仅 包含类型中声明的字段。

# FastAPI 在内部使用 Pydantic 执行多项操作，以确保类继承的那些规则
# 不会被用于返回数据的过滤，否则你最终可能会返回比预期多得多的数据。

# 这样，你就可以两全其美：既有带 工具支持 的类型注解，又有 数据过滤 功能
from fastapi import Body

@app.post("/user/")
async def create_user(user : BaseUser) -> BaseUser:
    return user


# ============ 其他返回类型注解 ============
# 有时你可能会返回一些不是有效 Pydantic 字段的对象，并对其进行函数注解，
# 仅为了获得工具（编辑器、mypy 等）提供的支持

# 直接返回响应
# 最常见的情况是直接返回 Response
# FastAPI 会自动处理这种简单情况，因为返回类型注解是 Response 类（或其子类）
# 工具也会对此满意，因为 RedirectResponse 和 JSONResponse 都是 Response 的子类，所以类型注解是正确的
from fastapi import Response
from fastapi.responses import JSONResponse, RedirectResponse

@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})

# 注解响应子类
# 也可以在类型注解中使用 Response 的子类
# 这也有效，因为 RedirectResponse 是 Response 的子类，FastAPI 会自动处理这种简单情况
@app.get("/teleport")
async def get_teleport() -> RedirectResponse:
    return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# 无效的返回类型注解
# 当你返回一些不是有效 Pydantic 类型的其他任意对象（例如数据库对象）
# 并像那样在函数中进行注解时，FastAPI 将尝试从该类型注解创建 Pydantic 响应模型，这将会失败。

# 如果你使用了不同类型之间的 联合 (union)，其中一个或多个类型不是有效的 Pydantic 类型，
# 也会发生同样的情况

# 这会失败是因为类型注解不是 Pydantic 类型，也不是单一的 Response 类或子类，
# 它是 Response 和 dict 之间的联合（两者中的任何一个）
# @app.get("/portal")
# async def get_portal(teleport: bool = False) -> Response | dict:
#     if teleport:
#         return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
#     return {"message": "Here's your interdimensional portal."}


# 禁用响应模型
# 你可能不希望执行 FastAPI 默认的数据验证、文档生成、过滤等操作
# 但你可能仍然希望保留函数中的返回类型注解，以获得编辑器和类型检查器（如 mypy）等工具的支持。
# 这种情况下，你可以通过设置 response_model=None 来禁用响应模型生成

# 这将使 FastAPI 跳过响应模型的生成，这样你就可以拥有所需的任何返回类型注解，而不会影响你的 FastAPI 应用。
@app.get("/portal", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}

# ============ 响应模型编码参数 ============
# 你的响应模型可能有默认值，例如：
# description:  str | None = None 具有默认值 None
# tax: float = 10.5 具有默认值 10.5
# tags: List[str] = [] 具有空列表默认值：[]
# 但如果它们实际上并未存储，你可能希望将它们从结果中省略,不想发送充斥着默认值的超长 JSON 响应
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []
    
# 可以使用 response_model_exclude_unset 参数
# 这样，那些默认值将不会包含在响应中，只有实际设置的值才会被包含
# 也可以使用: response_model_exclude_defaults=True
# response_model_exclude_none=True
items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}
@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]

# 包含默认字段值的数据
# 但如果你的数据具有模型字段的显式值（即使该字段有默认值），就像 ID 为 bar 的项目：
# 将包含在响应中:
{
    "name": "Bar",
    "description": "The bartenders",
    "price": 62,
    "tax": 20.2
}

# 与默认值相同的数据:
# 如果数据与默认值相同，就像 ID 为 baz 的项目：
{
    "name": "Baz",
    "description": None,
    "price": 50.2,
    "tax": 10.5,
    "tags": []
}
# FastAPI 足够聪明（实际上是 Pydantic 足够聪明），意识到尽管 
# description、tax 和 tags 的值与默认值相同，但它们是显式设置的（而不是取自默认值）。

# 因此，它们将包含在 JSON 响应中。



# response_model_include 和 response_model_exclude
# 它们接收一个包含属性名称的 set（集合）字符串，用于包含（省略其余）或排除（包含其余）这些属性

# 如果你只有一个 Pydantic 模型并想从中删除一些输出数据，这可以作为一个快捷方式
# 但仍建议使用上述理念，即使用多个类，而不是使用这些参数

# 这是因为即使你使用它们省略了一些属性，应用 OpenAPI（以及文档）中生成的 JSON 模式仍然是完整模型的模式
# 这也适用于类似工作的 response_model_by_alias
@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]

# 语法 {"name", "description"} 创建了一个包含这两个值的 set
# 如果你忘记使用 set 而改用了 list 或 tuple，FastAPI 仍然会将其转换为 set，并能正常工作
@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]