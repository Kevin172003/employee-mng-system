from datetime import datetime, timedelta, timezone
from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from dependencies import get_db
import models

SECRET_KEY = "kevinrupera2003"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# For endpoints that allow public access, no error is raised if token is missing.
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)
# For endpoints that require authentication.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: str = Cookie(default=None)  # assuming token is stored in cookie
):
    if token is None:
        print("Token not found in cookie.")
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            print("No username in token payload.")
            return None
        user = db.query(models.User).filter(models.User.username == username).first()
        if user:
            print(f"User found: {user.username}, Role: {user.role}")
        else:
            print("User not found in DB.")
        return user
    except JWTError as e:
        print(f"JWT decode error: {e}")
        return None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    username = request.session.get("username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def require_admin(user: models.User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_user(current_user: models.User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return current_user
