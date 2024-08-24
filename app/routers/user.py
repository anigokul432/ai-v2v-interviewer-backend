from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal

# Initialize the router with a prefix and tags for grouping user-related endpoints
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Dependency function to get the database session
# This ensures that the database session is opened before a request and closed after the request is completed
def get_db():
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Yield the session to be used in the request
    finally:
        db.close()  # Ensure the session is closed after the request is completed

# Endpoint to create a new user
# The response will be the user data based on the User schema
@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Create a new User instance with the provided data
    db_user = models.User(username=user.username, email=user.email, hashed_password=user.password)
    
    # Add the new user to the session and commit it to the database
    db.add(db_user)
    db.commit()
    
    # Refresh the session to reflect the newly created user data
    db.refresh(db_user)
    
    # Return the newly created user
    return db_user

# Endpoint to retrieve a user by their ID
# The response will be the user data based on the User schema
@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    # Query the database for a user with the given ID
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    # If the user is not found, raise a 404 error
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the found user
    return user
