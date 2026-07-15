from fastapi import FastAPI, Path, Query, Body, Depends
from typing import Annotated

app = FastAPI()

# ============ 安全性 - 第一步 ============

# 希望前端可以通过 用户名 和 密码 向后端进行身份验证
# 可以使用 OAuth2 通过 FastAPI 实现

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# docs 路径 中 会出现 Authorize 按钮
@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


# ===== password（密码）流 =====
# password “流”是 OAuth2 中定义用于处理安全性和身份验证的方式（“流”）之一。
# OAuth2 的设计初衷是让后端或 API 能够独立于验证用户的服务器。
# 但在本例中，同一个 FastAPI 应用程序将同时处理 API 和身份验证。

# 整体流程如下：
# 用户在前端输入 username 和 password，然后按下 Enter。
# 前端（在用户的浏览器中运行）将 username 和 password 发送到我们 API 中的一个特定 URL（由 tokenUrl="token" 声明）。
# API 检查该 username 和 password，并返回一个“令牌”（我们目前尚未实现这些）。
#   “令牌”（token）只是一串包含某些内容的字符串，我们稍后可以用它来验证该用户。
#   通常，令牌被设置为在一段时间后过期。
#       因此，用户在一段时间后将需要重新登录。
#       如果令牌被盗，风险也较小。它不像永久密钥那样（在大多数情况下）永远有效。
# 前端将该令牌临时存储在某个地方。
# 用户点击前端进入前端 Web 应用的另一个部分。
# 前端需要从 API 获取更多数据。
#   但它需要针对该特定端点进行身份验证。
#   因此，为了通过我们的 API 进行身份验证，它发送一个 Authorization 标头，其值为 Bearer 加上该令牌。
#   如果令牌包含 foobar，则 Authorization 标头的内容将是：Bearer foobar。

# ===== FastAPI 的 OAuth2PasswordBearer =====

# FastAPI 提供了多种不同抽象级别的工具来实现这些安全特性。
# 在本例中，我们将使用带有 Bearer 令牌的 Password 流的 OAuth2。我们使用 OAuth2PasswordBearer 类来实现。


# “Bearer”令牌并不是唯一的选择。
# 但它是我们用例的最佳选择。
# 对于大多数用例来说，它可能也是最好的选择，除非你是 OAuth2 专家，并且确切知道为什么还有其他选择更适合你的需求。
# 如果是那样，FastAPI 也为你提供了构建它的工具。


# 当我们创建 OAuth2PasswordBearer 类的实例时，我们传入 tokenUrl 参数。
# 该参数包含客户端（在用户浏览器中运行的前端）将用于发送 username 和 password 以获取令牌的 URL。

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 这里的 tokenUrl="token" 指的是一个我们尚未创建的相对 URL token。由于它是相对 URL，因此它等同于 ./token。
# 因为我们使用的是相对 URL，如果你的 API 位于 https://example.com/，那么它将指向 https://example.com/token。
# 但如果你的 API 位于 https://example.com/api/v1/，那么它将指向 https://example.com/api/v1/token。
# 使用相对 URL 很重要，以确保你的应用程序即使在代理之后等高级使用场景下也能正常工作。

# 此参数不会创建该端点/路径操作，但声明 URL /token 是客户端应该用来获取令牌的 URL。该信息用于 OpenAPI，并进而用于交互式 API 文档系统。

# oauth2_scheme 变量是 OAuth2PasswordBearer 的一个实例，但它也是一个“可调用对象”。

# 它可以像这样被调用
# oauth2_scheme(some, parameters)
# 所以，它可以与 Depends 一起使用。

# 此依赖项将提供一个 str，它被赋值给路径操作函数的参数 token。
# FastAPI 将知道它可以使用此依赖项在 OpenAPI 模式（以及自动 API 文档）中定义一个“安全方案”。

# ===== 技术细节 =====
# FastAPI 将知道它可以使用 OAuth2PasswordBearer 类（在依赖项中声明）在 OpenAPI 中定义安全方案，因为它继承
# 自 fastapi.security.oauth2.OAuth2，而后者又继承自 fastapi.security.base.SecurityBase。

# 所有与 OpenAPI（及自动 API 文档）集成的安全实用程序都继承自 SecurityBase，
# 这就是 FastAPI 如何知道如何将它们集成到 OpenAPI 中的方式。

# ===== 它的作用 =====
# 它会去请求中查找 Authorization 标头，检查其值是否为 Bearer 加上某个令牌，并将该令牌作为 str 返回。

# 如果它没有看到 Authorization 标头，或者该值没有 Bearer 令牌，它将直接返回 401 状态码错误（UNAUTHORIZED）。

# 你甚至不必检查令牌是否存在以返回错误。你可以确定，如果你的函数被执行，那么令牌中一定会有一个 str。

