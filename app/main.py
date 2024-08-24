from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import interview, user, auth
from .database import engine
from . import models

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://anigokul432.github.io"],  # Adjust this to your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(interview.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Interview Bot API"}
