import os

import pytest

from devo.api import Client
from devo.common.loadenv.load_env import load_env_file

# Load environment variables form test directory
load_env_file(os.path.abspath(os.getcwd()) + os.sep + "environment.env")


@pytest.fixture(scope="module")
def setup_client():
    yield Client(
        config={
            "key": os.getenv("DEVO_API_KEY", None),
            "secret": os.getenv("DEVO_API_SECRET", None),
            "address": os.getenv("DEVO_API_ADDRESS", "https://apiv2-us.devo.com/"),
            "stream": False,
            "destination": {
                "type": "donothing",
                "params": {"friendlyName": "devo-sdk-api-test"},
            },
        }
    )


@pytest.fixture(scope="module")
def setup_query():
    yield "from siem.logtrust.web.connection select action"


@pytest.mark.skip("temporarily disabled due to Query API bug")
def test_jobs_cycle(setup_client, setup_query):
    setup_client.query(query=setup_query, dates={"from": "1d"})

    # Get all jobs
    result = setup_client.get_jobs()
    assert result["object"] is True

    # Get job by name
    result = setup_client.get_jobs(name="devo-sdk-api-test")
    assert result["object"] is True

    # Get job by type
    result = setup_client.get_jobs(job_type="donothing")
    assert result["object"] is True

    # Get job by name and type
    result = setup_client.get_jobs(name="devo-sdk-api-test", job_type="donothing")
    assert result["object"] is True
    job_id = result["object"][0]["id"]

    # Stop job by id
    result = setup_client.stop_job(job_id)
    assert result["object"]["status"] == "STOPPED"

    # Start job by id
    result = setup_client.start_job(job_id)
    assert result["object"]["status"] == "RUNNING"

    # Delete job by id
    result = setup_client.remove_job(job_id)
    assert result["object"]["status"] == "REMOVED"


if __name__ == "__main__":
    pytest.main()
