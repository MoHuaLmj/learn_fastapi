from fastapi import FastAPI

app = FastAPI()

# ============ JSON 兼容编码器 ============
# 在某些情况下，你可能需要将数据类型（例如 Pydantic 模型）转换为与 JSON 兼容的格式（例如 dict、list 等）。

# 例如，如果你需要将其存储在数据库中。

# 为此，FastAPI 提供了 jsonable_encoder() 函数。

# jsonable_encoder接收一个对象（例如 Pydantic 模型），并返回其 JSON 兼容的版本
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from datetime import datetime

fake_db = {}
class Item(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

@app.put("/items/{id}")
def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    print(type(json_compatible_item_data))
    print(json_compatible_item_data)
    fake_db[id] = json_compatible_item_data
    
# 在这个例子中，它会将 Pydantic 模型转换为 dict，并将 datetime 转换为 str
# 调用它的结果是可以被 Python 标准库 json.dumps() 编码的数据
# 它返回的不是包含 JSON 格式数据的长 str（字符串），
# 而是标准的 Python 数据结构（例如 dict），其中所有值和子值都与 JSON 兼容
