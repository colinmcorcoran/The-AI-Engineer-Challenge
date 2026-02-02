# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
from typing import Optional
import logging

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    # Backwards-compatible: accept either a single `message`, or `developer_message` + `user_message`.
    message: Optional[str] = None
    developer_message: Optional[str] = ""  # Message from the developer/system
    user_message: Optional[str] = ""      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: Optional[str] = None          # OpenAI API key for authentication (optional)
    stream: Optional[bool] = False         # Whether to stream response (default False for compatibility)

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    logger.info(f"Received chat request: message='{request.message}', developer_message='{request.developer_message}', user_message='{request.user_message}', model='{request.model}', stream={request.stream}")
    try:
        # Prefer provided API key, fallback to environment variable
        api_key = request.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

        client = OpenAI(api_key=api_key)

        # Build messages depending on payload shape
        if request.message:
            messages = [
                {"role": "system", "content": "You are a supportive mental coach."},
                {"role": "user", "content": request.message}
            ]
        else:
            # Use developer and user roles if provided
            dev_content = request.developer_message or "You are a supportive mental coach."
            messages = [
                {"role": "developer", "content": dev_content},
                {"role": "user", "content": request.user_message}
            ]

        # If streaming requested, stream text/plain chunks
        if request.stream:
            async def generate():
                stream = client.chat.completions.create(
                    model=request.model,
                    messages=messages,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        logger.debug(f"Streaming chunk: {chunk.choices[0].delta.content}")
                        yield chunk.choices[0].delta.content

            logger.info("Starting streaming response to client.")
            return StreamingResponse(generate(), media_type="text/plain")

        # Otherwise, do a single request and return JSON
        logger.info("Performing non-streaming completion.")
        response = client.chat.completions.create(
            model=request.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /api/chat: {str(e)}")
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    logger.info("Health check requested.")
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
