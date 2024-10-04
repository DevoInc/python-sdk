import json
import os
import uuid
import pytest

from devo.api import Client
from devo.common.loadenv.load_env import load_env_file

# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


@pytest.fixture(scope="module")
def setup_client(job_name):
    yield Client(
        config={
            "key": os.getenv("DEVO_API_KEY", None),
            "secret": os.getenv("DEVO_API_SECRET", None),
            "address": os.getenv("DEVO_API_ADDRESS", "https://apiv2-us.devo.com/"),
            "stream": False,
            "destination": {
                "type": "donothing",
                "params": {"friendlyName": job_name},
            },
        }
    )


@pytest.fixture(scope="module")
def setup_query():
    yield "from siem.logtrust.web.connection select action"


@pytest.fixture(scope="module")
def job_name():
    return "devo-sdk-api-test" + str(uuid.uuid1().int)


def test_jobs_cycle(setup_client, setup_query, job_name):
    result = setup_client.query(query=setup_query, dates={"from": "1d", "to": "endday"})
    result = json.loads(result)
    assert result["status"] == 0
    assert "object" in result
    assert "id" in result["object"]
    job_id = result["object"]["id"]

    # Get all jobs
    result = setup_client.get_jobs()
    assert len(result["object"]) >  0

    # Get job by job id
    result = setup_client.get_job(job_id=job_id)
    assert result["object"]["friendlyName"] == job_name
    assert result["object"]["id"] == job_id

    # Stop job by id
    result = setup_client.stop_job(job_id)
    assert result["object"]["status"] in ["STOPPED", "COMPLETED"]

    # Start job by id
    result = setup_client.start_job(job_id)
    assert result["object"]["status"] in ["RUNNING", "COMPLETED"]

    # Delete all jobs created by this and past test execution (cleaning purposes)
    result = setup_client.get_jobs()
    jobs_ids = [job["id"] for job in result["object"] if job["friendlyName"].startswith("devo-sdk-api-test")]
    for job_id in jobs_ids:
        result = setup_client.remove_job(job_id)
        assert result["object"]["status"] == "REMOVED"


if __name__ == "__main__":
    pytest.main()
