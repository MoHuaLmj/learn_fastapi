from fastapi import FastAPI

app = FastAPI()

# ============ 处理错误 ============
# 在很多情况下，你需要向使用 API 的客户端通知错误
# 可能需要告知客户端出现了各种问题
# 在这种情况下，你通常会返回一个 HTTP 状态码，范围在 400 之间（400 到 499）
# 400 系列的状态码则意味着客户端出现了错误

# ============ 使用 HTTPException ============
# 要向客户端返回带有错误的 HTTP 响应，请使用 HTTPException
# 1.导入 HTTPException
from fastapi import HTTPException

items = {"foo": "The Foo Wrestlers"}

# 2.在代码中引发 HTTPException
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}

# HTTPException 是一个普通的 Python 异常，带有 API 相关的额外数据
# 这也意味着，如果你在调用 路径操作函数 内部的某个工具函数时引发了 HTTPException，
# 它将不会执行 路径操作函数 中剩余的代码，而是会立即终止该请求，
# 并将 HTTPException 中的 HTTP 错误发送给客户端

# 与返回一个值相比，引发异常的优势将在关于“依赖项”和“安全性”的章节中更加明显

# 如果客户端请求 http://example.com/items/foo（item_id 为 "foo"），
# 该客户端将收到 200 的 HTTP 状态码，以及如下 JSON 响应：
{
  "item": "The Foo Wrestlers"
}
# 但如果客户端请求 http://example.com/items/bar（一个不存在的 item_id "bar"），
# 该客户端将收到 404 的 HTTP 状态码（“未找到”错误），以及如下 JSON 响应：
{
  "detail": "Item not found"
}
# 引发 HTTPException 时，你可以将任何可转换为 JSON 的值作为 detail 参数传递，而不限于 str。
# 你可以传递 dict、list 等。它们会被 FastAPI 自动处理并转换为 JSON。


# ============ 添加自定义响应头 ============
# 在某些情况下，为 HTTP 错误添加自定义响应头是有用的。例如，用于某些类型的安全性验证。
items = {"foo": "The Foo Wrestlers"}

@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}

# ============ 安装自定义异常处理器 ============
# 你可以使用 来自 Starlette 的相同异常工具 添加自定义异常处理器。
# 假设你有一个自定义异常 UnicornException，你（或你使用的库）可能会 raise 它。
# 并且你希望使用 FastAPI 全局处理此异常。
# 你可以使用 @app.exception_handler() 添加自定义异常处理器。
from fastapi import Request
from fastapi.responses import JSONResponse

class UnicornException(Exception):
    def __init__(self, name: str, *args):
        super().__init__(*args)
        self.name = name
        
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
    
@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}
# 你也可以使用 from starlette.requests import Request 和 from starlette.responses import JSONResponse。

# FastAPI 提供了与 starlette.responses 相同的 fastapi.responses，这仅仅是为了方便开发者。
# 但大多数可用的响应直接来自 Starlette。Request 也是如此。


# ============ 覆盖默认的异常处理器 ============
# FastAPI 有一些默认的异常处理器。
# 这些处理器负责在 raise HTTPException 以及请求数据无效时返回默认的 JSON 响应。
# 你可以用自己的处理器覆盖这些异常处理器。


# 覆盖请求验证异常
# 当请求包含无效数据时，FastAPI 内部会引发 RequestValidationError。
# 它同时也包含了一个默认的异常处理器。

# 要覆盖它，请导入 RequestValidationError，并使用 
# @app.exception_handler(RequestValidationError) 来装饰该异常处理器。

# 该异常处理器将接收一个 Request 和该异常对象。
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(status_code=exc.status_code, content=str(exc.detail))

# 覆盖 HTTPException 错误处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    message = "Validation errors:"
    for error in exc.errors():
        message += f"\nField: {error['loc']}, Error: {error['msg']}"
    return PlainTextResponse(message, status_code=400)

@app.get("/itemsa/{item_id}")
async def read_itema(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}


# 使用 RequestValidationError 的请求体
# RequestValidationError 包含了它所接收到的包含无效数据的 body
# 你可以在开发应用程序时使用它来记录 body 并进行调试，或将其返回给用户等
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

class Item(BaseModel):
    title: str
    size: int

@app.post("/itemsd/")
async def create_item(item: Item):
    return item


# FastAPI 的 HTTPException 与 Starlette 的 HTTPException

# FastAPI 的 HTTPException 错误类继承自 Starlette 的 HTTPException 错误类
# 唯一的区别是 FastAPI 的 HTTPException 接受任何可 JSON 序列化的数据作为 detail 字段，
# 而 Starlette 的 HTTPException 只接受字符串。

# 因此，你可以像往常一样在代码中继续引发 FastAPI 的 HTTPException。
# 但当你注册异常处理器时，你应该注册 Starlette 的 HTTPException。

# 这样，如果 Starlette 的内部代码、Starlette 扩展
# 或插件引发了 Starlette HTTPException，你的处理器将能够捕获并处理它。

# 在此示例中，为了在同一代码中同时使用这两种 HTTPException，
# Starlette 的异常被重命名为 StarletteHTTPException。


# 复用 FastAPI 的异常处理器

# 如果你想在使用异常的同时使用 FastAPI 的默认异常处理器，
# 你可以导入并复用来自 fastapi.exception_handlers 的默认异常处理器

# 1.导入
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 复用
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {repr(exc)}")
    return await http_exception_handler(request, exc)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}