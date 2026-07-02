from fastapi import FastAPI, Form
from typing import Annotated

app = FastAPI()

# ============ 表单数据 ============
# 当你需要接收表单字段而不是 JSON 时，可以使用 Form
# 需要先安装 python-multipart

# 创建表单参数的方式与 Body 或 Query 相同, 包括验证、示例、别名等
# 例如，在 OAuth2 规范的使用方式之一（称为“密码流”）中，要求以表单字段的形式发送 username 和 password
# Form 是一个直接继承自 Body 的类
# 要声明表单主体，你需要显式使用 Form，否则参数会被解释为查询参数或主体（JSON）参数
@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}

# 表单数据通常使用“媒体类型” application/x-www-form-urlencoded 进行编码。

# 但当表单包含文件时，它会被编码为 multipart/form-data。你将在下一章中阅读有关处理文件的内容。

# 你可以在路径操作中声明多个 Form 参数，但不能同时声明预期接收为 JSON 的 Body 字段，
# 因为请求体将使用 application/x-www-form-urlencoded 而不是 application/json 进行编码。

# 这不是 FastAPI 的限制，它是 HTTP 协议的一部分。