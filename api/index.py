import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import yfinance as yf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

# CORS so the frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    logger.info("Got root")
    return {"status": "ok"}


def get_stock_details(ticker):
    stock_data = yf.Ticker(ticker)
    return stock_data.info


@app.post("/api/chat")
def chat2(request: ChatRequest):
    logger.info(f"Got chat {request.__dict__}")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    try:
        user_message = request.message
        input_list=[
                {"role": "system", "content": "You are a supportive mental coach."},
                {"role": "user", "content": user_message}
        ]

        available_tools = {"get_stock_details": get_stock_details}
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_stock_details",
                    "description": "gets up to date stock information for a given stock symbol",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticker": {
                                "type": "string",
                                "description": "stock symbol to get details for"
                                }
                        },
                        "required": ["ticker"]
                    },
                }
            },
        ]
        model = "gpt-5"
        
        response = client.chat.completions.create(
            model=model,
            messages=input_list,
            tools=tools
        )
        if response.choices[0].message.tool_calls is None:
            return {"reply": response.choices[0].message.content}


        tool_calls_stream = client.chat.completions.create(
            messages=input_list,
            model=model,
            tools=tools,
            stream=True
        )

        chunks = []
        for chunk in tool_calls_stream:
            if len(chunk.choices) > 0:
                chunks.append(chunk)

        arguments = []
        tool_call_idx = -1
        for chunk in chunks:

            if chunk.choices[0].delta.tool_calls:
                tool_call = chunk.choices[0].delta.tool_calls[0]

                if tool_call.index != tool_call_idx:
                    if tool_call_idx >= 0:
                        print(
                            f"streamed tool call arguments: {arguments[tool_call_idx]}"
                        )
                    tool_call_idx = chunk.choices[0].delta.tool_calls[0].index
                    arguments.append("")
                if tool_call.id:
                    print(f"streamed tool call id: {tool_call.id} ")

                if tool_call.function:
                    if tool_call.function.name:
                        print(f"streamed tool call name: {tool_call.function.name}")

                    if tool_call.function.arguments:
                        arguments[tool_call_idx] += tool_call.function.arguments

        if len(arguments):
            print(f"streamed tool call arguments: {arguments[-1]}")

        print("\n\n")

        input_list.append({
            "role": "assistant",
            "tool_calls": response.choices[0].message.tool_calls
        })

        completion_tool_calls = response.choices[0].message.tool_calls
        for call in completion_tool_calls:
            tool_to_call = available_tools[call.function.name]
            args = json.loads(call.function.arguments)
            result = tool_to_call(**args)
            print(result)
            input_list.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": call.id,
                "name": call.function.name
            })
        
        response_2 = client.chat.completions.create(messages=input_list,
                                                        model=model,
                                                        tools=tools,
                                                        stream=False)
        
        
        print(response_2)
        return {"reply": response_2.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")

