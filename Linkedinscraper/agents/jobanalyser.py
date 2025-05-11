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
    cv_recommendations: List[str] = Field(description="Specific suggestions to improve the CV for this job")

system_prompt = """
You are a career assistant that evaluates how well a user's resume (CV) matches a job posting.

Given a job description and a user CV:
1. Analyze the alignment between the job and the user's experience.
2. Return a JSON with:
    - score (0–100): match confidence
    - summary: a concise summary of the job role
    - required_skills: bullet-point list of job-specific skills
    - cv_recommendations: actionable suggestions for the user to improve their CV to better fit the job

Make sure `required_skills` and `cv_recommendations` are **never empty**. Even if the match is poor, recommend what the user can do to improve.
"""

job_analyser_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=List[JobAnalyser],
)
