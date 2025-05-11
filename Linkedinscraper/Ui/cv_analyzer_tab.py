# File: ui/cv_analyzer_tab.py

import gradio as gr
from agents.jobextractor import get_job_details_by_id
from agents.jobanalyser import job_analyser_agent
from Logic.job_cache import get_or_cache_job
import asyncio
import fitz

def extract_text_from_pdf(pdf_file) -> str:
    doc = fitz.open(pdf_file.name)
    return "\n".join(page.get_text() for page in doc)

async def analyze_job_fit(job_id: str, cv_file):
    if cv_file is not None:
        cv = extract_text_from_pdf(cv_file)
    else:
        return " Please upload a PDF or paste your CV.", gr.update(visible=False)

    job = get_or_cache_job(job_id)
    if not job:
        return " Could not fetch job details. Please check the Job ID.", gr.update(visible=False)
    job_info = job["job_info"]
    company_info = job["company_info"]

    job_text = f"""Job Title: {job_info['title']}
Company: {company_info['name']}
Location: {job_info.get('location', 'N/A')}
Description: {job_info['description']}"""

    llm_input = f"""
You are a job application coach. Analyze how well the following CV matches the provided job posting.

=== Job Posting ===
{job_text}

=== User CV ===
{cv}

Return your answer as a JSON object with:
- summary
- score (0–100)
- required_skills
- matched_skills
- missing_skills
- cv_recommendations
"""

    result = await job_analyser_agent.run(llm_input)
    output = result.output[0]

    formatted = (
        f"###  Job Summary\n{output.summary}\n\n"
        f"###  Confidence Score: **{output.score}** / 100\n\n"
        f"###  Required Skills:\n- " + "\n- ".join(output.required_skills) + "\n\n"
        f"###  Matched Skills:\n- " + "\n- ".join(output.matched_skills) + "\n\n"
        f"###  Missing Skills:\n- " + "\n- ".join(output.missing_skills) + "\n\n"
        f"###  CV Recommendations:\n- " + "\n- ".join(output.cv_recommendations)
    )

    return formatted, gr.update(visible=False)

def cv_analyzer_tab():
    uploaded_cv_file = gr.File(label="Upload CV (PDF)", file_types=[".pdf"])
    job_id_input = gr.Textbox(label="LinkedIn Job ID")
    analyze_btn = gr.Button("Analyze CV Fit", variant="primary")
    loading = gr.Markdown("⏳ Analyzing...", visible=False)
    analysis_output = gr.Markdown()

    async def run_analysis(job_id, file):
        result, _ = await analyze_job_fit(job_id, file)
        return result
    
    analyze_btn.click(
        fn=run_analysis,
        inputs=[job_id_input, uploaded_cv_file],
        outputs=[analysis_output]
        )


