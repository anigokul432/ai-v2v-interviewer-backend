from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, LargeBinary, BigInteger
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    interviews = relationship("Interview", back_populates="user")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'))

    interview = relationship("Interview", back_populates="questions")

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    taken = Column(Boolean, default=False)  # Track if the interview has been taken
    score = Column(Integer, nullable=True)  # Score of the interview
    recording = Column(LargeBinary, nullable=True)  # Add this line to store the recording

    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="interview", cascade="all, delete-orphan")



class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey('interviews.id'))
    question = Column(String)
    answer = Column(String)
    timestamp = Column(BigInteger)  # Add this line to store the timestamp

    interview = relationship("Interview", back_populates="conversations")