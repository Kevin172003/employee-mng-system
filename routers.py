# from fastapi import FastAPI, HTTPException, Depends, Request, APIRouter 
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from auth import require_admin, require_user
# from database import SessionLocal
# from dependencies import get_db
# from models import Employee
# from sqlalchemy.orm import Session
# import models
# from schemas import EmployeeBase, EmployeeCreate, EmployeeUpdate
# from fastapi.encoders import jsonable_encoder  # <-- Import jsonable_encoder
# import logging

# templates = Jinja2Templates(directory="templates")



# router = APIRouter(
#     prefix="/employees",
#     tags=["employees"]
# )

# @router.get("/get_employees")
# async def read_all(
#     request: Request, 
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_user)  # Add user authentication
# ):
#     employees = db.query(Employee).all()
#     return templates.TemplateResponse("index.html", {
#         "request": request, 
#         "employees": employees,
#         "user_role": current_user.role  # Pass user role to template
#     })

# @router.post("/create-employees/", response_model=EmployeeBase, dependencies=[Depends(require_user)])
# def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
#     new_emp = Employee(**emp.model_dump())
#     db.add(new_emp)
#     db.commit()
#     db.refresh(new_emp)
#     return new_emp

# @router.get("/create", response_class=HTMLResponse)
# async def create_employee_form(
#     request: Request,
#     current_user: models.User = Depends(require_admin)  # Only admins can access the form
# ):
#     return templates.TemplateResponse("add_employee.html", {"request": request})

# @router.get("/update-form/{emp_id}", response_class=HTMLResponse, name="update_employee_form")
# async def update_employee_form(
#     emp_id: int, 
#     request: Request, 
#     db: Session = Depends(get_db),
#     current_user: models.User = Depends(require_admin)  # Only admins can access update form
# ):
#     employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return templates.TemplateResponse("update_employee.html", {"request": request, "emp": employee})

# @router.put("/update/{emp_id}", dependencies=[Depends(require_admin)])
# async def update_employee(emp_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db)):
#     employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     # employee["experience"] = float(employee["experience"])
#     # Log the incoming update data for debugging
#     update_data = employee_update.model_dump(exclude_unset=True)
#     logging.info(f"Received update for employee {emp_id}: {update_data}")
    
#     if not update_data:
#         logging.warning(f"No update data provided for employee {emp_id}")
#         return {"msg": "No changes provided", "employee": jsonable_encoder(employee)}
    
#     for key, value in update_data.items():
#         setattr(employee, key, value)
#         logging.info(f"Updated {key} to {value} for employee {emp_id}")
    
#     db.commit()
#     db.refresh(employee)
    
#     logging.info(f"Employee {emp_id} updated successfully: {jsonable_encoder(employee)}")
#     return {"msg": "Employee updated successfully", "employee": jsonable_encoder(employee)}


# @router.delete("/delete/{emp_id}", dependencies=[Depends(require_admin)])
# def delete_employee(emp_id: int, db: Session = Depends(get_db)):
#     employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     db.delete(employee)
#     db.commit()
#     return {"message": "Employee deleted successfully"}
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import require_admin, get_current_user_optional
from dependencies import get_db
from models import Employee
from sqlalchemy.orm import Session
import models
from schemas import EmployeeBase, EmployeeCreate, EmployeeUpdate
from fastapi.encoders import jsonable_encoder
import logging

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/employees",
    tags=["employees"]
)

# Public endpoint: both viewers and unauthenticated users can access.
@router.get("/get_employees")
async def read_all(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional)
):
    role = current_user.role if current_user else "public"
    employees = db.query(Employee).all()
    return templates.TemplateResponse(
        request,
        "index.html",  # new partial template file
        {
            "user_role": role,
            "employees": employees,
        }
    )



# The following endpoints require admin rights.
@router.post("/create-employees/", response_model=EmployeeBase, dependencies=[Depends(require_admin)])
def create_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    new_emp = Employee(**emp.model_dump())
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

@router.get("/create", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def create_employee_form(
    request: Request,
):
    return templates.TemplateResponse("add_employee.html", {"request": request})


@router.get("/update-form/{emp_id}", response_class=HTMLResponse, name="update_employee_form")
async def update_employee_form(
    emp_id: int, 
    request: Request, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
):
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return templates.TemplateResponse("update_employee.html", {"request": request, "emp": employee})

@router.put("/update/{emp_id}", dependencies=[Depends(require_admin)])
async def update_employee(emp_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db),current_user: models.User = Depends(require_admin)):
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    update_data = employee_update.model_dump(exclude_unset=True)
    logging.info(f"Received update for employee {emp_id}: {update_data}")
    
    if not update_data:
        logging.warning(f"No update data provided for employee {emp_id}")
        return {"msg": "No changes provided", "employee": jsonable_encoder(employee)}
    
    for key, value in update_data.items():
        setattr(employee, key, value)
        logging.info(f"Updated {key} to {value} for employee {emp_id}")
    
    db.commit()
    db.refresh(employee)
    logging.info(f"Employee {emp_id} updated successfully: {jsonable_encoder(employee)}")
    return {"msg": "Employee updated successfully", "employee": jsonable_encoder(employee)}

@router.delete("/delete/{emp_id}", dependencies=[Depends(require_admin)])
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted successfully"}
