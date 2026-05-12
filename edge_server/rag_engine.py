import chromadb
from chromadb.utils import embedding_functions

# Initialize local ChromaDB
# This will create a 'medical_knowledge' folder to persist data
client = chromadb.PersistentClient(path="./medical_knowledge")

# Use a lightweight embedding model suitable for edge devices
# In a real scenario, you'd download the model files for fully offline use
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="paraphrase-multilingual-MiniLM-L12-v2")

collection = client.get_or_create_collection(
    name="triage_guidelines",
    embedding_function=embed_fn
)

def add_guideline(text, metadata):
    """Adds a medical guideline snippet to the vector store."""
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[str(hash(text))]
    )

def query_guidelines(query_text, n_results=2):
    """Searches for relevant medical guidelines based on patient symptoms."""
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results['documents'][0] if results['documents'] else []

import json
import uuid

def ingest_full_dataset(file_path):
    """Populates the vector database from a JSONL dataset."""
    print(f"Ingesting {file_path} into ChromaDB...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                item = json.loads(line)
                # Combine instruction and response for better context retrieval
                full_text = f"Instruction: {item['instruction']} | Protocol: {item['response']}"
                
                collection.add(
                    documents=[full_text],
                    metadatas=[{"context": item.get('context', 'general')}],
                    ids=[str(uuid.uuid4())]
                )
        print(f"Successfully ingested dataset from {file_path}")
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    except Exception as e:
        print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    # Path to your Kirundi dataset
    DATASET_PATH = "medical_dataset_kirundi.jsonl"
    ingest_full_dataset(DATASET_PATH)

