from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel
from typing import Literal
import time
import logging

load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "http://localhost:3000",  # Allow localhost for development
    "http://your-production-url.com",  # Allow your production URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai_client = OpenAI(
    api_key = os.getenv("OPEN_AI_API_KEY"),
    organization = os.getenv("OPENAI_ORGANIZATION_ID"),
    project = os.getenv("OPENAI_PROJECT_ID")
)




@app.get("/")
async def read_root():
    assistant_id = os.getenv("OPEN_AI_ASSISTANT_ID")
    if assistant_id is not None:
        assistant = openai_client.beta.assistants.retrieve(assistant_id)
        print(assistant)
        return {"messsage": f"Hello, Bob. I'm your new assistant, {assistant.name}."}
    else:
        return {"message": "Error: No assistant found. Please create an assistant first."}

@app.post("/assistant/create-thread")
async def create_thread():
    logging.info("Creating a new thread")
    response = openai_client.beta.threads.create()
    logging.info(response)
    return {
        "message": "What can I help you with today?",
        "thread_id": response.id
    }

class MessageRequest(BaseModel):
    message: str
    role: Literal["user", "assistant"]

@app.post("/assistant/messages/{thread_id}")
async def send_message(thread_id: str, request: MessageRequest):
    message = openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        content=request.message,
        role=request.role
    )

    run = openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=os.getenv("OPEN_AI_ASSISTANT_ID") or "assistant-id",
        instructions="Please respond to the user's message as clearly and simply as possible using the Feynman technique.",
    )

    while True:
        run_status = openai_client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        print(run_status.status)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            return {"message": "Error: Run failed."}
        time.sleep(1)
    messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
    print(messages.data)
    # Get the last messa
    number_of_messages = len(messages.data)
    print(number_of_messages)
    for message in messages.data:
        role = message.role  
        if role == "assistant":
            for content in message.content:
                if content.type == "text":
                    return {"message": content.text.value}
            return {"message": message.content}

@app.get("/assistant/messages/{thread_id}")
async def get_messages(thread_id: str):
    messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data