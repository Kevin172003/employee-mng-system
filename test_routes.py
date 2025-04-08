from fastapi.testclient import TestClient
from auth import require_admin
from routers import router 
from main import app 
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from dependencies import get_db
from models import Employee


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_employees.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(router=router)
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_admin] = lambda: None

client = TestClient(app)


def setup_module(module):
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add_all([
        Employee(fname="Alice", lname="Smith", role="admin", experience=2, phone_number="1234567890"),
        Employee(fname="Bob", lname="Jones", role="viewer", experience=5, phone_number="9876543210"),
    ])
    db.commit()
    db.close()

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)

def test_get_employee_without_login():
    response = client.get("/employees/get_employees")
    assert response.status_code == 200
    assert "Alice" in response.text
    assert "Bob" in response.text

# @router.post("/create-employees/", response_model=EmployeeBase, dependencies=[Depends(require_admin)])
# def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
#     new_emp = Employee(**emp.model_dump())
#     db.add(new_emp)
#     db.commit()
#     db.refresh(new_emp)
#     return new_emp
def test_create_employee():
    payload = {
    "fname": "admin",
    "lname": "string",
    "role": "admin",
    "gender": "string",
    "experience": 0,
    "address": "string",
    "phone_number": "string",
    "designation": "string"
    }

    response = client.post("/employees/create-employees/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["fname"] == "admin"
    assert data["role"] == "admin"

def test_update_employee():
    db = TestingSessionLocal()
    employee = Employee(
        fname="John",
        lname="Doe",
        role="viewer",
        gender="male",
        experience=1,
        address="string",
        phone_number="5550001234",
        designation="Intern"
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    emp_id = employee.emp_id
    db.close()
    payload = {
    "fname": "admin",
    "lname": "string",
    "role": "admin",
    "gender": "male",
    "experience": 2,
    "address": "string",
    "phone_number": "string",
    "designation": "Developer"
    }

    response = client.put(f"/employees/update/{emp_id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["employee"]["experience"] == 2
    assert data["employee"]["designation"] == "Developer"




def test_delete_employee():
    db = TestingSessionLocal()
    employee = Employee(
        fname="John",
        lname="Doe",
        role="viewer",
        gender="male",
        experience=1,
        address="string",
        phone_number="5550001234",
        designation="Intern"
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    emp_id = employee.emp_id
    db.close()

    # No payload here
    response = client.delete(f"/employees/delete/{emp_id}")
    assert response.status_code == 200
    assert {'message': 'Employee deleted successfully'}
    # Optional: Confirm deletion
    db = TestingSessionLocal()
    deleted_emp = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    assert deleted_emp is None
    db.close()



# def test_read_main():
#     response = client.get("/employees/get_employees")
#     assert response.status_code == 200
#     # assert "Welcome to the Employee Management System" in response.text
























# l1 = [1, 2, 3,3, 4]

# output = []
# num = len(l1)
# for i in range(num):
#     n = 1
#     print(i)
#     for j in range(num):
#         print(j, l1[j])
#         if i != j:
#             n *= l1[j]
#     output.append(n)

# print(output)

# def product_except_self(nums):
#     n = len(nums)
#     result = [1] * n

#     prefix = 1
#     for i in range(n):
#         result[i] = prefix
#         prefix *= nums[i]

#     suffix = 1
#     for i in range(n-1, -1, -1):
#         print(i)
#         result[i] *= suffix
#         suffix *= nums[i]

#     return result

# l1 = [0, 1, 2, 3, 4]
# print(product_except_self(l1))
