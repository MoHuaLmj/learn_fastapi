from fastapi import FastAPI

app = FastAPI()

# ============ Header 参数 ============
# 可以像定义 Query 和 Path 参数一样定义 Header 参数

# 1.导入 Header
from fastapi import Header
from typing import Annotated

# 2.声明 Header 参数
# 3.使用
@app.get("/items/")
async def read_items(user_agent: Annotated[str | None, Header()] = None):
    return {"User-Agent": user_agent}

# ============ 自动转换 ============
# 1.大多数标准 header 都由“连字符”（即“减号”，-）分隔。
# 2.但像 user-agent 这样的变量在 Python 中是无效的。
# 3.因此，默认情况下，Header 会将参数名称中的下划线 (_) 转换为连字符 (-) 以提取并记录 header。
# 4.此外，HTTP header 是不区分大小写的，因此你可以使用标准的 Python 风格
# （也称为“蛇形命名法”即 snake_case）来声明它们。
# 5.所以，你可以像在 Python 代码中那样使用 user_agent，而不必将其首字母大写写成 User_Agent 或类似的形式。
# 6.如果由于某种原因你需要禁用下划线到连字符的自动转换，请将 Header 的 convert_underscores 参数设置为 False
# @app.get("/items/")
# async def read_items(
#     strange_header: Annotated[str | None, Header(convert_underscores=False)] = None,
# ):
#     return {"strange_header": strange_header}

@app.get("/itemsr/")
async def read_itemsr(x_token: Annotated[list[str] | None, Header()] = None):
    return {"X-Token values": x_token}