from fastapi import FastAPI

app = FastAPI()

# ============ 路径参数验证 ============

# 1.导入 Path
from typing import Annotated
from fastapi import FastAPI, Path, Query

# 路径参数总是必需的，因为它必须是路径的一部分。
# 即使你用 None 声明它或设置了默认值，也不会有任何影响，它仍然是必需的。
# 2. 声明元数据
# 3. 使用Path
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.get("/itemsr/{item_id}")
async def read_itemsr(q: str, item_id: int = Path(title="The ID of the item to get")):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results