from fastapi import FastAPI, Path, Query, Body, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# ============ 获取当前用户 ============

# 上一章如下:
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

# 这还不够有用
# ===== 提供当前用户 =====

# 1.创建用户模型
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

# 2.创建 get_current_user 依赖项
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    return user

# 3. 获取用户
def fake_decode_token(token):
    return User(
        username=token + "fakedecoded", email="john@example.com", full_name="John Doe"
    )

# 4. 注入当前用户
@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

# ===== 其他模型 =====
# 现在，你可以直接在路径操作函数中获取当前用户，并在依赖注入层面处理安全机制，使用 Depends 即可。
# 而且你可以对安全需求使用任何模型或数据（在本例中是 Pydantic 模型 User）。
# 你并不受限于使用特定的数据模型、类或类型。
# 你想拥有 id 和 email 而模型中没有 username？没问题。你可以使用同样的工具。
# 你只想拥有一个 str？或者仅仅是一个 dict？或者直接使用数据库类的模型实例？它们的工作方式完全一样。
# 你的应用程序中没有登录用户，而是只有访问令牌的机器人、爬虫或其他系统？同样，它们的工作方式也完全一样。
# 只需使用应用程序所需的任何类型的模型、类或数据库。FastAPI 的依赖注入系统都能满足你的需求。


# ===== 代码量问题 =====
# 这个例子看起来可能有点冗长。请记住，我们在同一个文件中混合了安全、数据模型、工具函数和路径操作。
# 但关键点在于：
# 安全和依赖注入的代码只需要写一次。
# 你可以根据需要将其做得尽可能复杂。但即便如此，它也只需编写一次，且位于同一个地方。并且它具备极高的灵活性。
# 你可以拥有成千上万个使用相同安全系统的端点（路径操作）。
# 它们中的每一个（或你选择的任何一部分）都可以利用这些可重用的依赖项或你创建的任何其他依赖项。
# 而这成千上万个路径操作每一个都可以精简到只需 3 行代码。
