from fastapi import FastAPI
from openai import OpenAI
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv()
app = FastAPI()

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

@app.get("/assistant/create-thread")
async def create_thread():
    response = openai_client
    return response
