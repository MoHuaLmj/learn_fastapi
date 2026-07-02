from fastapi import FastAPI

app = FastAPI()

# ============ 额外模型 ============
# 拥有多个相关模型是很常见的。

# 对于用户模型来说尤其如此，因为：

# 输入模型需要包含密码。
# 输出模型不应包含密码。
# 数据库模型可能需要包含哈希后的密码。


# 多个模型
# 这里有一个通用构思，展示了模型及其密码字段在不同场景下的使用方式：
from pydantic import BaseModel, EmailStr
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: str | None = None

def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password

def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


# ============ 减少重复 ============
# 减少代码重复是 FastAPI 的核心理念之一
# 可以声明一个 UserBase 模型，作为其他模型的基础。然后我们可以创建该模型的子类，继承其属性（类型声明、验证等）
# 通过这种方式，我们只需要声明模型之间的差异（带明文 password 的、带 hashed_password 的、以及不带密码的）。
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

class UserIn(UserBase):
    password: str

class UserOut(UserBase):
    pass

class UserInDB(UserBase):
    hashed_password: str
    
    
# ============ Union 或 anyOf ============
# 你可以将响应声明为两个或多个类型的 Union，这意味着响应可以是其中任何一种
# 它将在 OpenAPI 中定义为 anyOf
# 为此，请使用 Python 标准类型提示 typing.Union
class BaseItem(BaseModel):
    description: str
    type: str

class CarItem(BaseItem):
    type: str = "car"

class PlaneItem(BaseItem):
    type: str = "plane"
    size: int

items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}

@app.get("/itemsr/{item_id}", response_model=PlaneItem | CarItem)
async def read_itemr(item_id: str):
    return items[item_id]

# 模型列表
# 同样，你可以声明对象列表作为响应
# 使用 python 标准的 list 即可
class Item(BaseModel):
    name: str
    description: str


@app.get("/items/", response_model=list[Item])
async def read_items():
    return items

# 返回任意 dict
@app.get("/keyword-weights/", response_model=dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}