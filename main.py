from getpass import getuser

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
def read_root():
    return {"hello": "world"}

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    print(f"username: {form_data.username}, password: {form_data.password}")
    return {"access_token" : f"hash-{form_data.username}", "token_type" : "bearer"}

class User(BaseModel):
    name: str | None

async def get_user(token: Annotated[str, Depends(oauth2_schema)]):
    return User(name=token)


@app.get("/items/")
def read_item(user: Annotated[User, Depends(get_user)]):
    return user
