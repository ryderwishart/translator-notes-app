import chromadb
from chromadb.utils import embedding_functions
import csv
from typing import List
import os

def load_template_docs(input: str) -> List[str]:
    # path /Users/ryderwishart/genesis/content_generation_pocs/translator-notes-app/templates.tsv
    with open('/Users/ryderwishart/genesis/content_generation_pocs/translator-notes-app/backend/templates.tsv', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Remove header if present
    if lines and lines[0].startswith('Template'):
        lines = lines[1:]
    
    # Split input into words
    input_words = set(input.lower().split())
    
    # Calculate similarity scores
    similarities = []
    for line in lines:
        template_words = set(line.lower().split())
        difference = len(input_words.symmetric_difference(template_words))
        similarities.append((difference, line.strip()))
    
    # Sort by similarity (smallest difference first) and get top 10
    similarities.sort(key=lambda x: x[0])
    top_10_templates = [template for _, template in similarities[:10]]
    
    return top_10_templates

class ChromaDBManager:
    def __init__(self, collection_name, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        # Create a persistent client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name, 
            embedding_function=self.embedding_function
        )

    def add_documents(self, tsv_file_path):
        with open(tsv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            documents = []
            metadatas = []
            ids = []
            for i, row in enumerate(reader):
                doc_id = f"doc_{i}"
                # Check if the document is already in the collection
                if not self.collection.get(ids=[doc_id])['ids']:
                    documents.append(row['Note'])
                    metadatas.append({
                        'Reference': row['Reference'],
                        'ID': row['ID'],
                        'Tags': row['Tags'],
                        'SupportReference': row['SupportReference'],
                        'Quote': row['Quote'],
                        'Occurrence': row['Occurrence']
                    })
                    ids.append(doc_id)

            if documents:  # Only add if there are new documents
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

    def query(self, query_text, n_results=10):
        print('Querying chroma db for', n_results)
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['metadatas', 'documents', 'distances']
        )
        
        # Let's also add into our results a template_docs[] 
        # these are the template docs 
        template_docs = load_template_docs(query_text)
        results['template_docs'] = template_docs
        
        return results