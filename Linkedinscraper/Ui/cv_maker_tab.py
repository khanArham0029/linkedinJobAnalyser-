# File: ui/cv_maker_tab.py

import gradio as gr
import json
from langgraph.cv_graph import build_cv_graph, CVState

async def run_cv_generation(shared_cv_text, shared_job_id, shared_job_info, shared_cv_suggestions):
    # Load user profile
    try:
        with open("data/user_profile.json", "r", encoding="utf-8") as f:
            profile = json.load(f)
    except FileNotFoundError:
        return " No saved user profile found. Please complete and save your profile."

    job = shared_job_info.value
    job_id = shared_job_id.value
    cv_text = shared_cv_text.value
    suggestions = shared_cv_suggestions.value

    if not all([job, job_id, cv_text, suggestions]):
        return " Missing context. Please analyze your CV first."

    # Prepare and run the LangGraph flow
    initial_state = CVState(
        job_id=job_id,
        profile=profile,
        job=job,
        cv_text=cv_text,
        original_cv=cv_text,
        cv_suggestions=suggestions,
        final_cv=None
    )

    workflow = build_cv_graph()
    result = await workflow.ainvoke(initial_state)
    return result["final_cv"]

def cv_maker_tab(shared_cv_text, shared_job_id, shared_job_info, shared_cv_suggestions):
    with gr.Tab("🧾 Generate Final CV"):
        gr.Markdown("This tab uses your latest CV analysis to generate a tailored resume.")
        
        generate_btn = gr.Button("Generate Tailored CV", variant="primary")
        output = gr.Textbox(label="Generated CV", lines=25)

        # Async wrapper for Gradio
        async def generate_click_handler():
            return await run_cv_generation(
                shared_cv_text,
                shared_job_id,
                shared_job_info,
                shared_cv_suggestions
            )

        #  Hook up click event
        generate_btn.click(
            fn=generate_click_handler,
            inputs=[],
            outputs=[output]
        )
