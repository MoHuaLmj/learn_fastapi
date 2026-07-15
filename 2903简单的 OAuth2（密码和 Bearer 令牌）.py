from fastapi import FastAPI, Path, Query, Body, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# ============ 简单的 OAuth2（密码和 Bearer 令牌） ============
# 现在，让我们在上一章的基础上构建，并添加缺失的部分，以实现一个完整的安全流程。

# ===== 获取 username 和 password =====
# OAuth2 规范指出，在使用“密码流”（我们正在使用）时，客户端/用户必须以表单数据的形式发送 username 和 password 字段。
# 规范要求这些字段必须以此命名。因此，使用 user-name 或 email 是行不通的。
# 但别担心，你可以在前端按照你喜欢的方式向最终用户展示这些字段。
# 你的数据库模型也可以使用任何你想要的名称。
# 但在登录的路径操作（path operation）中，我们需要使用这些特定的名称以符合规范（从而能够使用集成的 API 文档系统）。
# 该规范还指出，username 和 password 必须以表单数据的形式发送（即这里不能用 JSON）。

# scope
# 规范还提到，客户端可以发送另一个表单字段“scope”。
# 该表单字段名称为 scope（单数形式），但它实际上是一个由空格分隔的多个“作用域（scopes）”组成的长字符串。
# 每个“scope”只是一个字符串（不包含空格）。
# 它们通常用于声明特定的安全权限，例如：
#     users:read 或 users:write 是常见的示例。
#     instagram_basic 被 Facebook / Instagram 使用。
#     https://www.googleapis.com/auth/drive 被 Google 使用。

# 注意
# 在 OAuth2 中，“scope”只是一个声明所需特定权限的字符串。
# 它是否包含像 : 这样的字符，或者它是否是一个 URL，都不重要。
# 这些细节取决于具体实现。
# 对于 OAuth2 而言，它们仅仅是字符串。

# ===== 获取 username 和 password 的代码 =====
# 1.OAuth2PasswordRequestForm
# 首先，导入 OAuth2PasswordRequestForm，并在 /token 的路径操作中通过 Depends 将其作为依赖项使用。
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

def fake_hash_password(password: str):
    return "fakehashed" + password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user

# 更新依赖项
# 我们希望仅在用户处于活跃状态时获取 current_user。
# 因此，我们创建了一个额外的依赖项 get_current_active_user，它反过来使用 get_current_user 作为依赖项。
# 这两个依赖项在用户不存在或处于非活跃状态时都会返回 HTTP 错误。
# 因此，在我们的端点中，只有当用户存在、经过正确身份验证且处于活跃状态时，我们才能获取到用户。

# 注意:
# 我们在这里返回的带有 Bearer 值的额外 WWW-Authenticate 头部也是规范的一部分。
# 任何 401 “UNAUTHORIZED” HTTP（错误）状态码都应该返回一个 WWW-Authenticate 头部。
# 对于 Bearer 令牌（我们的情况），该头部的值应该是 Bearer。
# 实际上，你可以跳过这个额外的头部，它依然可以工作。
# 但这里提供它是为了符合规范。
# 此外，可能存在某些工具会预期并使用它（现在或将来），这对你或你的用户而言可能会有所助益。
# 这就是标准带来的益处……
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# OAuth2PasswordRequestForm 是一个类依赖项，它声明了一个包含以下内容的表单体：
    # username。
    # password。
    # 一个可选的 scope 字段，作为由空格分隔的字符串组成的长字符串。
    # 一个可选的 grant_type。
    # 一个可选的 client_id（在本例中我们不需要）。
    # 一个可选的 client_secret（在本例中我们不需要）。
# OAuth2 规范实际上要求 grant_type 字段的值必须固定为 password，但 OAuth2PasswordRequestForm 并不会强制校验它。
# 如果你需要强制校验，请使用 OAuth2PasswordRequestFormStrict 而不是 OAuth2PasswordRequestForm。



# 与 OAuth2PasswordBearer 不同，OAuth2PasswordRequestForm 对 FastAPI 而言并不是一个特殊类。
# OAuth2PasswordBearer 告知 FastAPI 这是一个安全方案，因此它会被添加到 OpenAPI 中。
# 但 OAuth2PasswordRequestForm 只是一个你可以自己编写的类依赖项，或者你也可以直接声明 Form 参数。
# 但由于这是一个常见用例，FastAPI 直接提供了它，以简化开发。


# 依赖类 OAuth2PasswordRequestForm 的实例不会有一个包含空格分隔长字符串的 scope 属性，取而代之的是，它拥有一个 scopes 属性，其中包含了每个发送的作用域组成的字符串列表。
# 虽然本例中我们未使用 scopes，但如果需要，该功能已准备就绪。
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

# 返回令牌 token
# token 端点的响应必须是一个 JSON 对象。
# 它应该包含一个 token_type。在本例中，由于我们使用的是“Bearer”令牌，令牌类型应为“bearer”。
# 它还应该包含一个 access_token，其值为包含我们访问令牌的字符串。
# 对于这个简单的示例，我们完全不考虑安全性，直接返回 username 作为令牌。

# 提示:
# 根据规范，你应该返回一个包含 access_token 和 token_type 的 JSON，与本示例相同。
# 这是你必须在代码中亲自实现的部分，请确保使用了这些 JSON 键。
# 为了符合规范，这是你几乎唯一需要记住手动正确处理的事情。
# 对于其余部分，FastAPI 都会为你处理。
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user