from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from .auth import get_current_user 
import openai
from .auth import LLM_API_KEY
from typing import List


openai.api_key = LLM_API_KEY

router = APIRouter(
    prefix="/interview",
    tags=["interview"]
)

@router.get("/")
def get_interview():
    return {"message": "This is where the interview data will be returned."}

@router.post("/submit")
def submit_interview(answers: dict):
    return {"message": "Interview submitted successfully!", "answers": answers}

@router.get("/user-interviews")
def get_user_interviews(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    interviews = db.query(models.Interview).filter(models.Interview.user_id == user.id).all()
    
    # Building the response data
    interviews_data = [
        {
            "id": interview.id,
            "title": interview.title,
            "description": interview.description,
            "questions": [q.text for q in interview.questions],  # Assuming you have a questions relationship
            "taken": interview.taken ,  # Ensure this line is included
            "score": interview.score

        }
        for interview in interviews
    ]
    
    return interviews_data


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_interview(interview: schemas.InterviewCreate, db: Session = Depends(get_db)):
    try:
        # Validate email and ensure user exists
        user = db.query(models.User).filter(models.User.email == interview.email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found with the provided email")

        # Create a new interview instance
        new_interview = models.Interview(
            title=interview.title,
            description=interview.description,
            user_id=user.id
        )
        db.add(new_interview)
        db.commit()
        db.refresh(new_interview)

        # (Optional) Handle questions if they need to be saved separately
        for question_text in interview.questions:
            question = models.Question(
                text=question_text,
                interview_id=new_interview.id
            )
            db.add(question)

        db.commit()

        return {"message": "Interview created successfully", "interview": new_interview}
    
    except ValidationError as e:
        # This will catch any Pydantic validation errors and return them in the response
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )
    except Exception as e:
        # General exception handling to catch unexpected errors
        db.rollback()  # Rollback the transaction in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the interview: {str(e)}"
        )

@router.get("/all")
def get_all_interviews(db: Session = Depends(get_db)):
    # Fetch all interviews without filtering by user
    interviews = db.query(models.Interview).all()
    interviews_data = [
        {
            "id": interview.id,
            "title": interview.title,
            "description": interview.description,
            "questions": [q.text for q in interview.questions],  # Assuming you have a questions relationship
            "taken": interview.taken,  # Ensure this line is included
            "score": interview.score
        }
        for interview in interviews
    ]
    
    return interviews_data


@router.get("/{interview_id}")
def get_interview_by_id(interview_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id, models.Interview.user_id == user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # If questions are a separate model, make sure they are fetched correctly
    interview_data = {
        "id": interview.id,
        "title": interview.title,
        "description": interview.description,
        "questions": [q.text for q in interview.questions] , # Assuming you have a questions relationship
        "taken": interview.taken,  # Ensure this line is included
        "score": interview.score
    }
    return interview_data


@router.put("/update/{interview_id}")
def update_interview(interview_id: int, interview: schemas.InterviewUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    existing_interview = db.query(models.Interview).filter(models.Interview.id == interview_id, models.Interview.user_id == user.id).first()
    if not existing_interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Update the interview fields if they are provided
    if interview.title is not None:
        existing_interview.title = interview.title
    if interview.description is not None:
        existing_interview.description = interview.description

    # Assuming questions need to be updated similarly
    if interview.questions is not None:
        # Remove old questions and add new ones
        db.query(models.Question).filter(models.Question.interview_id == interview_id).delete()
        for question_text in interview.questions:
            question = models.Question(
                text=question_text,
                interview_id=existing_interview.id
            )
            db.add(question)

    db.commit()
    db.refresh(existing_interview)

    return {"message": "Interview updated successfully", "interview": existing_interview}

@router.delete("/delete/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(interview_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id, models.Interview.user_id == user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Delete associated questions
    db.query(models.Question).filter(models.Question.interview_id == interview_id).delete()

    # Delete the interview
    db.delete(interview)
    db.commit()

    return {"message": "Interview deleted successfully"}


@router.post("/gpt-followup")
def gpt_followup(gpt_request: schemas.GPTFollowupRequest):
    try:
        # Build the prompt to ask for a follow-up question
        prompt = f"You are an AI interviewer. The only response you will generate will be follow up questions. It is as if you are conducting the interview and you are responding to the human like a human. The interviewee was asked the following question: '{gpt_request.previous_question}'. They responded with: '{gpt_request.previous_answer}'. Please generate a follow-up question based on their response. Before the follow up question, state a comment about their previous response in a professional manner."

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Replace with the desired model
            messages=[
                {"role": "system", "content": "You are an interviewer."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.7,
        )

        followup_question = response['choices'][0]['message']['content'].strip()

        return {"followup_question": followup_question}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while communicating with GPT: {str(e)}")

@router.post("/submit-conversation")
def submit_conversation(request: schemas.ConversationCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # Find the interview
    interview = db.query(models.Interview).filter(models.Interview.id == request.interview_id, models.Interview.user_id == user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    try:
        # Call GPT to calculate the score
        prompt = "Based on the following interview conversation, provide an integer score out of 100. You must only provide the number and no other text.\n\n"
        for q, a in request.conversation:
            prompt += f"Q: {q}\nA: {a}\n\n"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI scoring expert."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.7,
        )

        gpt_response = response['choices'][0]['message']['content'].strip()
        
        # Extract integer score from GPT response
        score = int(''.join(filter(str.isdigit, gpt_response)))

        # Update the interview with the score and mark it as taken
        interview.score = score
        interview.taken = True
        db.commit()

        return {"message": "Interview submitted successfully", "score": score}

    except ValueError:
        raise HTTPException(status_code=500, detail="Failed to parse the score from GPT response")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the conversation: {str(e)}")
