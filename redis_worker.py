from rq import Queue, Worker
from redis import Redis
import os
from dotenv import load_dotenv
import sys
from rq import get_current_job
import logging
import json
import ollama
from utility.utils import * 
load_dotenv()

ollama_model = os.getenv('MODEL')

sentenct_transformer = os.getenv("TRANSFORMER1")
embedding_model = SentenceTransformer(sentenct_transformer)
# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
host_name = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_conn = Redis(host=host_name, port=redis_port)
queue_name = os.getenv("PROCESS_NAME")

print(queue_name,"-----------")


def process_resume(file_path):
    try:
        job = get_current_job()
        if job:
            logging.info(f"Processing job ID: {job.id}")
        print(os.getcwd(),"------",file_path)
        resume_content = extract_content(file_path)
        if "Error" in resume_content:
            raise ValueError(f"Error extracting content from {file_path}")

        # Ollama for LLM-based structured data extraction
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": resume_content}]
        response = ollama.chat(model=ollama_model, messages=messages)
        # Parse JSON response
        candidate_data = json.loads(response["message"]["content"])
        print("INSERT in DB ------------- ")
        candidate_id = insert_candidate_into_postgres(candidate_data)
        print("Insert done")
        #Generate embeddings and store
        embedding_text = prepare_embedding_text(candidate_data)
        embedding = embedding_model.encode(embedding_text)
        # embedding = embedding_model.encode(candidate_data)
        print("INSERT in chroma **************")
        collection.add(
            documents=[embedding_text],
            embeddings=[embedding],
            metadatas=[{"candidate_id": candidate_id, "domain": candidate_data.get("domain", "Unknown")}],
            ids=[str(candidate_id)]
        )

        logging.info(f"File processed successfully: {file_path} with candidate ID: {candidate_id}")
        return f"Processed {file_path} successfully."
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return f"Error processing file {file_path}: {e}"
    
if __name__ == "__main__":
    worker = Worker(queues=[queue_name], connection=redis_conn)
    worker.work()


