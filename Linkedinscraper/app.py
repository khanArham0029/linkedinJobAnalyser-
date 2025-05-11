# app.py


import gradio as gr
from agents.jobextractor import get_job_details_by_id
from agents.profileanalyser import profile_analyser_agent
from agents.jobanalyser import job_analyser_agent
import asyncio
import fitz
import json
import os
from typing import List



# Load profile if it exists
def load_profile():
    try:
        with open("data/user_profile.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Load at startup
preloaded_profile = load_profile()




# --- Helper: Extract text from PDF ---
def extract_text_from_pdf(pdf_file) -> str:
    doc = fitz.open(pdf_file.name)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# --- Save user profile to local file ---
def save_profile(name_val, uni, deg, crs, exp_list, skl, proj_list):
    profile = {
        "name": name_val,
        "university": uni,
        "degree": deg,
        "courses": crs,
        "experience": exp_list,
        "skills": skl,
        "projects": proj_list
    }
    os.makedirs("data", exist_ok=True)
    with open("data/user_profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    return gr.update(visible=True), "✅ Profile saved to data/user_profile.json!"

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

# --- Gradio UI ---
with gr.Blocks(title="Job Fit Analyzer") as demo:
    gr.Markdown("# 💼 AI Job Fit Analyzer")
    gr.Markdown("Evaluate your resume against any LinkedIn job posting.")

    with gr.Tabs():
        with gr.Tab("👤 User Profile"):
            name = gr.Textbox(label="Full Name", value=preloaded_profile.get("name", ""))
            university = gr.Textbox(label="University", value=preloaded_profile.get("university", ""))
            degree = gr.Textbox(label="Degree", value=preloaded_profile.get("degree", ""))
            courses = gr.Textbox(label="Relevant Courses", value=preloaded_profile.get("courses", ""), placeholder="Comma-separated...")
            skills = gr.Textbox(label="Skills", value=preloaded_profile.get("skills", ""), placeholder="Comma-separated...")
            experience_list = gr.State(preloaded_profile.get("experience", []))
            project_list = gr.State(preloaded_profile.get("projects", []))

            gr.Markdown("### Experience")
            experience_input = gr.Textbox(label="Add Experience", placeholder="E.g., Software Intern at XYZ")
            add_exp_btn = gr.Button("➕ Add Experience")
            experience_display = gr.Textbox(
                label="All Experiences",
                interactive=False,
                lines=4,
                value=", ".join(preloaded_profile.get("experience", []))
            )

            gr.Markdown("### Projects")
            project_input = gr.Textbox(label="Add Project", placeholder="E.g., Built AI-powered chatbot")
            add_proj_btn = gr.Button("➕ Add Project")
            project_display = gr.Textbox(
                label="All Projects",
                interactive=False,
                lines=4,
                value=", ".join(preloaded_profile.get("projects", []))
            )

            save_profile_btn = gr.Button("💾 Save Profile")
            save_status = gr.Markdown(visible=False)

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

        with gr.Tab("🧠 Profile Analyzer"):
            job_id_input_profile = gr.Textbox(label="LinkedIn Job ID")
            profile_analyze_btn = gr.Button("Analyze Profile Fit")
            profile_loading = gr.Markdown("⏳ Analyzing...", visible=False)
            profile_analysis_output = gr.Markdown()


    # Save profile button logic
    save_profile_btn.click(
        fn=save_profile,
        inputs=[name, university, degree, courses, experience_list, skills, project_list],
        outputs=[save_status, save_status]
    )

    def add_experience(new_exp, current_list: List[str]):
        if new_exp:
            updated = current_list + [new_exp]
            return ", ".join(updated), updated
        return ", ".join(current_list), current_list

    def add_project(new_proj, current_list: List[str]):
        if new_proj:
            updated = current_list + [new_proj]
            return ", ".join(updated), updated
        return ", ".join(current_list), current_list


    add_exp_btn.click(
        fn=add_experience,
        inputs=[experience_input, experience_list],
        outputs=[experience_display, experience_list]
    )

    add_proj_btn.click(
        fn=add_project,
        inputs=[project_input, project_list],
        outputs=[project_display, project_list]
    )

    

    # Spinner logic
    async def wrapped(job_id_val, file_val, text_val):
        yield gr.update(visible=True), gr.update(value="⏳ Analyzing...")
        result, hide_spinner = await analyze_job_fit(job_id_val, file_val, text_val)
        yield hide_spinner, result

    analyze_btn.click(
        fn=wrapped,
        inputs=[job_id_input, uploaded_cv_file, pasted_cv_text],
        outputs=[loading, analysis_output]
    )
    #Profile Analyzer Logic
    async def analyze_profile_fit(job_id: str):
    # Load saved user profile
        try:
            with open("data/user_profile.json", "r", encoding="utf-8") as f:
                profile = json.load(f)
        except FileNotFoundError:
            return "❌ No saved user profile found. Please complete and save your profile.", gr.update(visible=False)

        # Fetch job
        jobs = get_job_details_by_id([job_id])
        if not jobs:
            return "❌ Could not fetch job details. Check the Job ID.", gr.update(visible=False)

        job = jobs[0]
        job_info = job["job_info"]
        company_info = job["company_info"]

        job_text = f"""
            Job Title: {job_info['title']}
            Company: {company_info['name']}
            Location: {job_info.get('location', 'N/A')}
            Description: {job_info['description']}
        """

        profile_text = f"""
            Name: {profile['name']}
            University: {profile['university']}
            Degree: {profile['degree']}
            Courses: {profile['courses']}
            Experience: {', '.join(profile['experience']) if isinstance(profile['experience'], list) else profile['experience']}
            Skills: {profile['skills']}
            Projects: {', '.join(profile['projects']) if isinstance(profile['projects'], list) else profile['projects']}
        """

        llm_input = f"""
            Compare the following user profile with the job description.

            === Job Description ===
            {job_text}

            === User Profile ===
            {profile_text}

            Return a JSON with:
            - score (0–100): match score
            - summary: short summary of the job
            - matched_elements: list of aligned skills, experience, or projects
            - missing_elements: important things the user lacks
            - improvement_recommendations: tips to improve the profile for this job
        """

        result = await profile_analyser_agent.run(llm_input)
        output = result.output[0]

        formatted = (
            f"### 📝 Job Summary\n{output.summary}\n\n"
            f"### 🔍 Profile Match Score: **{output.score}** / 100\n\n"
            f"### ✅ Matched Elements:\n- " + "\n- ".join(output.matched_elements) + "\n\n"
            f"### ❌ Missing Elements:\n- " + "\n- ".join(output.missing_elements) + "\n\n"
            f"### 💡 Recommendations:\n- " + "\n- ".join(output.improvement_recommendations)
        )

        return formatted, gr.update(visible=False)

    async def profile_wrapped(job_id):
        yield gr.update(visible=True), gr.update(value="⏳ Analyzing...")
        result, hide_spinner = await analyze_profile_fit(job_id)
        yield hide_spinner, result

    profile_analyze_btn.click(
        fn=profile_wrapped,
        inputs=[job_id_input_profile],
        outputs=[profile_loading, profile_analysis_output]
    )



demo.launch()
