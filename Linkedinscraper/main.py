from typing import TypedDict, List, Dict, Any, Optional
from agents.jobextractor import get_job_details_by_id  # renamed from jobextractor
from agents.jobanalyser import job_analyser_agent
from langgraph.graph import StateGraph, START, END
import asyncio

class AgentState(TypedDict):
    job_ids: List[str]
    user_cv: str
    job_details: Optional[List[Dict[str, Any]]]
    job_analysis: Optional[List[Dict[str, Any]]]
    status: str
    error: Optional[str]

# --- Node 1: Fetch job details by job ID ---
async def fetch_by_job_id(state: AgentState) -> AgentState:
    jobs = get_job_details_by_id(state["job_ids"])
    return {**state, "job_details": jobs, "status": "job_details_fetched"}

# --- Node 2: Analyze each job against CV ---
async def analyze(state: AgentState) -> AgentState:
    job_analysis = []

    for job in state["job_details"]:
        job_text = f"""
        Job Title: {job['job_info']['title']}
        Company: {job['company_info']['name']}
        Location: {job['job_info'].get('location', 'N/A')}
        Description: {job['job_info']['description']}
        """

        full_input = f"""
Compare the following job with the user's CV.

=== Job Posting ===
{job_text}

=== User CV ===
{state['user_cv']}

Return a JSON with:
- summary (summary of the job)
- score (0–100 confidence score on match)
- required_skills (from the job)
- cv_recommendations (what the user should change/add to their CV)
        """

        result = await job_analyser_agent.run(full_input)

        job_analysis.append({
            "job_id": job['job_info']['job_url'].split('/')[-2],
            "title": job['job_info']['title'],
            "company": job['company_info']['name'],
            "score": result.output[0].score,
            "summary": result.output[0].summary,
            "required_skills": result.output[0].required_skills,
            "cv_recommendations": result.output[0].cv_recommendations,
            "link": job['job_info']['job_url']
        })

    return {**state, "job_analysis": job_analysis, "status": "analysis_done"}

# --- LangGraph setup ---
builder = StateGraph(AgentState)
builder.add_node("Fetch Job Details", fetch_by_job_id)
builder.add_node("Analyze Job Fit", analyze)
builder.add_edge(START, "Fetch Job Details")
builder.add_edge("Fetch Job Details", "Analyze Job Fit")
builder.add_edge("Analyze Job Fit", END)
workflow = builder.compile()

# --- Initial input (update this with user-provided job IDs and CV) ---
initial_state = AgentState(
    job_ids=["4224754737"],  #  job ID
    user_cv="""- 2 years experience with Python and PyTorch
- Worked on multiple AI side-projects
- Familiar with Blender, Unity, and 3D avatar models
- Experience with Google Colab and HuggingFace for hosted model training""",
    job_details=None,
    job_analysis=None,
    status="start",
    error=None
)

async def main():
    result = await workflow.ainvoke(initial_state)
    print("\n📊 Final Analysis Results:\n")
    for job in result["job_analysis"]:
        print(f"{job['title']} at {job['company']} — Score: {job['score']}")
        print(f"Summary: {job['summary']}")
        print(f"Skills: {', '.join(job['required_skills'])}")
        print(f"CV Suggestions: {job['cv_recommendations']}")
        print(f"Link: {job['link']}\n")

if __name__ == "__main__":
    asyncio.run(main())
