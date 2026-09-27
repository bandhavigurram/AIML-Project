# Zepto Policy RAG Assistant

## Project Overview

This project is a simple Retrieval-Augmented Generation (RAG) application for answering Zepto policy-related customer questions.

The application:

- Reads policy documents from text files
- Converts them into embeddings using a Sentence Transformer model
- Stores embeddings in ChromaDB
- Accepts customer questions through a FastAPI endpoint
- Retrieves relevant policy content
- Returns an answer based on the retrieved information

---

## Technologies Used

- Python
- FastAPI
- Sentence Transformers
- ChromaDB
- Pydantic
- LangGraph (imported for future workflow usage)

---

## Project Flow

1. Load policy documents from the `docs` folder.
2. Generate embeddings for each document.
3. Store embeddings in ChromaDB.
4. Receive a customer query.
5. Identify whether the query is policy-related.
6. Retrieve the most relevant policy documents.
7. Generate and return an answer.


## Code Explanation

### 1. Path Configuration

```python
base_dir = Path(__file__).resolve().parent
docs_dir = base_dir / "docs"
chroma_dir = base_dir / "chroma_db"
```

Defines locations for:
- Policy documents
- ChromaDB storage


### 2. Load Embedding Model

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
```

Loads a pre-trained embedding model.

Purpose:
- Convert text into numerical vectors.
- Helps perform semantic search.


### 3. Connect to ChromaDB

```python
client = chromadb.PersistentClient(path=str(chroma_dir))
```

Creates a persistent ChromaDB database.

Purpose:
- Store embeddings permanently.
- Avoid losing data between runs.


### 4. Read Policy Documents

```python
for file_path in sorted(docs_dir.glob("*.txt")):
```

Reads all text files from the docs folder.

Purpose:
- Load Zepto policies into memory.


### 5. Generate Embeddings

```python
embeddings = model.encode(
    chunks,
    normalize_embeddings=True
).tolist()
```

Converts policy text into vector embeddings.

Purpose:
- Enable similarity search.


### 6. Store Data in ChromaDB

```python
zepto_docs.upsert(...)
```

Stores:
- Document IDs
- Document text
- Embeddings
- Metadata

Purpose:
- Make documents searchable.


### 7. Prompt Template

```python
prompt_template = Template(...)
```

Creates a reusable prompt template.

Purpose:
- Provide context and instructions to an LLM.
- Currently prepared for future LLM integration.


### 8. State Definition

```python
class State(TypedDict):
```

Stores:

- query
- intent
- context
- answer

Purpose:
- Maintain information throughout processing.


### 9. API Request and Response Models

```python
class AskRequest(BaseModel)
class FinalAnswer(BaseModel)
```

Purpose:

- Validate API requests.
- Standardize API responses.


### 10. Intent Classification

```python
def classify_intent(state):
```

Checks whether the question contains keywords such as:

- delivery
- refund
- cancel
- membership

Purpose:
- Decide if the query is policy-related.


### 11. Retrieve Relevant Documents

```python
def retrieve_and_answer(state):
```

Steps:

1. Convert query into an embedding.
2. Search ChromaDB.
3. Retrieve top matching documents.

Purpose:
- Find the most relevant policy information.


## API Endpoint

### POST /ask

Example Request

```json
{
  "query": "What is the delivery fee for orders below INR 149?"
}
```

Example Response

```json
{
  "answer": "Based on the retrieved context: doc_01 — Delivery Policy: \"Zepto delivers grocery and household essentials to serviceable pin codes within 10 to 30 minutes of order confirmation, depending on the customer's delivery zone and current",
  "sources": [
    "doc1",
    "doc5",
    "doc7"
  ],
  "confidence": 1
}
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

to test the API.


## Current Limitations

- Uses simple keyword-based intent classification.
- Uses mock LLM responses.
- LangGraph is imported but not yet implemented.
- Documents are reprocessed on startup.


## Future Improvements

- Integrate a real LLM.
- Implement LangGraph workflow.
- Add document chunking.
- Add confidence scoring.
- Improve intent classification using semantic methods.
