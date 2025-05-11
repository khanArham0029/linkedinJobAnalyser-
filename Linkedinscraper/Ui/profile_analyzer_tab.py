# File: ui/profile_analyzer_tab.py

import gradio as gr
import json
import asyncio
from agents.jobextractor import get_job_details_by_id
from agents.profileanalyser import profile_analyser_agent
from Logic.job_cache import get_or_cache_job

async def analyze_profile_fit(job_id: str):
    try:
        with open("data/user_profile.json", "r", encoding="utf-8") as f:
            profile = json.load(f)
    except FileNotFoundError:
        return " No saved user profile found. Please complete and save your profile.", gr.update(visible=False)

    job = get_or_cache_job(job_id)
    if not job:
        return " Could not fetch job details. Check the Job ID.", gr.update(visible=False)
    job_info = job["job_info"]
    company_info = job["company_info"]

    job_text = f"""Job Title: {job_info['title']}
Company: {company_info['name']}
Location: {job_info.get('location', 'N/A')}
Description: {job_info['description']}"""

    profile_text = f"""Name: {profile['name']}
University: {profile['university']}
Degree: {profile['degree']}
Courses: {profile['courses']}
Experience: {', '.join(profile['experience']) if isinstance(profile['experience'], list) else profile['experience']}
Skills: {profile['skills']}
Projects: {', '.join(profile['projects']) if isinstance(profile['projects'], list) else profile['projects']}"""

    llm_input = f"""
Compare the following user profile with the job description.

=== Job Description ===
{job_text}

=== User Profile ===
{profile_text}

Return a JSON with:
- score (0–100)
- summary
- matched_elements
- missing_elements
- improvement_recommendations
"""

    result = await profile_analyser_agent.run(llm_input)
    output = result.output[0]

    formatted = (
        f"###  Job Summary\n{output.summary}\n\n"
        f"###  Profile Match Score: **{output.score}** / 100\n\n"
        f"###  Matched Elements:\n- " + "\n- ".join(output.matched_elements) + "\n\n"
        f"###  Missing Elements:\n- " + "\n- ".join(output.missing_elements) + "\n\n"
        f"###  Recommendations:\n- " + "\n- ".join(output.improvement_recommendations)
    )
    return formatted

def profile_analyzer_ui():
    with gr.Tab("🧠 Profile Analyzer"):
        job_id_input = gr.Textbox(label="LinkedIn Job ID")
        analyze_btn = gr.Button("Analyze Profile Fit",variant="primary")
        loading = gr.Markdown(" Analyzing...", visible=False)
        output = gr.Markdown()

        async def run_profile_analysis(job_id):
            return await analyze_profile_fit(job_id)

        analyze_btn.click(
            fn=run_profile_analysis,
            inputs=[job_id_input],
            outputs=[output]
        )
