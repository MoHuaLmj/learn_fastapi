from fastapi import FastAPI

app = FastAPI()

# ============ Body - Fields ============
# 正如你可以使用 Query、Path 和 Body 在路径操作函数参数中声明额外的校验和元数据一样，
# 你也可以在 Pydantic 模型中使用 Pydantic 的 Field 来声明校验和元数据。

#实际上，你接下来会看到的 Query、Path 等，创建的是通用 Param 类的子类对象，
# 而该类本身又是 Pydantic 的 FieldInfo 类的子类。
# 而 Pydantic 的 Field 返回的也是 FieldInfo 的一个实例。
# Body 也直接返回 FieldInfo 子类的对象。后面你还会看到其他类，它们是 Body 类的子类。
# 请记住，当你从 fastapi 导入 Query、Path 等时，它们实际上是返回特殊类的函数。

# 注意每个带有类型、默认值和 Field 的模型属性，其结构与路径操作函数的参数相同，
# 只是将 Path、Query 和 Body 替换成了 Field。

# 1.导入 Field
from pydantic import BaseModel, Field
from fastapi import Body, Path
from typing import Annotated

# 2.声明模型属性
# Field 的工作方式与 Query、Path 和 Body 相同，它拥有所有相同的参数等
class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300, min_length=10
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None

@app.put("/items/{item_id}")
async def update_item(item_id: Annotated[int, Path()], item: Annotated[Item | None, Body(embed=True)] = None):
    results = {"item_id": item_id, "item": item}
    return results

# ============ 添加额外信息 ============
# 你可以在 Field、Query、Body 等中声明额外信息。这些信息会被包含在生成的 JSON Schema 中。
# 在后续文档学习如何声明示例（examples）时，你将了解更多关于添加额外信息的内容。

# 传递给 Field 的额外键（key）也会出现在应用程序生成的 OpenAPI 模式中。
# 由于这些键不一定是 OpenAPI 规范的一部分，
# 某些 OpenAPI 工具（例如 OpenAPI 验证器）可能无法处理你生成的模式。