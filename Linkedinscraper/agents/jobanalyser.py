from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import os

load_dotenv()
model = OpenAIModel("gpt-4o-mini")

class JobAnalyser(BaseModel):
    score: int = Field(description="The confidence score (0-100) for the job posting")
    summary: str = Field(description="A summary of the job posting")
    required_skills: List[str] = Field(description="List of required skills for the job")
    matched_skills: List[str] = Field(description="Skills from the required list that are present in the user's CV")
    missing_skills: List[str] = Field(description="Skills from the required list that are missing in the user's CV")
    cv_recommendations: List[str] = Field(description="Specific suggestions to improve the CV for this job")

system_prompt = """
You are an AI career assistant.

Your task is to analyze how well a user's CV matches a specific job description. Use a structured and consistent format.

---

## Job Description
{job_title}
{company_name}
{location}

{job_description_text}

---

## User CV
{cv_text}

---

## Instructions:
Based on the above, return a JSON object with the following **exact keys** and structure:

{
  "summary": "<A 2-3 line summary of the job in plain English>",
  "score": <Integer from 0 to 100 representing how well the user's CV matches this job>,
  "required_skills": ["Skill A", "Skill B", ...],
  "matched_skills": ["Skill X", "Skill Y", ...],
  "missing_skills": ["Skill Z", ...],
  "cv_recommendations": [
    "<Suggestion 1: Add more detail on your experience with Skill Z>",
    "<Suggestion 2: Mention familiarity with remote collaboration tools>",
    "<Suggestion 3: Improve formatting to highlight leadership roles>"
  ]
}

❗ Do not add any extra commentary. Only return the structured JSON object. Ensure keys are always present and correctly named.
"""

job_analyser_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=List[JobAnalyser],
)
