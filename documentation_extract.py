import re
import sys
import os
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from pypdf import PdfReader
from typing import List
import chromadb

def resource_path(relative_path):
    """Get the absolute path to a resource."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_pdf(file_path):
    """Read text from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def split_text(text: str) -> List[str]:
    """Split text into chunks."""
    split_text = re.split('\n \n', text)
    return [i for i in split_text if i != ""]

class GeminiEmbeddingFunction(EmbeddingFunction):
    """Embedding function using Gemini API."""
    
    def __call__(self, input: Documents) -> Embeddings:
        gemini_api_key = os.getenv("Gemini_API")
        if not gemini_api_key:
            raise ValueError("Gemini API Key not provided. Please provide Gemini_API as an environment variable")
        genai.configure(api_key=gemini_api_key)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model, content=input, task_type="retrieval_document", title=title)["embedding"]

def create_chroma_db(documents: List[str], path: str, name: str):
    """Create a Chroma DB collection."""
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
    for i, d in enumerate(documents):
        db.add(documents=d, ids=str(i))
    return db, name

def load_chroma_collection(path: str, name: str):
    """Load an existing Chroma DB collection."""
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())
    return db

def get_relevant_passages(query: str, db, n_results: int) -> List[str]:
    """Retrieve relevant passages from the Chroma DB."""
    results = db.query(query_texts=[query], n_results=n_results)['documents']
    return [item for sublist in results for item in sublist]

def make_rag_prompt(query: str, relevant_passages: List[str]) -> str:
    """Create a prompt for RAG model using relevant passages."""
    escaped = " ".join(relevant_passages).replace("'", "").replace('"', "").replace("\n", " ")
    prompt = ("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
    Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
    However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
    strike a friendly and conversational tone. \
    If the passage is irrelevant to the answer, you may ignore it.
    QUESTION: '{query}'
    PASSAGE: '{relevant_passage}'
    ANSWER:
    """).format(query=query, relevant_passage=escaped)
    return prompt

def generate_answer1(prompt: str) -> str:
    """Generate an answer using the Gemini API."""
    gemini_api_key = os.getenv("Gemini_API")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide Gemini_API as an environment variable")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    answer = model.generate_content(prompt)
    return answer.text

def generate_answer(db, query: str) -> str:
    """Generate an answer for a query using RAG approach."""
    relevant_passages = get_relevant_passages(query, db, n_results=3)
    if not relevant_passages:
        return "I'm sorry, but this document does not mention how to make a calculator using PyQt6, so I cannot answer this question."
    prompt = make_rag_prompt(query, relevant_passages)
    answer = generate_answer1(prompt)
    if not answer.strip():
        return "I'm sorry, but this document does not mention how to make a calculator using PyQt6, so I cannot answer this question."
    return answer

def main():
    pyqttext = load_pdf(file_path=resource_path("documentations/PyQt 6.pdf"))
    chunked_text = split_text(text=pyqttext)
    
    try:
        db = load_chroma_collection(path=resource_path("embeddings_cache"), name="rag_experiment")
        print("Collection already exists. Loaded the existing collection.")
    except Exception as e:
        print(f"Collection does not exist. Creating a new collection. Error: {e}")
        db, name = create_chroma_db(documents=chunked_text, path=resource_path("embeddings_cache"), name="rag_experiment")
    
    query = "How to make a calculator using PyQt6?"
    answer = generate_answer(db, query)
    print(answer)

if __name__ == "__main__":
    main()
