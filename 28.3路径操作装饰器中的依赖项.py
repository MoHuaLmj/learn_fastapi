from fastapi import FastAPI

app = FastAPI()

# ============ 路径操作装饰器中的依赖项 ============
# 在某些情况下，你并不需要在 路径操作函数 内部使用依赖项的返回值。
# 或者该依赖项根本不会返回任何值。
# 但你仍然需要执行或解析它。
# 对于这些情况，你无需在 路径操作函数 中声明带有 Depends 的参数，
# 而是可以将一个包含 dependencies 的 list 添加到 路径操作装饰器 中。

# ===== 在 路径操作装饰器 中添加 dependencies =====
# 路径操作装饰器 接收一个可选参数 dependencies
# 它应该是一个包含 Depends() 的 list
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException

async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key

@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]

# 这些依赖项将以与普通依赖项相同的方式执行/解析。
# 但它们的值（如果它们有返回值）不会被传递给你的 路径操作函数。
