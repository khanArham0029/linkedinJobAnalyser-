# app.py


import gradio as gr
from agents.jobextractor import get_job_details_by_id
from agents.profileanalyser import profile_analyser_agent
from agents.jobanalyser import job_analyser_agent
from Ui.cv_analyzer_tab import cv_analyzer_tab
from Ui.profile_tab import profile_ui
from Ui.profile_analyzer_tab import profile_analyzer_ui
from Ui.cv_maker_tab import cv_maker_tab
import asyncio
import fitz
import json
import os
from typing import List


shared_cv_text = gr.State()
shared_job_id = gr.State()
shared_job_info = gr.State()
shared_cv_suggestions = gr.State()



# --- Gradio UI ---
with gr.Blocks(title="Job Fit Analyzer") as demo:
    gr.Markdown("# 💼 AI Job Fit Analyzer")
    gr.Markdown("Evaluate your resume against any LinkedIn job posting.")

    with gr.Tabs():
        with gr.Tab("👤 User Profile"):
            profile_ui()

        with gr.Tab(" Profile Analyzer"):
            profile_analyzer_ui()
        
        with gr.Tab(" CV Analyzer"):
            cv_analyzer_tab(shared_cv_text, shared_job_id, shared_job_info, shared_cv_suggestions)

        with gr.Tab("🧾 Generate personalized  CV"):
            cv_maker_tab(shared_cv_text, shared_job_id, shared_job_info, shared_cv_suggestions)

        with gr.Tab(" History / Export"):
            gr.Markdown("📝 This section will let you save & compare results (coming soon).")

demo.launch()
