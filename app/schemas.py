from pydantic import BaseModel, EmailStr
from typing import List, Optional, Tuple

# Base model for user-related data
class UserBase(BaseModel):
    username: str  
    email: str  

# Model for creating a new user, extends UserBase with an additional password field
class UserCreate(UserBase):
    password: str  

# Model for representing a user in the response, extends UserBase with additional fields
class User(UserBase):
    id: int  
    is_active: bool  

    # Enable compatibility with ORM objects by configuring Pydantic to use SQLAlchemy's models
    class Config:
        orm_mode = True

# Model for creating a new interview
class InterviewCreate(BaseModel):
    title: str  
    description: str 
    email: EmailStr 
    questions: List[str] 

# Model for updating an existing interview
class InterviewUpdate(BaseModel):
    title: Optional[str] = None  
    description: Optional[str] = None 
    questions: Optional[List[str]] = None 

# Model for the GPT follow-up request
class GPTFollowupRequest(BaseModel):
    previous_question: str 
    previous_answer: str 

# Model for creating a conversation, which includes a list of (question, answer, timestamp) tuples
class ConversationCreate(BaseModel):
    interview_id: int  
    conversation: List[Tuple[str, str, int]] 
    recording: Optional[bytes] = None 
