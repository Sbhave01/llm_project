import gradio as gr

from utility.utils import * 
from dotenv import load_dotenv
load_dotenv()

def match_candidates(file):
    try:
        logging.info(f"Job description file uploaded: {file.name}")
        job_description = extract_job_description(file)
        if not job_description or "Error" in job_description:
            logging.warning(f"Job description extraction failed: {job_description}")
            return [], "Error extracting job description. Please check the uploaded file."
        
        # Find the best candidates
        matched_candidates = find_best_candidates(job_description)

        if matched_candidates:
            logging.info("Matched candidates successfully retrieved.")
            table_data = [
                [
                    candidate["name"],
                    candidate["email"],
                    candidate["phone"],
                    candidate["linkedin"],
                    candidate["github"],
                    candidate["professional_summary"],
                    candidate["domain"],
                    candidate["retrieval_score"],
                ]
                for candidate in matched_candidates
            ]
            return table_data, f"Found {len(matched_candidates)} candidates that fits the requirement"
        else:
            logging.warning("No suitable candidates found.")
            return [], "No suitable candidates found."
    except Exception as e:
        logging.error(f"Error processing job description file: {e}")
        return [], f"Error processing job description file: {e}"



# job_matching_app = gr.Interface(
#     fn=match_candidates,
#     inputs=gr.File(file_types=[".docx", ".txt"], label="Upload Job Description"),
#     outputs="text",
#     title="Job Description Matching",
#     description="Upload a job description file (.txt or .docx) to find the top 3 matched candidates."
# )

# Custom CSS for table styling
CUSTOM_CSS = """
.gr-block .dataframe td {
    white-space: normal; /* Allow text to wrap */
    word-wrap: break-word; /* Break long words if necessary */
}
.gr-block .dataframe th {
    text-align: left; /* Align column headers to the left */
}
"""
# job_matching_app = gr.Interface(
#     fn=match_candidates,
#     inputs=gr.File(file_types=[".docx", ".txt"], label="Upload Job Description"),
#     outputs=[
#         gr.DataFrame(
#             headers=["Name", "Email", "Phone", "LinkedIn", "GitHub", "Summary", "Domain"],
#             label="Matched Candidates",
#         ),
#         gr.Textbox(label="Status"),
#     ],
#     title="Job Description Matching",
#     description="Upload a job description file (.txt or .docx) to find the top 3 matched candidates in a structured format."
# )

with gr.Blocks(css=CUSTOM_CSS) as job_matching_app:
    gr.Markdown("# Find the candidates")
    gr.Markdown("Upload a job description file (.txt or .docx) to find the candidates that fits the requirement ")
    file_input = gr.File(label="Upload Job Description", file_types=[".txt", ".docx"])
    output_table = gr.DataFrame(headers=["Name", "Email", "Phone", "LinkedIn", "GitHub", "Summary", "Domain", "Retrieval Score"])  # Added "Retrieval Score" column
    output_status = gr.Textbox(label="Status")
    match_button = gr.Button("Get Matched Candidates")

    match_button.click(fn=match_candidates, inputs=file_input, outputs=[output_table, output_status])



if __name__ == "__main__":
    # job_matching_app.launch() 
    job_matching_app.launch(share=True)