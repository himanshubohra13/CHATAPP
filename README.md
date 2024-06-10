# Conversational AI ChatBot with Voice Features
<br>

## Features 
1. Type or Record User Query vis microphone
2. Speech Recognition: Utilizing Web Speech API
3. Efficient and Fast retrieval via Milvus VectorDB
4. Conversational Chain: Using Llama3
5. LLM Response Streaming in React UI
6. Speech Synthesizer: Using IBM TTS to synthesize LLM response as audio
<br>

## RAG Pipeline
1. Data Preprocessing
   - Web scrapped open-source Patent related data (Automotive domain) and store them as CSV data
2. Retriever
   - Using Langchain to create documents and Milvus vectorDB locally installed via Podman for storage
3. Search
   - Using LLama3 model hosted via IBM WatsonX.ai for answer generation and streaming response in real-time on React UI
<br>

## Steps to setup Milvus locally via Podman

We need three containers to run a Milvus standalone server:
  - etcd: a distributed key value store for metadata storage and access
  - minio: AWS S3-compatible persistent storage for logs and index files
  - milvus: the database server
Rather than configure and run each container individually, we are using Podman Compose to connect and orchestrate them.

1. Open the terminal and update the system package repository by running:

```
sudo apt update
```

2. Install Podman with the following command:
```
sudo apt -y install podman
```

Similarly, install the podman-compose in your system.

3. Download `milvus-standalone-docker-compose.yml` file via wget command or you can find it in assets folder
```
wget https://github.com/milvus-io/milvus/releases/download/v2.4.4/milvus-standalone-docker-compose.yml -O docker-compose.yml
```

4. In the same folder, run following command:
```
podman compose up -d
```

5. To check these three containers running, run:
```
podman ps -a
```

6. To check on the Milvus server with docker logs, run:
```
podman logs milvus-standalone
```
<br>

## Steps to run RAG Pipeline

1. Rename the `sample.env` file to `.env`. Add your credentials.
2. Navigate to `backend` folder
```
uvicorn main:app --reload
```
3. Now move to `frontend` folder and start the frontend server to start interacting with ChatBot UI.
<br>

## UI Screenshots
