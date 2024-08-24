from pydantic import BaseModel, EmailStr
from typing import List, Optional, Tuple

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True



class InterviewCreate(BaseModel):
    title: str
    description: str
    email: EmailStr  # Validates email format
    questions: List[str]  # List of questions to be included in the interview

class InterviewUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[str]] = None 

class GPTFollowupRequest(BaseModel):
    previous_question: str
    previous_answer: str

class ConversationCreate(BaseModel):
    interview_id: int
    conversation: List[Tuple[str, str, int]]  # Now includes a timestamp as an integer
    recording: Optional[bytes] = None