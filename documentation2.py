import sys
import os
from chromadb import Documents, EmbeddingFunction, Embeddings
import google.generativeai as genai
import pdfplumber
from typing import List
import chromadb
import numpy as np
from sentence_transformers import CrossEncoder
import shutil
import google.api_core.exceptions
import hashlib
import json

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def load_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
    except Exception as e:
        print(f"Error loading PDF {file_path}: {e}")
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
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return genai.embed_content(model=model, content=input, task_type="retrieval_document", title=title)["embedding"]
            except google.api_core.exceptions.InternalServerError as e:
                if attempt < max_retries - 1:
                    print(f"Retrying due to server error: {e}")
                    continue
                else:
                    raise

def delete_chroma_db(path: str, name: str):
    try:
        chroma_client = chromadb.PersistentClient(path=path)
        chroma_client.delete_collection(name=name)
        print(f"Deleted collection {name} from {path}")
    except Exception as e:
        print(f"Error deleting collection {name}: {e}")

def create_or_update_chroma_db(documents: List[str], path: str, name: str, metadata_path: str):
    chroma_client = chromadb.PersistentClient(path=path)
    metadata = load_metadata(metadata_path)

    try:
        db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())
        print(f"Updating existing collection: {name}")
    except ValueError:
        db = chroma_client.create_collection(name=name, embedding_function=GeminiEmbeddingFunction())
        print(f"Created new collection: {name}")

    # Find the last processed ID
    last_processed_id = max(map(int, metadata.keys()), default=-1)
    print(f"Continuing from ID: {last_processed_id + 1}")

    for i, d in enumerate(documents):
        doc_id = str(i)
        if i > last_processed_id:
            db.add(documents=d, ids=doc_id)
            metadata[doc_id] = True  # Mark this document as processed

    save_metadata(metadata, metadata_path)
    return db, name

def load_chroma_collection(path: str, name: str):
    try:
        chroma_client = chromadb.PersistentClient(path=path)
        db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())
        return db
    except Exception as e:
        print(f"Error loading Chroma collection {name}: {e}")
        return None

def get_relevant_passages(query: str, db, n_results: int) -> List[str]:
    try:
        results = db.query(query_texts=[query], n_results=n_results)['documents']
        return [item for sublist in results for item in sublist]
    except Exception as e:
        print(f"Error querying relevant passages: {e}")
        return []

def rank_documents(cross_encoder: CrossEncoder, query: str, retrieved_documents: List[str]):
    try:
        pairs = [[query, doc] for doc in retrieved_documents]
        scores = cross_encoder.predict(pairs)
        ranks = np.argsort(scores)[::-1]
        ranked_docs = {rank_num: doc for rank_num, doc in zip(ranks, retrieved_documents)}
        return ranked_docs
    except Exception as e:
        print(f"Error ranking documents: {e}")
        return {}

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

def handle_document_upload(documentation_folder: str, embeddings_cache_path: str, metadata_path: str):
    user_response = input("No documents found. Do you want to upload a document? (yes/no): ").strip().lower()
    if user_response != 'yes':
        print("No document uploaded. Exiting.")
        sys.exit()

    file_path = input("Enter the path of the PDF document to upload: ").strip()
    if not os.path.isfile(file_path) or not file_path.endswith(".pdf"):
        print("Invalid file. Please upload a valid PDF document.")
        sys.exit()

    destination_path = os.path.join(documentation_folder, os.path.basename(file_path))
    try:
        os.rename(file_path, destination_path)
        print(f"Document {os.path.basename(file_path)} uploaded to {documentation_folder}.")
    except Exception as e:
        print(f"Error moving file: {e}")
        sys.exit()

    if not os.path.exists(embeddings_cache_path):
        os.makedirs(embeddings_cache_path)
        print("Created new embeddings_cache folder.")

    all_text = ""
    metadata = load_metadata(metadata_path)

    for filename in os.listdir(documentation_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(documentation_folder, filename)
            file_checksum = compute_md5(file_path)

            if filename in metadata and metadata[filename]['checksum'] == file_checksum:
                print(f"Skipping {filename}, embeddings already exist.")
                continue

            text = load_pdf(file_path)
            all_text += text

            # Update metadata
            metadata[filename] = {'checksum': file_checksum}

    chunked_text = split_text(all_text)
    db, name = create_or_update_chroma_db(documents=chunked_text, path=embeddings_cache_path, name="rag_experiment")
    if db is None:
        sys.exit("Failed to create Chroma DB.")

    save_metadata(metadata, metadata_path)
    print("Created new collection with embeddings from all PDF files in the documentation folder.")
    return db

def delete_embeddings_cache(path: str):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            print("Deleted existing embeddings_cache directory.")
    except Exception as e:
        print(f"Error deleting embeddings_cache directory: {e}")

def generate_answer(prompt: str) -> str:
    gemini_api_key = os.getenv("Gemini_API")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide Gemini_API as an environment variable")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    try:
        answer = model.generate_content(prompt)
        return answer.text
    except Exception as e:
        print(f"Error generating answer: {e}")
        return ""

def process_query(file_structure: str, user_request: str, tech_stack: str, db) -> str:
    query = f"Create {user_request} using {tech_stack} with the following file structure: {file_structure}"
    
    # Use Gemini API to create a smaller prompt for RAG searching
    gemini_api_key = os.getenv("Gemini_API")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide Gemini_API as an environment variable")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    try:
        rag_query = model.generate_content(f"Summarize the following query for RAG search: {query}").text
    except Exception as e:
        print(f"Error generating RAG query: {e}")
        return ""
    
    relevant_passages = get_relevant_passages(rag_query, db, n_results=10)
    if not relevant_passages:
        return generate_answer(query)
    
    cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    ranked_docs = rank_documents(cross_encoder, rag_query, relevant_passages)
    if not ranked_docs:
        return generate_answer(query)
    
    prompt = make_rag_prompt(query, list(ranked_docs.values()))
    answer = generate_answer(prompt)
    if not answer.strip():
        return generate_answer(query)
    
    return answer

def load_metadata(metadata_path):
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return {}

def save_metadata(metadata, metadata_path):
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)

def compute_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def main():
    embeddings_cache_path = resource_path("embeddings_cache")
    documentation_folder = resource_path("documentations")
    metadata_path = os.path.join(embeddings_cache_path, "metadata.json")

    if not os.path.exists(embeddings_cache_path):
        os.makedirs(embeddings_cache_path)
        print("Created embeddings_cache folder.")
    print("Loading the documentation folder...")

    if not os.path.exists(documentation_folder):
        os.makedirs(documentation_folder)
        print("Created documentations folder.")
    print("Loading PDF files from the documentation folder...")

    all_text = ""
    for filename in os.listdir(documentation_folder):
        if filename.endswith(".pdf"):
            file_path = os.path.join(documentation_folder, filename)
            all_text += load_pdf(file_path)

    chunked_text = split_text(all_text)
    print("Loaded PDF files from the documentation folder.")

    try:
        db, name = create_or_update_chroma_db(documents=chunked_text, path=embeddings_cache_path, name="rag_experiment", metadata_path=metadata_path)
        print("Processed embeddings for all PDF files in the documentation folder.")
    except Exception as e:
        print(f"Error creating or updating Chroma DB: {e}")
        return

    file_structure = input("Enter the file structure: ")
    user_request = input("What do you want to make? ")
    tech_stack = input("Enter the tech stack you're using: ")

    answer = process_query(file_structure, user_request, tech_stack, db)
    print(answer)

    while True:
        user_input = input("Do you want to continue the generation? (yes/no): ").lower()
        if user_input != 'yes':
            break
        continuation = generate_answer(f"Continue the previous answer: {answer}")
        print(continuation)
        answer += continuation

if __name__ == "__main__":
    main()