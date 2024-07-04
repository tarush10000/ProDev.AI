import re
import sys
import os
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
from pypdf import PdfReader
from typing import List
import chromadb
import numpy as np
from sentence_transformers import CrossEncoder

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def split_text(text: str) -> List[str]:
    # Split text into chunks, preserving code blocks and explanations
    chunks = []
    current_chunk = ""
    in_code_block = False
    
    for line in text.split('\n'):
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            current_chunk += line + '\n'
        elif in_code_block:
            current_chunk += line + '\n'
        else:
            if len(current_chunk) + len(line) > 1000:
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

class GeminiEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        gemini_api_key = os.getenv("Gemini_API")
        if not gemini_api_key:
            raise ValueError("Gemini API Key not provided. Please provide Gemini_API as an environment variable")
        genai.configure(api_key=gemini_api_key)
        model = "models/embedding-001"
        title = "Custom query"
        return genai.embed_content(model=model, content=input, task_type="retrieval_document", title=title)["embedding"]

def create_chroma_db(documents: List[str], path: str, name: str):
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
    for i, d in enumerate(documents):
        db.add(documents=d, ids=str(i))
    return db, name

def load_chroma_collection(path: str, name: str):
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())
    return db

def get_relevant_passages(query: str, db, n_results: int) -> List[str]:
    results = db.query(query_texts=[query], n_results=n_results)['documents']
    return [item for sublist in results for item in sublist]

def rank_documents(cross_encoder: CrossEncoder, query: str, retrieved_documents: List[str]):
    pairs = [[query, doc] for doc in retrieved_documents]
    scores = cross_encoder.predict(pairs)
    ranks = np.argsort(scores)[::-1]
    ranked_docs = {rank_num: doc for rank_num, doc in zip(ranks, retrieved_documents)}
    return ranked_docs

def make_rag_prompt(query: str, relevant_passages: List[str]) -> str:
    escaped = " ".join(relevant_passages).replace("'", "").replace('"', "").replace("\n", " ")
    prompt = f"""You are a helpful and informative bot that answers questions using text from the reference passage included below. 
    Provide a step-by-step guide on how to implement the requested functionality, including which files to create or modify and what code to input.
    Focus on providing only the necessary code and file structure information.
    If the passage is irrelevant to the answer, you may ignore it.
    QUESTION: '{query}'
    PASSAGE: '{escaped}'
    ANSWER:
    """
    return prompt

def generate_answer(prompt: str) -> str:
    gemini_api_key = os.getenv("Gemini_API")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide Gemini_API as an environment variable")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    answer = model.generate_content(prompt)
    return answer.text

def process_query(file_structure: str, user_request: str, tech_stack: str, db) -> str:
    query = f"Create {user_request} using {tech_stack} with the following file structure: {file_structure}"
    
    # Use Gemini API to create a smaller prompt for RAG searching
    gemini_api_key = os.getenv("Gemini_API")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide Gemini_API as an environment variable")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    rag_query = model.generate_content(f"Summarize the following query for RAG search: {query}").text
    
    relevant_passages = get_relevant_passages(rag_query, db, n_results=10)
    
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    ranked_docs = rank_documents(cross_encoder, rag_query, relevant_passages)
    
    if not ranked_docs:
        return generate_answer(query)
    
    prompt = make_rag_prompt(query, list(ranked_docs.values()))
    answer = generate_answer(prompt)
    
    if not answer.strip():
        return generate_answer(query)
    
    return answer

def main():
    embeddings_cache_path = resource_path("embeddings_cache")
    if not os.path.exists(embeddings_cache_path):
        os.makedirs(embeddings_cache_path)
        print("Created embeddings_cache folder.")
        
        documentation_folder = resource_path("documentations")
        all_text = ""
        for filename in os.listdir(documentation_folder):
            if filename.endswith(".pdf"):
                file_path = os.path.join(documentation_folder, filename)
                all_text += load_pdf(file_path)
        
        chunked_text = split_text(all_text)
        db, name = create_chroma_db(documents=chunked_text, path=embeddings_cache_path, name="rag_experiment")
        print("Created new collection with embeddings from all PDF files in the documentation folder.")
    else:
        try:
            db = load_chroma_collection(path=embeddings_cache_path, name="rag_experiment")
            print("Loaded existing collection.")
        except Exception as e:
            print(f"Error loading existing collection: {e}")
            return

    file_structure = input("Enter the file structure: ")
    user_request = input("What do you want to make? ")
    tech_stack = input("Enter the tech stack you're using: ")

    answer = process_query(file_structure, user_request, tech_stack, db)
    print(answer)

    # if "I am sorry" in answer:
    #     # generate response
    #     answer = ""

    while True:
        user_input = input("Do you want to continue the generation? (yes/no): ").lower()
        if user_input != 'yes':
            break
        continuation = generate_answer(f"Continue the previous answer: {answer}")
        print(continuation)
        answer += continuation

if __name__ == "__main__":
    main()