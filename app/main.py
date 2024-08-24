from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import interview, user, auth
from .database import engine
from . import models

# Initialize the FastAPI application
app = FastAPI()

# Add CORS (Cross-Origin Resource Sharing) middleware to the application
# This allows your API to be accessed by frontend applications hosted on different domains
app.add_middleware(
    CORSMiddleware,
    # allow_origins specifies the origins that are allowed to access the API
    # Uncomment the following line if you want to allow requests from your deployed frontend (GitHub Pages)
    allow_origins=[
        "https://anigokul432.github.io",
        "http://localhost:3000",
    ], 
    allow_credentials=True,  # Allow cookies to be sent with requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers in requests
)

# Create all tables in the database according to the models defined
# This ensures that the database schema is set up before the application starts
models.Base.metadata.create_all(bind=engine)

# Include the routers for different parts of the application
# This registers the routes defined in the interview, user, and auth modules with the FastAPI app
app.include_router(interview.router)
app.include_router(user.router)
app.include_router(auth.router)

# Define a simple root endpoint to verify that the API is working
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Interview Bot API"}
