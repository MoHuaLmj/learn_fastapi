from fastapi import FastAPI, Path, Query, Body, Depends
from typing import Annotated

app = FastAPI()

# ============ 带 yield 的依赖项 ============
# FastAPI 支持在完成操作后执行一些额外步骤的依赖项。
# 要做到这一点，请使用 yield 而不是 return，并将额外的步骤（代码）写在 yield 之后
# 确保每个依赖项中只使用一次 yield。


# 任何可以与
# @contextlib.contextmanager 或
# @contextlib.asynccontextmanager
# 一起使用的函数都可以作为 FastAPI 依赖项。
# 事实上，FastAPI 在内部正是使用了这两个装饰器。


# ===== 带有 yield 的数据库依赖项 =====
# 例如，你可以用它来创建数据库会话，并在完成后将其关闭。
# 只有在 yield 语句之前（包含该语句）的代码会在创建响应之前执行
async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
        
# yield 的值即为注入到路径操作和其他依赖项中的值
# yield 语句之后的代码会在响应发送后执行

# ===== 带有 yield 和 try 的依赖项 =====
# 如果你在带有 yield 的依赖项中使用 try 代码块，你将捕获到在使用该依赖项时抛出的任何异常
# 例如，如果中间的某些代码、另一个依赖项或路径操作导致数据库事务“回滚”或产生了任何其他异常，你都可以在依赖项中捕获到该异常。
# 因此，你可以在带有 yield 的依赖项中使用 except SomeException 来针对特定异常进行处理。
# 同样，你可以使用 finally 来确保无论是否发生异常，退出步骤都会被执行。
async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()
        
# ===== 带有 yield 的子依赖项 =====
# 你可以拥有任意规模和结构的子依赖项以及“依赖树”，并且其中任何一个或全部都可以使用 yield。
# 例如，dependency_c 可以依赖 dependency_b，而 dependency_b 依赖 dependency_a。
async def dependency_a():
    dep_a = generate_dep_a()
    try:
        yield dep_a
    finally:
        dep_a.close()

async def dependency_b(dep_a: Annotated[DepA, Depends(dependency_a)]):
    dep_b = generate_dep_b()
    try:
        yield dep_b
    finally:
        dep_b.close(dep_a)

async def dependency_c(dep_b: Annotated[DepB, Depends(dependency_b)]):
    dep_c = generate_dep_c()
    try:
        yield dep_c
    finally:
        dep_c.close(dep_b)
        
# 在这种情况下，dependency_c 要执行其退出代码，需要 dependency_b 的值（此处命名为 dep_b）仍然可用。
# 同理，dependency_b 的退出代码也需要 dependency_a 的值（此处命名为 dep_a）可用。

# 同样，你可以混合使用带有 yield 和 return 的依赖项，并让它们相互依赖。
# 你也可以拥有一个同时需要多个带 yield 依赖项的单一依赖项，等等。
# 你可以拥有任何你想要的依赖项组合。
# FastAPI 会确保所有内容都按正确的顺序运行。
# 这得益于 Python 的上下文管理器 (Context Managers)。


# ===== 带有 yield 和 HTTPException 的依赖项 =====
# 你已经了解到，可以使用带有 yield 的依赖项，通过 try 代码块来执行代码，并在 finally 之后运行退出代码。
# 你还可以使用 except 来捕获抛出的异常并进行处理。
# 例如，你可以抛出一个不同的异常，比如 HTTPException。

# 这是一种较为高级的技术，大多数情况下你并不需要它，
# 因为你可以在应用程序代码的其他地方（例如在路径操作函数中）抛出异常（包括 HTTPException）。
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException

data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}
class OwnerError(Exception):
    pass

def get_username():
    try:
        yield "Rick"
    except OwnerError as e:
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")

@app.get("/items/{item_id}")
def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]
    if item["owner"] != username:
        raise OwnerError(username)
    return item


# ===== 带有 yield 和 except 的依赖项 =====
# 如果你在带 yield 的依赖项中使用 except 捕获了异常且没有再次抛出（或抛出新异常），
# FastAPI 将无法察觉到异常的发生，这与普通 Python 中的情况一致。
class InternalError(Exception):
    pass

def get_username():
    try:
        yield "Rick"
    except InternalError:
        print("Oops, we didn't raise again, Britney 😱")

@app.get("/itemsr/{item_id}")
def get_itemr(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id == "portal-gun":
        raise InternalError(
            f"The portal gun is too dangerous to be owned by {username}"
        )
    if item_id != "plumbus":
        raise HTTPException(
            status_code=404, detail="Item not found, there's only a plumbus here"
        )
    return item_id

# 在这种情况下，客户端会如预料中那样收到 HTTP 500 内部服务器错误 响应，
# 因为我们没有抛出 HTTPException 或类似异常，但服务器不会有任何日志或其他关于错误原因的提示。


# 在带有 yield 和 except 的依赖项中始终使用 raise
# 如果你在带有 yield 的依赖项中捕获了异常，除非你抛出了另一个 HTTPException 或类似异常，
# 否则你应该重新抛出原始异常。

# 你可以使用 raise 重新抛出同一个异常
class InternalError(Exception):
    pass

def get_username():
    try:
        yield "Rick"
    except InternalError:
        print("We don't swallow the internal error here, we raise again 😎")
        raise

@app.get("/items/{item_id}")
def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id == "portal-gun":
        raise InternalError(
            f"The portal gun is too dangerous to be owned by {username}"
        )
    if item_id != "plumbus":
        raise HTTPException(
            status_code=404, detail="Item not found, there's only a plumbus here"
        )
    return item_id

# 现在客户端仍会收到 HTTP 500 内部服务器错误 响应，但服务器日志中将会有我们的自定义 InternalError

# 只会向客户端发送一个响应。它可能是错误响应之一，或者是路径操作的响应。
# 在发送了上述任一响应后，将无法再发送其他响应。

# 如果你在路径操作函数的代码中抛出任何异常，它将被传递给带 yield 的依赖项，包括 HTTPException。
# 在大多数情况下，你应该在带 yield 的依赖项中重新抛出该异常或抛出一个新异常，以确保它得到妥善处理。


# ===== 提前退出和 scope =====
# 通常，带 yield 依赖项的退出代码是在响应发送给客户端之后执行的

# 但如果你知道在路径操作函数返回后不需要再使用该依赖项，你
# 可以使用 Depends(scope="function") 来告知 FastAPI，
# 它应该在路径操作函数返回后，但在响应发送之前关闭该依赖项。
def get_username():
    try:
        yield "Rick"
    finally:
        print("Cleanup up before response is sent")


@app.get("/users/me")
def get_user_me(username: Annotated[str, Depends(get_username, scope="function")]):
    return username

# Depends() 接收一个 scope 参数，可选值包括：

# "function"：在处理请求的路径操作函数之前启动依赖项，在路径操作函数结束后、
# 但在响应发送回客户端之前结束该依赖项。因此，依赖函数将在路径操作函数的执行期间运行。

# "request"：在处理请求的路径操作函数之前启动依赖项（类似于使用 "function"），
# 但在响应发送回客户端之后结束。因此，依赖函数将在请求和响应周期的执行期间运行。

# 如果未指定且依赖项包含 yield，默认情况下其 scope 将为 "request"


# 子依赖项的 scope

# 当你声明一个 scope="request"（默认值）的依赖项时，任何子依赖项也必须具有 "request" 作用域。
# 但具有 scope="function" 的依赖项可以拥有 scope="function" 和 scope="request" 的子依赖项。

# 这是因为任何依赖项都必须能够在子依赖项之前运行其退出代码，因为它在执行退出代码时可能还需要用到子依赖项。


# ===== 带有 yield、HTTPException、except 和后台任务的依赖项 =====
# 带 yield 的依赖项经过不断演进，涵盖了不同的用例并修复了一些问题。


# ===== 上下文管理器 =====
# “上下文管理器”是指任何可以在 with 语句中使用的 Python 对象。

# 例如，你可以使用 with 来读取文件。
with open("./somefile.txt") as f:
    contents = f.read()
    print(contents)
    
# 当你创建一个带 yield 的依赖项时，FastAPI 会在内部为其创建一个上下文管理器，并将其与其他相关工具结合使用。


# 在带 yield 的依赖项中使用上下文管理器
# 在 Python 中，你可以通过创建具有 __enter__() 和 __exit__() 两个方法的类来创建上下文管理器。
# 你也可以在 FastAPI 的带 yield 依赖项内部使用 with 或 async with 语句来使用它们。
class MySuperContextManager:
    def __init__(self):
        self.db = DBSession()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


async def get_db():
    with MySuperContextManager() as db:
        yield db
        
# 另一种创建上下文管理器的方法是使用

# @contextlib.contextmanager 或
# @contextlib.asynccontextmanager
# 使用它们来装饰一个包含单个 yield 的函数。

# 这正是 FastAPI 内部对带 yield 依赖项所做的事情。
# 但你不需要手动为 FastAPI 依赖项使用这些装饰器（也不应该这么做）。

# FastAPI 会在内部为你完成。