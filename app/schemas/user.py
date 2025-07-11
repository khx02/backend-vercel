from pydantic import BaseModel, EmailStr


# Request body when client requests to create user.
class UserCreateReq(BaseModel):
    email: EmailStr
    password: str

class UserHashed(BaseModel):
    email: EmailStr
    hashed_password: str

# User model in the DB.
class UserModel(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str

# Response model when sending user details to client.
class UserRes(BaseModel):
    email: EmailStr
