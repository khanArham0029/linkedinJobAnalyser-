# File: ui/profile_tab.py

import gradio as gr
import os, json
from typing import List

def load_profile():
    try:
        with open("data/user_profile.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

preloaded = load_profile()

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
    return gr.update(visible=True), " Profile saved to data/user_profile.json!"

def add_item(new_item, current_list: List[str]):
    if new_item:
        updated = current_list + [new_item]
        return ", ".join(updated), updated
    return ", ".join(current_list), current_list

def profile_ui():
    name = gr.Textbox(label="Full Name", value=preloaded.get("name", ""))
    university = gr.Textbox(label="University", value=preloaded.get("university", ""))
    degree = gr.Textbox(label="Degree", value=preloaded.get("degree", ""))
    courses = gr.Textbox(label="Courses", value=preloaded.get("courses", ""))
    skills = gr.Textbox(label="Skills", value=preloaded.get("skills", ""))

    experience_input = gr.Textbox(label="Add Experience")
    add_exp_btn = gr.Button("➕ Add Experience")
    experience_list = gr.State(preloaded.get("experience", []))
    experience_display = gr.Textbox(
        label="All Experiences",
        interactive=False,
        lines=4,
        value=", ".join(preloaded.get("experience", [])) 
        )

    project_input = gr.Textbox(label="Add Project")
    add_proj_btn = gr.Button("➕ Add Project")
    project_list = gr.State(preloaded.get("projects", []))
    project_display = gr.Textbox(
        label="All Projects",
        interactive=False,
        lines=4,
        value=", ".join(preloaded.get("projects", [])) 
        )

    save_profile_btn = gr.Button("💾 Save Profile")
    save_status = gr.Markdown(visible=False)

    add_exp_btn.click(fn=add_item, inputs=[experience_input, experience_list], outputs=[experience_display, experience_list])
    add_proj_btn.click(fn=add_item, inputs=[project_input, project_list], outputs=[project_display, project_list])
    save_profile_btn.click(
        fn=save_profile,
        inputs=[name, university, degree, courses, experience_list, skills, project_list],
        outputs=[save_status, save_status]
        )
