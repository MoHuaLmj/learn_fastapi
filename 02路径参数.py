from fastapi import FastAPI

app = FastAPI()

@app.get("/{item}")
async def aaa(item: int): # 会进行类型检查，若传入 str 会返回错误
    return {"item" : item}


# ============ 出现类似下方的冲突时，即有歧义的地方，将优先的内容放在上面 =============
# ============ 即：路径首先匹配 ============
@app.get("/users/me")
async def read_user_me():
    return {"user_id" : "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id" : user_id}

# ============ 预定义路径参数值 ============
# 即：传入的值只能时枚举类中定义好的值
from enum import Enum
class ModelName(str, Enum):
    alexnet = "ALEXNET"
    resnet = "RESNET"
    lenet = "LENET"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name" : model_name, "message" : "alexnet is the start net for dp"}
    if model_name == ModelName.resnet:
        return {"model_name" : model_name, "message" : "its a the greatest invocation for the world"}
    else:
        return {"model_name" : model_name, "message" : "it sounds great"}

# ============ 包含路径的路径参数 ============
# 即： /files/{file_path} 中的 file_path = "home/jhondoe/myfile.txt"
# OpenAPI 不支持这种形式，因为难以测试和定义，而且会造成歧义
# 但是 Starlette(fastapi基于它) 中的路径转换器可以实现 (:path 表明该参数应匹配任何 路径 )
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path" : file_path}

