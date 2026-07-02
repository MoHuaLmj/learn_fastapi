from fastapi import FastAPI

app = FastAPI()

# ============ 请求文件 ============
# 你可以使用 File 定义客户端上传的文件
# 要接收上传的文件，请先安装 python-multipart
# 这是因为上传的文件是作为“表单数据”发送的

# 1.导入 File
# 2. 定义 File 参数

# 创建文件参数的方式与 Body 或 Form 相同
# File 是直接继承自 Form 的类
# 但请记住，当你从 fastapi 导入 Query、Path、File 等时，它们实际上是返回特殊类的函数
from typing import Annotated
from fastapi import FastAPI, File, UploadFile

@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

# 若要声明文件主体，必须使用 File，否则参数会被解释为查询参数或主体（JSON）参数
# 文件将作为“表单数据”上传
# 如果将 路径操作函数 参数的类型声明为 bytes，FastAPI 将为你读取文件，你将以 bytes 形式接收内容
# 请记住，这意味着所有内容都将存储在内存中。这对于小文件来说效果很好
# 但在某些情况下，使用 UploadFile 会更有利

# ============ UploadFile ============
# 使用 UploadFile 的文件参数
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
# 与 bytes 相比，使用 UploadFile 有几个优点

# 你不需要在参数的默认值中使用 File()。

# 它使用“脱机缓存”文件（spooled file）
# 文件存储在内存中直至达到最大大小限制，超过该限制后，它将存储在磁盘上。
# 这意味着它非常适合处理大型文件（如图像、视频、大二进制文件等），而不会耗尽所有内存。

# 你可以从上传的文件中获取元数据。

# 它具有一个 类文件 的 async 接口。
# 它公开了一个实际的 Python SpooledTemporaryFile 对象，你可以将其直接传递给其他期望类文件对象的库。


# UploadFile 具有以下属性
# filename: 一个 str，表示上传的原始文件名（例如 myimage.jpg）。
# content_type: 一个 str，表示内容类型（MIME 类型 / 媒体类型）（例如 image/jpeg）。
# file: 一个 SpooledTemporaryFile（一个 类文件 对象）。这是实际的 Python 文件对象，你可以将其直接传递给其他期望“类文件”对象的函数或库。


# UploadFile 具有以下 async 方法。它们在底层（使用内部的 SpooledTemporaryFile）调用相应的文件方法。
# write(data): 将 data（str 或 bytes）写入文件。
# read(size): 读取文件的 size（int）个字节/字符。
# seek(offset): 跳转到文件中的字节位置 offset（int）。
# 例如，await myfile.seek(0) 会跳转到文件开头。
# 如果你运行了一次 await myfile.read() 之后需要再次读取内容，这非常有用。
# close(): 关闭文件。

# 由于所有这些方法都是 async 方法，因此你需要对其使用 "await"。
# 例如，在 async 路径操作函数 内部，你可以通过以下方式获取内容
# contents = await myfile.read()

# 如果你在普通的 def 路径操作函数 内部，你可以直接访问 UploadFile.file，例如
# contents = myfile.file.read()


# 当不包含文件时，来自表单的数据通常使用“媒体类型” application/x-www-form-urlencoded 进行编码。

# 但当表单包含文件时，它会被编码为 multipart/form-data
# 如果你使用 File，FastAPI 将知道它必须从请求主体的正确部分获取文件

# 如果你想详细了解这些编码和表单字段，请前往 MDN 关于 POST 的 Web 文档。



# ============ 可选文件上传 ============
# 你可以通过使用标准的类型注解并设置默认值为 None，使文件变为可选
@app.post("/files/")
async def create_file(file: Annotated[bytes | None, File()] = None):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}
    
    
# ============ 带有额外元数据的 UploadFile ============
# 你也可以将 File() 与 UploadFile 一起使用，例如，设置额外的元数据
@app.post("/files/")
async def create_file(file: Annotated[bytes, File(description="A file read as bytes")]):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(
    file: Annotated[UploadFile, File(description="A file read as UploadFile")],
):
    return {"filename": file.filename}


# ============ 多文件上传 ============
# 可以同时上传多个文件。
# 它们将关联到使用“表单数据”发送的同一个“表单字段”。
# 要使用此功能，请声明一个 bytes 或 UploadFile 的列表
from fastapi.responses import HTMLResponse
@app.post("/files/")
async def create_files(files: Annotated[list[bytes], File()]):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}

@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

# 带有额外元数据的多文件上传
# 和之前一样，你可以使用 File() 设置额外参数，即使对于 UploadFile 也可以
@app.post("/files/")
async def create_files(
    files: Annotated[list[bytes], File(description="Multiple files as bytes")],
):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    return {"filenames": [file.filename for file in files]}