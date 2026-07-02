from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# ============ 声明请求示例数据 ============
# 可以为应用接收的数据声明示例，以下是几种实现方式:

# 1.Pydantic 模型中的额外 JSON Schema 数据
# 这些额外信息将按原样添加到该模型的 JSON Schema 输出中，并会被用于 API 文档。
# 你可以使用 model_config 属性，它接收一个 dict，详见:https://docs.pydantic.org.cn/latest/api/config/
# 你可以设置 "json_schema_extra" 为一个包含任何你想在生成的 JSON Schema 中显示的额外数据的 dict，包括 examples
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }
    }
    
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results

# 2.Field 的额外参数
# 当在 Pydantic 模型中使用 Field() 时，你也可以声明额外的 examples
from pydantic import BaseModel, Field
class Itemu(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(default=None, examples=["A very nice Item"])
    price: float = Field(examples=[35.4])
    tax: float | None = Field(default=None, examples=[3.2])
    
@app.put("/itemsu/{item_id}")
async def update_itemu(item_id: int, item: Itemu):
    results = {"item_id": item_id, "item": item}
    return results

# 3.JSON Schema 中的 examples - OpenAPI
# 当使用以下任何一种时Path()、Query()、Header()、Cookie()、Body()、Form()、File()
# 可以声明一组带有额外信息的 examples，它们将被添加到 OpenAPI 内的 JSON Schema 中:

from typing import Annotated
from fastapi import Body
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results

# 也可以传入多个 examples
# 然而，在 编写本文时，负责显示文档 UI 的 Swagger UI 工具并不支持显示 JSON Schema 数据中的多个示例
@app.put("/itemsr/{item_id}")
async def update_itemr(
    *,
    item_id: int,
    item: Annotated[
        Item,
        Body(
            examples=[
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
                {
                    "name": "Bar",
                    "price": "35.4",
                },
                {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            ],
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results

# OpenAPI 特有的 examples
# ============ 使用 openapi_examples 参数 ============
# 你可以通过 openapi_examples 参数在 FastAPI 中声明 OpenAPI 特有的 examples
# 用于Path()、Query()、Header()、Cookie()、Body()、Form()、File()
# dict 的键标识每个示例，每个值是另一个 dict。
# examples 中每个特定的示例 dict 可以包含：
# summary：示例的简短描述。
# description：可以包含 Markdown 文本的长描述。
# value：实际展示的示例，例如一个 dict。
# externalValue：value 的替代方案，一个指向该示例的 URL。虽然可能不像 value 那样被广泛工具支持。
@app.put("/itemso/{item_id}")
async def update_itemo(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
):
    results = {"item_id": item_id, "item": item}
    return results