from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import Any, List
from pydantic_ai.models.openai import OpenAIModel
from dotenv import load_dotenv
import httpx
import os
load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "linkedin-api8.p.rapidapi.com"

URL = "https://linkedin-api8.p.rapidapi.com/"

async def get_linkedin_data(username: str) -> dict[str, Any] | None:
    
    params = {
        "username": username,
    }
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                URL,
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            print(f"Error fetching LinkedIn data:")
            return None

class Tool(BaseModel):
    name: str = Field(description="The name of the person")
    experience: str = Field(description="The work experience of the person")


model = OpenAIModel("gpt-4o-mini")

system_prompt = f"""You are an assistant that helps find information about LinkedIn profiles. Use the linkedin_profile_scraper tool to fetch profile details for the given username."""

scrape_agent = Agent(
    model=model,
    system_prompt=system_prompt,
    result_type=List[Tool],
)

@scrape_agent.tool_plain
async def linkedin_profile_scraper(username: str) -> dict[str, Any] | None:
    """
    Fetch LinkedIn profile data for a given username.
    """
    return await get_linkedin_data(username)

result = scrape_agent.run_sync("please fetch details for the username 'atulpandey-iift'")
print(result.data)