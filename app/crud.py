from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_enterprise(db: Session, enterprise_id: int):
    return db.query(models.Enterprise).filter(models.Enterprise.id == enterprise_id).first()

def get_enterprise_by_username(db: Session, username: str):
    return db.query(models.Enterprise).filter(models.Enterprise.username == username).first()

def create_enterprise(db: Session, enterprise: schemas.EnterpriseCreate):
    hashed_password = pwd_context.hash(enterprise.password)
    db_enterprise = models.Enterprise(username=enterprise.username, hashed_password=hashed_password)
    db.add(db_enterprise)
    db.commit()
    db.refresh(db_enterprise)
    return db_enterprise
