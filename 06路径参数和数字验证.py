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

# ============ 按需排列参数 及 技巧 ============
# 当使用 Annotated 的时候就不需要考虑该内容
# 不使用 Annotated 的时候需要参考该部分内容
# 具体参考: https://fastapi.org.cn/tutorial/path-params-numeric-validations/#order-the-parameters-as-you-need


# ============ 数值校验：大于或等于 ============
# item_id: Annotated[int, Path(title="The ID of the item to get", ge=1)]
# ge: 'g'reater than or 'e'qual（大于或等于）
# gt：'g'reater 't'han（大于）
# le：'l'ess than or 'e'qual（小于或等于）
# lt：'l'ess 't'han（小于）
# 数值校验也适用于 float 值
@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="The ID of the item to get", gt=0, le=1000)],
    q: str,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results