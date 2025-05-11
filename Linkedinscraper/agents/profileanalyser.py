from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import os

load_dotenv()

model = OpenAIModel("gpt-4o-mini")

class ProfileAnalyser(BaseModel):
    score: int = Field(description="Match score (0–100) between the user profile and job")
    summary: str = Field(description="2–3 line summary of the job")
    matched_elements: List[str] = Field(description="Elements in the user profile that align with the job requirements")
    missing_elements: List[str] = Field(description="Elements missing from user profile that are important for the job")
    improvement_recommendations: List[str] = Field(description="Suggestions to improve user's profile for this role")

system_prompt = """
You are an assistant that evaluates how well a user's structured profile matches a job posting.

Compare the user's profile with the job description and return:
- score (0–100): overall match score
- summary: short 2–3 line summary of the job
- matched_elements: list of profile components that align with the job
- missing_elements: what the user is lacking (skills, tools, experience, etc.)
- improvement_recommendations: actionable tips to enhance profile alignment

Respond with a JSON object matching the defined format.
"""

profile_analyser_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=List[ProfileAnalyser],
)