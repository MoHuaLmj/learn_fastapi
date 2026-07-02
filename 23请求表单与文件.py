from fastapi import FastAPI

app = FastAPI()

# ============ 请求表单与文件 ============
# 你可以同时使用 File 和 Form 来定义文件和表单字段

# 1.导入 File 和 Form
from typing import Annotated
from fastapi import FastAPI, File, Form, UploadFile

# 2.定义 File 和 Form 参数
@app.post("/files/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
    
# 文件和表单字段将作为表单数据上传，你将接收到这些文件和表单字段。

# 你可以将部分文件声明为 bytes，部分声明为 UploadFile

# 你可以在一个 路径操作 中声明多个 File 和 Form 参数，
# 但不能同时声明预期接收 JSON 的 Body 字段，
# 因为请求的 Body 编码方式将是 multipart/form-data 而不是 application/json。