# File: agents/jobextractor.py

from apify_client import ApifyClient
from dotenv import load_dotenv
from typing import List, Dict, Any
import os

load_dotenv()
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

def get_job_details_by_id(job_ids: List[str]) -> List[Dict[str, any]]:
    client = ApifyClient(APIFY_API_TOKEN)

    run_input = {
        "job_id": job_ids
    }

    try:
        run = client.actor("apimaestro/linkedin-job-detail").call(run_input=run_input)
        jobs = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        return jobs
    except Exception as e:
        print(f" ****** Error fetching job details: {e}")
        return []