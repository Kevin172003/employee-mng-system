from fastapi import FastAPI, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from models import Base, User
from database import engine
from auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from schemas import UserCreate, Token
from routers import get_db, router

from fastapi.middleware.cors import CORSMiddleware

# Allow all origins (adjust as needed)
origins = ["*"]
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="kevinrupera2003")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(router)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# -------------------- Routes --------------------

# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     # Redirect to the employee list page (public view)
#     return templates.TemplateResponse("index.html", {"request": request})
@app.get("/register", response_class=HTMLResponse)
async def home(request: Request):
    # Redirect to the employee list page (public view)
    return templates.TemplateResponse(request,"register.html", {"request": request})

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully"}

@app.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/login")
def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})



@app.post("/login")
def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    request.session["username"] = username
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "msg": "Invalid login"})

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    redirect_response = RedirectResponse(url="/employees/get_employees", status_code=303)
    redirect_response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        samesite="Lax"
    )
    return redirect_response

@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.username}! This is a protected route."}
