from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from string import Template
from typing import TypedDict
import os
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field, ValidationError
from fastapi import FastAPI

#path to import docs to charoma db
base_dir = Path(__file__).resolve().parent
docs_dir = base_dir / "docs"
chroma_dir = base_dir / "chroma_db"

# load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

#connects to chromaDB database
client = chromadb.PersistentClient(path=str(chroma_dir))
# create documents collection
zepto_docs = client.get_or_create_collection(
    name="zepto_policies"
)
#read documents
documents = []
document_ids = []
metadatas = []
#load all documnets into a list
for file_path in sorted(docs_dir.glob("*.txt")):
    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        continue
    documents.append(text)
    document_ids.append(file_path.stem)
    metadatas.append({
        "source": file_path.name
    })
#create chunks
chunks = documents
chunk_ids = document_ids
chunk_metadatas = metadatas
#generate embeddings
embeddings = model.encode(chunks,normalize_embeddings=True).tolist()
#store embeddings and docs in chromaDB
zepto_docs.upsert(
    ids=chunk_ids,
    documents=chunks,
    embeddings=embeddings,
    metadatas=chunk_metadatas
)
prompt_template = Template("""
Role:
You are a Zepto customer support assistant.
You answer questions using only the provided Zepto policy context.

Context:
$context

Task:
Answer the customer's question using the provided context.

If the question is about a Zepto policy, give a direct and concise answer.
If the provided context does not contain enough information to answer the question,
say that the information is not available in the provided Zepto policy context.

Negative constraint:
Do not use information that is not present in the provided context.
Do not make up or assume policy details.

Format:
Return the answer as plain text.
Do not include a separate explanation of your reasoning.
Keep the answer customer-friendly and factual.

Length:
Keep the answer between 1 and 3 sentences.

Few-shot example:
Example question:
"What is the delivery fee for an order below INR 149?"

Example context:
"Standard delivery is free on orders over INR 149; orders below this threshold
incur a flat INR 25 delivery fee."

Example answer:
"Orders below INR 149 incur a flat INR 25 standard delivery fee."

Customer Question:
$question

Answer:
""")

def build_prompt(context, question):
    return prompt_template.substitute(
        context=context,
        question=question
    )

#LangGraph State 
class State(TypedDict):
    query: str
    intent: str
    context: str
    answer: str

#output schema in JSON format
class FinalAnswer(BaseModel):
    answer: str
    sources: list[str]
    confidence: float = Field(
        ge=0.0,
        le=1.0
    )
#FastAPI
class AskRequest(BaseModel):
    query: str
app = FastAPI()

#classify intent
def classify_intent(state):
    query = state["query"].lower()
    # Check MOCK_LLM
    mock_llm = os.getenv('MOCK_LLM', '1')

    #required mock mode
    if mock_llm == '1':
        policy_keywords = ["delivery", "return", "refund", "membership",
                            "tracking", "cancel", "gift card", "support hours"]
        if any (keyword in query 
                for keyword in policy_keywords):
            intent = "policy_question"
        else:
            intent = "general_question"
    
    return intent

#retrieve_and_answer 
def retrieve_and_answer(state):
    query = state["query"]
    #create embedding for query
    query_embedding = model.encode(query,normalize_embeddings=True).tolist()
    #retieve top-3 chunks from chromaDB
    results = zepto_docs.query(query_embeddings=[query_embedding],n_results=3)
    retrieved_documents = results["documents"][0]
    retrieved_ids = results["ids"][0]
    #combine retrieved context
    context = "\n\n".join(retrieved_documents)
    #Mock LLM call
    mock_llm = os.getenv('MOCK_LLM','1')
    if mock_llm == '1':
        #top_chunk_snippet from doc
        top_chunck = retrieved_documents[0]
        # get 200 characters snippet
        top_chunk_snippet = top_chunck[:200]
        ans = (f"Based on the retrieved context: {top_chunk_snippet}")
        final_answer = FinalAnswer(
            answer=ans,
            sources=retrieved_ids,
            confidence=1.0
        )
        #validate schema and convert to dictionary
        validated_answer = final_answer.model_dump()
    return context, validated_answer

#direct_answer 
def direct_answer(state):
    mock_llm = os.getenv('MOCK_LLM','1')
    if mock_llm == '1':
        ans = '''I can only answer questions about Zepto policies right now.'''
    final_answer = FinalAnswer(
            answer=ans,
            sources=[],
            confidence=1.0
        )
    validated_answer = final_answer.model_dump()
    return validated_answer

#process query
def process_query(state):
    que_intent = classify_intent(state)
    # store intent in state
    state["intent"] = que_intent
    if que_intent == "policy_question":
        context, ans = retrieve_and_answer(state)
        result = {
            "context" : context,
            "answer"  : ans["answer"]
        }
    else:
        ans = direct_answer(state)
        result = {
            "answer" : ans["answer"]
        }
    #update state with result
    state.update(result)
    return {
        "query": state["query"],
        "intent": state["intent"],
        "context": state["context"],
        "answer": ans
    }

@app.post("/ask", response_model=FinalAnswer)
def ask(request: AskRequest):
    state = {
        "query": request.query,
        "intent": "",
        "context": "",
        "answer": ""
    }
    result = process_query(state)
    return FinalAnswer(**result["answer"])

# to run on your own without FastAPI
'''if __name__ == "__main__":
    query = input("Enter a query: ")
    state = {
        "query": query,
        "intent": "",
        "context": "",
        "answer": ""
    }
    # Call process_query()
    result = process_query(state)
    print("\nQuestion:")
    print(result["query"])
    print("\nIntent:")
    print(result["intent"])
    print("\nContext:")
    print(result["context"])
    print("\nFinal JSON output:")
    print(result["answer"])'''

