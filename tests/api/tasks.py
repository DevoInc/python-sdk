import os
import unittest
from devo.api import Client, ClientConfig


class TestApi(unittest.TestCase):
    def setUp(self):
        self.client = Client(
            config={'key': os.getenv('DEVO_API_KEY', None),
                    'secret': os.getenv('DEVO_API_SECRET', None),
                    'address': os.getenv('DEVO_API_ADDRESS',
                                         'https://apiv2-us.devo.com/'),
                    "stream": False,
                    "destination": {
                        "type": "donothing",
                        "params": {"friendlyName": "devo-sdk-api-test"}
                    }
                    })
        self.query = "from siem.logtrust.web.connection select action"

    @unittest.skip("temporarily disabled due to Query API bug")
    def test_jobs_cycle(self):
        self.client.query(
            query=self.query,
            dates={'from': '1d'})

        # Get all jobs
        result = self.client.get_jobs()
        self.assertTrue(result['object'])

        # Get job by name
        result = self.client.get_jobs(name="devo-sdk-api-test")
        self.assertTrue(result['object'])

        # Get job by type
        result = self.client.get_jobs(job_type="donothing")
        self.assertTrue(result['object'])

        # Get job by name and type
        result = self.client.get_jobs(name="devo-sdk-api-test",
                                      job_type="donothing")
        self.assertTrue(result['object'])
        job_id = result['object'][0]['id']

        # Stop job by id
        result = self.client.stop_job(job_id)
        self.assertEqual(result['object']['status'], "STOPPED")

        # Start job by id
        result = self.client.start_job(job_id)
        self.assertEqual(result['object']['status'], "RUNNING")

        # Delete job by id
        result = self.client.remove_job(job_id)
        self.assertEqual(result['object']['status'], "REMOVED")


if __name__ == '__main__':
    unittest.main()
