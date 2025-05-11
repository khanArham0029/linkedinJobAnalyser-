# app.py

import gradio as gr
from agents.jobextractor import get_job_details_by_id
from agents.jobanalyser import job_analyser_agent
import asyncio
import fitz

def extract_text_from_pdf(pdf_file) -> str:
    doc = fitz.open(pdf_file.name)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

async def analyze_job_fit(job_id: str, cv_file, cv_text: str):
    if cv_file is not None:
        cv = extract_text_from_pdf(cv_file)
    elif cv_text.strip():
        cv = cv_text.strip()
    else:
        return "❌ Please upload a PDF or paste your CV."

    jobs = get_job_details_by_id([job_id])
    if not jobs:
        return "❌ Could not fetch job details. Please check the Job ID."

    job = jobs[0]
    job_info = job["job_info"]
    company_info = job["company_info"]

    job_text = f"""
Job Title: {job_info['title']}
Company: {company_info['name']}
Location: {job_info.get('location', 'N/A')}
Description: {job_info['description']}
    """

    llm_input = f"""
Compare the following job with the user's CV.

=== Job Posting ===
{job_text}

=== User CV ===
{cv}

Return a JSON with:
- summary (summary of the job)
- score (0–100 confidence score on match)
- required_skills (from the job)
- cv_recommendations (what the user should change/add to their CV)
    """

    result = await job_analyser_agent.run(llm_input)
    output = result.output[0]

    return (
        f"### 📝 Job Summary\n{output.summary}\n\n"
        f"### 🔍 Confidence Score: **{output.score}** / 100\n\n"
        f"### 🛠️ Required Skills:\n- " + "\n- ".join(output.required_skills) + "\n\n"
        f"### 🧠 CV Recommendations:\n- " + "\n- ".join(output.cv_recommendations)
    )


# Gradio UI using Blocks for spinner control
with gr.Blocks(title="Job Fit Analyzer") as demo:
    gr.Markdown("# 🧠 Job Fit Analyzer")
    gr.Markdown("Upload your resume or paste it, and provide a LinkedIn Job ID to see how well you match.")

    job_id = gr.Textbox(label="🔗 LinkedIn Job ID")
    cv_file = gr.File(label="📎 Upload CV (PDF)", file_types=[".pdf"])
    cv_text = gr.Textbox(label="📄 Or Paste Your CV", lines=10, placeholder="Paste your resume here...")

    with gr.Row():
        submit_btn = gr.Button("Analyze Fit", variant="primary")
        loading = gr.Markdown("⏳ Analyzing...", visible=False)

    output = gr.Markdown()

    async def wrapped(job_id_val, file_val, text_val):
        yield gr.update(visible=True), gr.update(value="⏳ Analyzing...")
        result = await analyze_job_fit(job_id_val, file_val, text_val)
        yield gr.update(visible=False), result
        

    submit_btn.click(
        fn=wrapped,
        inputs=[job_id, cv_file, cv_text],
        outputs=[loading, output],
        show_progress=True
    )

demo.launch()
