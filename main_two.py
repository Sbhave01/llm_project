import gradio as gr
import os
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
from redis_worker import process_resume
from utility.utils import save_uploaded_files 

load_dotenv()

# Environment variables
host_name = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT", 6379))
process_name = os.getenv("PROCESS_NAME")
UPLOAD_DIR=os.getenv("UPLOAD_DESTINATION")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Connect to Redis
redis_conn = Redis(host=host_name, port=redis_port)
resume_queue = Queue(process_name, connection=redis_conn)

def upload_and_process_files(files):
    # Save uploaded files to the UPLOAD_DIR
    file_paths = save_uploaded_files(files, UPLOAD_DIR)

    # Enqueue processing tasks
    for file_path in file_paths:
        resume_queue.enqueue(process_resume, file_path)

    return f"{len(files)} files uploaded successfully. Processing has been queued."


app = gr.Interface(
    fn=upload_and_process_files,
    inputs=gr.File(file_types=[".pdf", ".docx", ".txt"], label="Upload Resumes", type="filepath", file_count="multiple"),
    outputs=gr.Textbox(label="Upload Status"),
    title="Upload Candidate Resume",
    description="Upload resumes and let AI agent do the work !!"
)

if __name__ == "__main__":
    # app.launch()
    app.launch(server_name="0.0.0.0", server_port=7860,share=True)

