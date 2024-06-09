from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse,StreamingResponse
from pydantic import BaseModel
from starlette.responses import FileResponse
import time


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"]
)

def foo():
    for i in range(10):
        time.sleep(1)
        yield b'foobar'


@app.post('/api/askpatentgpt')
async def bar(request:Request):
    data = await request.json()
    query = data.get("query", "")
    return StreamingResponse(foo(), media_type="text/event-stream")