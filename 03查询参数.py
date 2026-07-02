from fastapi import FastAPI

app = FastAPI()

# ============ 查询参数 ============
# 即：通过路径之后添加 '?' 并在它后面跟上由 '&' 分隔的键值对
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]

# ============ 路径参数 与 查询参数 同时使用 ============
# FastAPI 足够智能，可以识别出路径参数 item_id 是路径参数，而 q 不是，因此 q 是查询参数
@app.get("/items/{item_id}")
async def read_items(item_id: str, q: str | None = None):
    if q:
        return {"item_id" : item_id, "q" : q}
    return {"item_id": item_id}

# 也可以声明为 bool
@app.get("/itemsb/{item_id}/")
async def read_itemb(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    item.update({"short": short})
    return item

# ============ 多个 路径参数 与 查询参数 ============
# FastAPI 会自动区分它们。
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id : int, item_id : str, q : str | None = None, short : bool = False):
    return {
        "user_id" : user_id,
        "item_id" : item_id,
        "q" : q,
        "short" : short
    }

# ============ 必需的查询参数 ============
# 当你为非路径参数（目前我们只见过查询参数）声明了默认值时，该参数就不是必需的。
# 如果你不想设置特定值但想使其成为可选参数，请将默认值设为 None。
# 但如果你想使某个查询参数成为必需项，只需不声明任何默认值即可。
@app.get("/itemsr/{item_id}")
async def read_user_item(item_id: str, needy: str | None = None):
    item = {"item_id": item_id, "needy": needy}
    return item