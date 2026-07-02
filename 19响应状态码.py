from fastapi import FastAPI, status

app = FastAPI()

# ============ 响应状态码 ============
# 与指定响应模型的方式相同，你也可以在任何路径操作中使用参数 status_code 来声明用于响应的 HTTP 状态码
# 包括: GET/POST/PUT/DELETE等

# status_code 参数接收一个代表 HTTP 状态码的数字
# 它会在响应中返回该状态码 并 在 OpenAPI 模式（以及用户界面）中将其记录下来。
@app.post("/items/", status_code=221)
async def create_item(name: str):
    return {"name": name}

# 但你不必强行记忆这些代码的含义
# 你可以使用 fastapi.status 提供的便捷变量
@app.post("/items/", status_code=status.HTTP_200_OK)
async def create_item(name: str):
    return {"name": name}