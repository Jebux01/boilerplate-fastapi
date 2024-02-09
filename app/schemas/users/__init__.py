from pydantic import BaseModel


class User(BaseModel):
    """Base model for user"""

    id: int
    username: str
    password: str

class UserLogin(BaseModel):
    """Base model for Login user"""

    username: str
    password: str


class UserTokenData(BaseModel):
    """Data untoken"""

    username: str
    password: str


class CreateUser(BaseModel):
    """Base model for create user"""

    username: str
    password: str


class UpdateUser(CreateUser):
    """Base model for update user"""


