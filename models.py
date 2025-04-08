from sqlalchemy import Column, Integer, String, Float
from database import Base


class Employee(Base):
    __tablename__ = "employees"

    emp_id = Column(Integer, primary_key=True, index=True)
    fname = Column(String, index=True)
    lname = Column(String, index=True)
    role = Column(String)
    gender = Column(String)
    experience = Column(Float)
    address = Column(String)
    phone_number = Column(String, index=True)
    designation = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer")