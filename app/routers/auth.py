import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from .. import models, schemas
from ..database import get_db

import jwt
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize a FastAPI router with a specific prefix and tag for grouping related routes
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Environment variables for Google OAuth and JWT token generation
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
LLM_API_KEY = os.getenv('LLM_API_KEY')
ALGORITHM = "HS256"  # Algorithm used for encoding JWT tokens

# Define the structure of the token request body using Pydantic's BaseModel
class Token(BaseModel):
    token: str

# Route to handle Google login using the OAuth2 token provided by the frontend
@router.post("/google")
def google_login(token: Token, db: Session = Depends(get_db)):
    try:
        # Verify the OAuth2 token with Google's API
        id_info = id_token.verify_oauth2_token(token.token, requests.Request(), CLIENT_ID)
        
        # Extract necessary information from the verified token
        google_id = id_info['sub']  # Google user ID
        email = id_info['email']    # User's email address
        name = id_info['name']      # User's full name

        # Check if the user already exists in the database
        user = db.query(models.User).filter(models.User.email == email).first()

        # If user doesn't exist, create a new user in the database
        if user is None:
            new_user = models.User(username=name, email=email, hashed_password=google_id)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)  # Refresh the session to get the new user's ID
            user = new_user

        # Create a JWT token using the user's email as the subject
        jwt_token = jwt.encode({"sub": user.email}, CLIENT_SECRET, algorithm=ALGORITHM)

        # Return the JWT token to the client
        return {"access_token": jwt_token, "token_type": "bearer"}

    except ValueError:
        # If the token is invalid, raise an HTTP exception with a 400 status code
        raise HTTPException(status_code=400, detail="Invalid token")

# OAuth2PasswordBearer is used to handle token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency function to get the current user based on the JWT token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token to retrieve the user's email
        payload = jwt.decode(token, CLIENT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        # If there's an error decoding the token, raise an unauthorized exception
        raise credentials_exception
    
    # Query the database to find the user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception  # Raise an exception if the user is not found
    return user  # Return the authenticated user object
