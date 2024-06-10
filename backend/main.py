from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from utils import get_results
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv(".env"))


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"]
)


WX_API_KEY = os.getenv("WX_API_KEY")
WX_PROJECT_ID = os.getenv("WX_PROJECT_ID")
IBM_CLOUD_URL = os.getenv("IBM_CLOUD_URL")
credentials = {
    "url": IBM_CLOUD_URL,
    "apikey": WX_API_KEY
}
model_id = "mistralai/mixtral-8x7b-instruct-v01"
parameters = {
    GenParams.DECODING_METHOD: "greedy",
    GenParams.MAX_NEW_TOKENS: 500
}
RAG_PROMPT = """<s>[INST] You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Please ensure that your responses are socially unbiased and positive in nature.
1. For a given query, you will be provided with the context information to help generate your answer. Ensure your response is relevant to the question and based on the provided context.
2. When the question cannot be answered using the context, just state that you do not have an answer. If you don't know the answer to a question, please don't share false information.
3. Do not add unnecessary or inaccurate information or use external sources to answer the question. 
4. Provide accurate and concise response in English as helpfully as possible.

Answer the following question using the provided context. 

Context:
{context_documents}

Question:
{question}
[/INST]</s>
"""


@app.get('/')
async def home():
    return JSONResponse(content={"message": "Welcome to PatentGPT backend"})


@app.post('/api/askpatentgpt')
async def bar(request:Request):
    data = await request.json()
    try: 
        query = data["query"].strip()
        db_results = get_results(query=query)
        model = Model(
            model_id=model_id, 
            params=parameters, 
            credentials=credentials,
            project_id=WX_PROJECT_ID
        )
        input_prompt = RAG_PROMPT.format(context_documents="\n\n".join(doc["Patent_Text"] for doc in db_results), question=query)
        print(input_prompt)
        return StreamingResponse(model.generate_text_stream(prompt=input_prompt), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Exception occurred: " + str(e))
