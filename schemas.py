from typing import Optional
from pydantic import BaseModel


class EmployeeBase(BaseModel):
    fname: str
    lname: str
    role: str
    gender: str
    experience: float
    address: str
    phone_number: str
    designation: str

class EmployeeCreate(EmployeeBase):
    pass
class EmployeeUpdate(EmployeeBase):
    pass





# Schemas

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "viewer"
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserInDB(UserCreate):
    hashed_password: str
