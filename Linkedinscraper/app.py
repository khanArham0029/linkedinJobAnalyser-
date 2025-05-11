# app.py

import gradio as gr
from agents.jobextractor import get_job_details_by_id
from agents.jobanalyser import job_analyser_agent
import asyncio
import fitz

# --- Helper: Extract text from PDF ---
def extract_text_from_pdf(pdf_file) -> str:
    doc = fitz.open(pdf_file.name)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# --- Main Analysis Logic ---
async def analyze_job_fit(job_id: str, cv_file, cv_text: str):
    if cv_file is not None:
        cv = extract_text_from_pdf(cv_file)
    elif cv_text.strip():
        cv = cv_text.strip()
    else:
        return "❌ Please upload a PDF or paste your CV.", gr.update(visible=False)

    jobs = get_job_details_by_id([job_id])
    if not jobs:
        return "❌ Could not fetch job details. Please check the Job ID.", gr.update(visible=False)

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
You are a job application coach. Analyze how well the following CV matches the provided job posting.

=== Job Posting ===
{job_text}

=== User CV ===
{cv}

Return your answer as a JSON object with the following keys:
- summary: a short 2–3 line summary of the job
- score: integer from 0–100 (confidence match between CV and job)
- required_skills: list of explicit skills mentioned in the job
- matched_skills: list of skills from required_skills that appear in the CV
- missing_skills: list of required_skills that are NOT present in the CV
- cv_recommendations: list of specific suggestions to improve the CV for this job
    """

    result = await job_analyser_agent.run(llm_input)
    output = result.output[0]

    formatted = (
        f"### 📝 Job Summary\n{output.summary}\n\n"
        f"### 🔍 Confidence Score: **{output.score}** / 100\n\n"
        f"### 🛠️ Required Skills:\n- " + "\n- ".join(output.required_skills) + "\n\n"
        f"### ✅ Matched Skills:\n- " + "\n- ".join(output.matched_skills) + "\n\n"
        f"### ❌ Missing Skills:\n- " + "\n- ".join(output.missing_skills) + "\n\n"
        f"### 🧠 CV Recommendations:\n- " + "\n- ".join(output.cv_recommendations)
    )

    return formatted, gr.update(visible=False)

# --- Gradio App ---
with gr.Blocks(title="Job Fit Analyzer") as demo:
    gr.Markdown("# 💼 AI Job Fit Analyzer")
    gr.Markdown("Evaluate your resume against any LinkedIn job posting.")

    with gr.Tabs():
        with gr.Tab("📄 Upload CV"):
            uploaded_cv_file = gr.File(label="Upload CV (PDF)", file_types=[".pdf"])
            pasted_cv_text = gr.Textbox(label="Or Paste Your CV", lines=10, placeholder="E.g. experience, projects...")

        with gr.Tab("🔍 Analyze Job"):
            job_id_input = gr.Textbox(label="LinkedIn Job ID", placeholder="e.g. 4224754737")
            analyze_btn = gr.Button("Analyze Fit", variant="primary")

            loading = gr.Markdown("⏳ Analyzing...", visible=False)
            analysis_output = gr.Markdown()

        with gr.Tab("📁 History / Export"):
            gr.Markdown("📝 This section will let you save & compare results (coming soon).")

    # Event logic with progress spinner
    async def wrapped(job_id_val, file_val, text_val):
        yield gr.update(visible=True), gr.update(value="⏳ Analyzing...")
        result, hide_spinner = await analyze_job_fit(job_id_val, file_val, text_val)
        yield hide_spinner, result

    analyze_btn.click(
        fn=wrapped,
        inputs=[job_id_input, uploaded_cv_file, pasted_cv_text],
        outputs=[loading, analysis_output]
    )

demo.launch()
