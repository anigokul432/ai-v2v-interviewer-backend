# AI Interview Bot API

This repository contains the backend API for an AI Interview Bot, built with FastAPI. The API allows users to conduct and manage interviews, with features such as user authentication, interview creation, and AI-generated follow-up questions. The application is designed to be used with a frontend hosted on multiple domains.

## Features

- **User Management**: Create and manage users with secure authentication.
- **Interview Management**: Create, update, and delete interviews with associated questions and recordings.
- **AI Integration**: Generate AI-powered follow-up questions and interview scoring using OpenAI's GPT model.
- **Conversation Tracking**: Store and manage conversations during interviews with timestamps and recordings.
- **CORS Support**: Configured to allow requests from multiple frontend domains.

## Project Structure

- **main.py**: The entry point of the application. Initializes the FastAPI app, sets up CORS, and includes the routers.
- **models.py**: Defines the SQLAlchemy ORM models for users, interviews, questions, and conversations.
- **schemas.py**: Defines Pydantic models for request validation and response serialization.
- **database.py**: Configures the database connection and session management using SQLAlchemy.
- **routers/**: Contains route handlers for users, interviews, and authentication.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/anigokul432/ai-interview-bot-api.git
   cd ai-interview-bot-api
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with the following variables:
   ```
   DATABASE_URL=your_database_url
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   LLM_API_KEY=your_openai_api_key
   ```

4. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

## Usage

- Access the API documentation at `http://localhost:8000/docs` or `http://localhost:8000/redoc`.
- The API root endpoint returns a welcome message.

## Deployment

- Configure the `allow_origins` in `main.py` to include your production frontend domains.
- Deploy the FastAPI application on your preferred cloud platform (e.g., Azure, AWS, Heroku).

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements.