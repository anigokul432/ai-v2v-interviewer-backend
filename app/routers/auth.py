import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from .. import models, schemas
from ..database import get_db

import os
import jwt
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
LLM_API_KEY = os.getenv('LLM_API_KEY')
ALGORITHM = "HS256"

class Token(BaseModel):
    token: str

@router.post("/google")
def google_login(token: Token, db: Session = Depends(get_db)):
    try:
        id_info = id_token.verify_oauth2_token(token.token, requests.Request(), CLIENT_ID)
        google_id = id_info['sub']
        email = id_info['email']
        name = id_info['name']

        user = db.query(models.User).filter(models.User.email == email).first()

        if user is None:
            new_user = models.User(username=name, email=email, hashed_password=google_id)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user

        # Create JWT token
        jwt_token = jwt.encode({"sub": user.email}, CLIENT_SECRET, algorithm=ALGORITHM)

        return {"access_token": jwt_token, "token_type": "bearer"}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, CLIENT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
