from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, LargeBinary, BigInteger
from sqlalchemy.orm import relationship
from .database import Base

# Define the User model, which represents users in the application
class User(Base):
    __tablename__ = "users"  # The name of the table in the database

    # Define the columns in the users table
    id = Column(Integer, primary_key=True, index=True)  # Unique identifier for each user
    username = Column(String, unique=True, index=True)  # Username, must be unique
    email = Column(String, unique=True, index=True)  # Email, must be unique
    hashed_password = Column(String)  # Password, stored as a hashed string
    is_active = Column(Boolean, default=True)  # Flag to indicate if the user is active

    # Relationship to the Interview model
    # This creates a one-to-many relationship where a user can have multiple interviews
    interviews = relationship("Interview", back_populates="user")

# Define the Question model, which represents interview questions
class Question(Base):
    __tablename__ = "questions"  # The name of the table in the database

    # Define the columns in the questions table
    id = Column(Integer, primary_key=True, index=True)  # Unique identifier for each question
    text = Column(String, index=True)  # The text of the question
    interview_id = Column(Integer, ForeignKey('interviews.id'))  # Foreign key linking to the Interview model

    # Relationship to the Interview model
    # This creates a many-to-one relationship where each question belongs to one interview
    interview = relationship("Interview", back_populates="questions")

# Define the Interview model, which represents interviews taken by users
class Interview(Base):
    __tablename__ = "interviews"  # The name of the table in the database

    # Define the columns in the interviews table
    id = Column(Integer, primary_key=True, index=True)  # Unique identifier for each interview
    title = Column(String, index=True)  # Title of the interview
    description = Column(String, index=True)  # Description of the interview
    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key linking to the User model
    taken = Column(Boolean, default=False)  # Indicates if the interview has been completed
    score = Column(Integer, nullable=True)  # The score of the interview, nullable because it may not be available immediately
    recording = Column(LargeBinary, nullable=True)  # Stores the binary data of the interview recording # TODO does not store base64 properly

    # Relationship to the User model
    # This creates a many-to-one relationship where each interview belongs to one user
    user = relationship("User", back_populates="interviews")
    
    # Relationship to the Question model
    # This creates a one-to-many relationship where an interview can have multiple questions
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    
    # Relationship to the Conversation model
    # This creates a one-to-many relationship where an interview can have multiple conversation entries
    conversations = relationship("Conversation", back_populates="interview", cascade="all, delete-orphan")

# Define the Conversation model, which represents individual interactions within an interview
class Conversation(Base):
    __tablename__ = "conversations"  # The name of the table in the database

    # Define the columns in the conversations table
    id = Column(Integer, primary_key=True, index=True)  # Unique identifier for each conversation entry
    interview_id = Column(Integer, ForeignKey('interviews.id'))  # Foreign key linking to the Interview model
    question = Column(String)  # The question asked during the interview
    answer = Column(String)  # The answer provided by the interviewee
    timestamp = Column(BigInteger)  # Timestamp to track when the interaction occurred

    # Relationship to the Interview model
    # This creates a many-to-one relationship where each conversation entry belongs to one interview
    interview = relationship("Interview", back_populates="conversations")
