from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, field_validator
from database import ChromaDBManager
from bible_utils import BibleManager
from prompt_generator import PromptGenerator
from llm_interface import LLMInterface
from typing import List, Union
import os

app = FastAPI()

# Initialize components
chroma_manager = ChromaDBManager("my_collection")
bible_manager = BibleManager("./data/bsb-utf8.txt")
prompt_generator = PromptGenerator(chroma_manager, bible_manager)
llm_interface = LLMInterface()

# Embed initial documents
initial_file_path = "./data/en_tn/combined.txt"
if os.path.exists(initial_file_path):
    chroma_manager.add_documents(initial_file_path)
else:
    raise FileNotFoundError(f"Initial file '{initial_file_path}' not found")

class QueryInput(BaseModel):
    query: str
    verse_reference: str

class EmbedDocumentsInput(BaseModel):
    file_paths_or_folder: Union[List[str], str]

    @field_validator('file_paths_or_folder')
    @classmethod
    def validate_input(cls, v):
        if isinstance(v, str):
            if not os.path.exists(v):
                raise ValueError(f"The path '{v}' does not exist")
        elif isinstance(v, list):
            for path in v:
                if not os.path.exists(path):
                    raise ValueError(f"The path '{path}' does not exist")
        else:
            raise ValueError("Input must be a string (folder path) or a list of strings (file paths)")
        return v

@app.post("/embed_documents")
async def embed_documents(input_data: EmbedDocumentsInput):
    try:
        file_paths_or_folder = input_data.file_paths_or_folder
        tsv_files = []

        if isinstance(file_paths_or_folder, str):
            if os.path.isdir(file_paths_or_folder):
                for file in os.listdir(file_paths_or_folder):
                    if file.endswith('.tsv'):
                        tsv_files.append(os.path.join(file_paths_or_folder, file))
            else:
                raise ValueError(f"'{file_paths_or_folder}' is not a valid directory")
        elif isinstance(file_paths_or_folder, list):
            for path in file_paths_or_folder:
                if os.path.isdir(path):
                    for file in os.listdir(path):
                        if file.endswith('.tsv'):
                            tsv_files.append(os.path.join(path, file))
                elif path.endswith('.tsv'):
                    tsv_files.append(path)
                else:
                    raise ValueError(f"'{path}' is not a valid .tsv file or directory")

        # Embed documents
        for tsv_file_path in tsv_files:
            chroma_manager.add_documents(tsv_file_path)

        return {"message": "Documents embedded successfully", "files_processed": len(tsv_files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear_database")
async def clear_database():
    try:
        chroma_manager.clear_collection()
        return JSONResponse(content={"message": "Database cleared successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_response")
async def generate_response(input_data: QueryInput):
    try:
        prompt = prompt_generator.generate_prompt(input_data.query, input_data.verse_reference)
        response = llm_interface.get_completion(prompt)
        verse = bible_manager.get_verse(input_data.verse_reference)
        return {"response": response, "verse": verse}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check_verse_string")
async def check_verse_string(query: str):
    """
    Use this to double check verse ref strings to make sure you are getting the verse you want
    """
    return bible_manager.get_verse(query)

class ChromaQueryInput(BaseModel):
    query: str
    
@app.post("/query_chroma")
async def query_chroma(input_data: ChromaQueryInput, n_results: int = 10):
    try:
        response = chroma_manager.query(input_data.query, n_results)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve Svelte app
app.mount("/", StaticFiles(directory="../svelte-frontend/dist", html=True), name="static")

@app.get("/{full_path:path}")
async def serve_svelte(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")
    return FileResponse("../svelte-frontend/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8078, reload=True)