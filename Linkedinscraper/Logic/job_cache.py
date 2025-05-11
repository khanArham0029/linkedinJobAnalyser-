import os
import json
from agents.jobextractor import get_job_details_by_id

def get_or_cache_job(job_id: str, cache_dir="data") -> dict | None:
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, f"job_{job_id}.json")

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fetch from API
    job_data = get_job_details_by_id([job_id])
    if not job_data:
        return None

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(job_data[0], f, indent=2)

    return job_data[0]
