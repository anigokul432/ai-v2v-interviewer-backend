from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from fastapi.middleware.cors import CORSMiddleware
import logging
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Logging is set up correctly!")



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

openai.api_key = os.getenv("OPENAI_API_KEY")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    logging.info(f"Authenticating user: {username}")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    role = "user"

    if not user:
        user = db.query(models.Enterprise).filter(models.Enterprise.username == username).first()
        role = "enterprise"
    
    if not user:
        logging.warning(f"User not found: {username}")
        return None, None
    
    if not verify_password(password, user.hashed_password):
        logging.warning(f"Password mismatch for user: {username}")
        return None, None
    
    logging.info(f"User authenticated: {username} as {role}")
    return user, role

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    logging.info(f"Username received: {form_data.username}")
    user, role = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logging.info(f"User role determined: {role}")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": role}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": role}



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@app.post("/users/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.post("/enterprises/register", response_model=schemas.Enterprise)
def register_enterprise(enterprise: schemas.EnterpriseCreate, db: Session = Depends(get_db)):
    db_enterprise = crud.get_enterprise_by_username(db, username=enterprise.username)
    if db_enterprise:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_enterprise(db=db, enterprise=enterprise)

@app.get("/fun-fact")
async def get_fun_fact():
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me a fun and interesting fact about math. Just say the fun fact and nothing else."}
            ],
            max_tokens=150,
            temperature=0.9
        )
        fact = response['choices'][0]['message']['content'].strip()
        return {"fun_fact": fact}
    except Exception as e:
        logging.error(f"Error generating fun fact: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate fun fact") from e

@app.get("/")
def read_root():
    return {"message": "Welcome to the basic template!"}