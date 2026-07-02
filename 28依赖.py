from fastapi import FastAPI

app = FastAPI()

# ============ 依赖 ============


# ===== 第一步 =====
# 1.创建依赖项或“可依赖对象”
# 依赖项只是一个函数，可以接收路径操作函数所能接收的所有相同参数
# 你可以将其视为没有“装饰器”（没有 @app.get("/some-path")）的路径操作函数。

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

# 2.导入 Depends
from fastapi import Depends
from typing import Annotated

# 3.在“从属对象”中声明依赖项
# 就像在路径操作函数参数中使用 Body、Query 等一样，在新参数中使用 Depends
@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

@app.get("/users/")
async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

# 尽管你在函数的参数中以与使用 Body、Query 等相同的方式使用 Depends，但 Depends 的工作方式略有不同。
# 你只给 Depends 提供一个参数。此参数必须类似于函数。
# 你不要直接调用它（不要在末尾添加括号），只需将其作为参数传递给 Depends()。
# 该函数以与路径操作函数相同的方式接收参数。

# 每当有新请求到达时，FastAPI 将负责:
# 用正确的参数调用你的依赖项（“可依赖对象”）函数。
# 获取函数的结果。
# 将该结果分配给你的路径操作函数中的参数。
# graph TB

# common_parameters(["common_parameters"])
# read_items["/items/"]
# read_users["/users/"]

# common_parameters --> read_items
# common_parameters --> read_users

# 这样你就只需编写一次共享代码，FastAPI 就会负责为你的路径操作调用它。

# ===== 共享 Annotated 依赖项 =====
# 因为我们使用了 Annotated，我们可以将该 Annotated 值存储在一个变量中，并在多个地方使用它

CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.get("/items/")
async def read_items(commons: CommonsDep):
    return commons


@app.get("/users/")
async def read_users(commons: CommonsDep):
    return commons

# 依赖项将按预期继续工作，最棒的部分是类型信息将被保留，
# 这意味着你的编辑器将能够继续为你提供自动补全、行内错误提示等。其他工具（如 mypy）也是如此

# ===== 是否使用 async =====
# 由于依赖项也会由 FastAPI 调用（与你的路径操作函数相同），因此定义函数时适用相同的规则。
# 你可以使用 async def 或普通的 def。
# 你可以在普通的 def 路径操作函数中声明 async def 依赖项，或者在 async def 路径操作函数中声明 def 依赖项，等等。
# 这无关紧要。FastAPI 会知道怎么做。


# ===== 与 OpenAPI 集成 =====
# 你的依赖项（和子依赖项）的所有请求声明、验证和要求都将集成在同一个 OpenAPI 模式中
# 因此，交互式文档也将包含来自这些依赖项的所有信息

# ===== 简单用法 =====
# 路径操作函数被声明为在路径和操作匹配时使用，然后 FastAPI 负责用正确的参数调用该函数，并从请求中提取数据。

# 事实上，所有（或大多数）Web 框架都以这种相同的方式工作。

# 你从不直接调用这些函数。它们是由你的框架（在本例中为 FastAPI）调用的。

# 借助依赖注入系统，你还可以告诉 FastAPI，你的路径操作函数还“依赖”于
# 其他需要在你的路径操作函数之前执行的事物，FastAPI 将负责执行它并“注入”结果。

# 对于这种“依赖注入”的概念，其他常用术语包括：

# 资源 (resources)
# 提供程序 (providers)
# 服务 (services)
# 可注入对象 (injectables)
# 组件 (components)

# ===== FastAPI 插件 =====
# 可以使用 依赖注入 系统构建集成和“插件”。但实际上，根本不需要创建“插件”，
# 因为通过使用依赖项，可以声明无限数量的集成和交互，这些集成和交互可供你的路径操作函数使用。

# 而且依赖项可以以非常简单直观的方式创建，让你能够
# 只需导入所需的 Python 包，并字面上在几行代码内将它们与你的 API 函数集成。


# ===== FastAPI 兼容性 =====
# 依赖注入系统的简洁性使 FastAPI 能够兼容：

# 所有关系型数据库
# NoSQL 数据库
# 外部包
# 外部 API
# 身份验证和授权系统
# API 使用监控系统
# 响应数据注入系统
# 等等。


# ===== 简单而强大 =====
# 尽管分层依赖注入系统定义和使用起来非常简单，但它仍然非常强大。

# 你可以定义依赖项，而这些依赖项本身又可以定义其他依赖项。

# 最终，将构建出一棵分层的依赖树，
# 依赖注入 系统会负责为你解决所有这些依赖项（及其子依赖项），并在每个步骤提供（注入）结果

# 例如，假设你有 4 个 API 端点（路径操作）

# /items/public/
# /items/private/
# /users/{user_id}/activate
# /items/pro/
# 那么你可以仅使用依赖项和子依赖项为它们中的每一个添加不同的权限要求:

# graph TB

# current_user(["current_user"])
# active_user(["active_user"])
# admin_user(["admin_user"])
# paying_user(["paying_user"])

# public["/items/public/"]
# private["/items/private/"]
# activate_user["/users/{user_id}/activate"]
# pro_items["/items/pro/"]

# current_user --> active_user
# active_user --> admin_user
# active_user --> paying_user

# current_user --> public
# active_user --> private
# admin_user --> activate_user
# paying_user --> pro_items


# ===== 与 OpenAPI 集成 =====
# 所有这些依赖项在声明其要求的同时，也向你的路径操作添加了参数、验证等。
# FastAPI 会负责将所有这些添加到 OpenAPI 模式中，以便它们显示在交互式文档系统中。