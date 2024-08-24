from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection URL specifying the database type, username, password, host, and database name
SQLALCHEMY_DATABASE_URL = "postgresql://anigokul:KkgtLmszKNz5mNN@fastapi-demo.postgres.database.azure.com/postgres"

# Create an engine that will manage the connection to the database
# This engine will be used by SQLAlchemy to issue SQL commands to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "SessionLocal" class which will serve as a factory for new Session objects
# autocommit=False: Prevents automatic committing of transactions, requiring manual control
# autoflush=False: Disables the automatic flush of pending changes to the database before each query
# bind=engine: Binds the session to the engine created above
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models in SQLAlchemy
# This class is used to create the models' table structure in the database
Base = declarative_base()

# Dependency function to get the database session
# It ensures that the session is opened before a request and properly closed after the request is handled
def get_db():
    db = SessionLocal()  # Create a new session object from SessionLocal
    try:
        yield db  # Yield the session for use in the request
    finally:
        db.close()  # Ensure the session is closed after the request, preventing resource leaks
