from typing import List, Annotated
from pydantic import BaseModel
from fastapi import FastAPI, status, Body
from fastapi.responses import StreamingResponse
from datetime import datetime
import json

from llama_query import generate_response  # Ensure this is correctly imported and available

app = FastAPI()

class Query(BaseModel):
    query: str

class ResponseItem(BaseModel):
    event_id: int
    time: str
    data: str

"""
    Root endpoint that returns a simple greeting message.

    Returns:
        dict: A dictionary containing a greeting message.
"""
@app.get('/')
async def read_root():
    return {"hello": "world"}


"""
    Endpoint to generate and stream AI response based on the provided query.

    Args:
        q (Query): The query model containing the query string.

    Returns:
        StreamingResponse: A streaming response with JSON data.
"""
@app.post("/api/ai/response/", status_code=status.HTTP_201_CREATED)
async def post_query(
    q: Annotated[
        Query,
        Body(
            example={
                "query": "What is Tesla's greatest invention?"
            }
        ,description="Input your Query here", title="Query input") #idk why it didnt work here
    ]
):
    response = generate_response(q.query)
    
    """
        Asynchronous generator function that yields JSON formatted response items.
        
        Yields:
            str: JSON formatted response item.
    """
    async def wrapped_response():
        event_id = 0
        async for part in response:
            current_time = datetime.now().isoformat()
            # Strip double quotes from the data field
            part = part.strip().strip('"')
            response_item = ResponseItem(event_id=event_id, time=current_time, data=part)
            json_data = json.dumps(response_item.dict()).strip()  # Ensure trimming
            yield json_data +'\n'
            event_id += 1

    return StreamingResponse(wrapped_response(), media_type="application/json")

