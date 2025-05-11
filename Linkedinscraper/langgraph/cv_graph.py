from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from Logic.job_cache import get_or_cache_job
from agents.jobanalyser import job_analyser_agent
from agents.cv_maker import cv_maker_agent

# Step 1: Define the flow state
class CVState(TypedDict):
    job_id: str
    profile: Dict[str, Any]
    job: Optional[Dict[str, Any]]
    cv_text: Optional[str]
    cv_suggestions: Optional[Dict[str, Any]]
    final_cv: Optional[str]

# Step 2: Define node functions

async def load_job_node(state: CVState) -> CVState:
    job = get_or_cache_job(state["job_id"])
    return {**state, "job": job}

async def analyze_cv_node(state: CVState) -> CVState:
    job = state["job"]
    cv_text = state["cv_text"]

    job_text = f"""
Job Title: {job['job_info']['title']}
Company: {job['company_info']['name']}
Description: {job['job_info']['description']}
"""

    prompt = f"""
Compare this job with the following user CV.

=== Job Description ===
{job_text}

=== User CV ===
{cv_text}

Return structured suggestions:
- summary
- score
- required_skills
- matched_skills
- missing_skills
- cv_recommendations
"""

    result = await job_analyser_agent.run(prompt)
    suggestions = {
        "summary": result.output[0].summary,
        "score": result.output[0].score,
        "required_skills": result.output[0].required_skills,
        "matched_skills": result.output[0].matched_skills,
        "missing_skills": result.output[0].missing_skills,
        "cv_recommendations": result.output[0].cv_recommendations,
    }

    return {**state, "cv_suggestions": suggestions}

async def generate_cv_node(state: CVState) -> CVState:
    profile = state["profile"]
    job = state["job"]
    suggestions = state["cv_suggestions"]

    job_text = job["job_info"]["description"]

    prompt = f"""
Job Description:
{job_text}

User Profile:
{profile}

CV Suggestions:
{suggestions}

Now create a clean, job-specific, tailored CV using this information.
"""

    result = await cv_maker_agent.run(prompt)
    return {**state, "final_cv": result.output.cv}

# Step 3: Build the graph
def build_cv_graph():
    graph = StateGraph(CVState)
    graph.add_node("LoadJob", load_job_node)
    graph.add_node("AnalyzeCV", analyze_cv_node)
    graph.add_node("GenerateCV", generate_cv_node)

    graph.set_entry_point("LoadJob")
    graph.add_edge("LoadJob", "AnalyzeCV")
    graph.add_edge("AnalyzeCV", "GenerateCV")
    graph.set_finish_point("GenerateCV")

    return graph.compile()
