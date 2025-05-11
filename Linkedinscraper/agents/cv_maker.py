# File: agents/cv_maker.py

from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import os

load_dotenv()
model = OpenAIModel("gpt-4o-mini")

class CVOutput(BaseModel):
    cv: str = Field(description="A fully tailored CV based on the job and profile")

system_prompt = """
You are a professional resume writer.

You will be given:
- A job description
- A user's structured profile
- A list of suggestions (missing/matched skills, CV recommendations)

Your task is to generate a clean, well-structured, job-specific CV in plain text format.

The CV should include:
- Name and contact (from profile)
- Education
- Technical Skills (from both profile and job match)
- Projects
- Experience

Highlight strengths that match the job.
Format clearly and professionally.
"""

cv_maker_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=CVOutput,
)
