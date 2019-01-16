import os
import unittest
from devo.api import Client


class TestApi(unittest.TestCase):
    def setUp(self):
        self.uri = os.getenv('DEVO_API_URL',
                             'https://api-us.logtrust.com/')
        self.client = Client.from_config(
            {'key': os.getenv('DEVO_API_KEY', None),
             'secret': os.getenv('DEVO_API_SECRET', None),
             'url': os.getenv('DEVO_API_URL', 'https://api-us.logtrust.com/'),
             })

    def test_jobs_cycle(self):
        self.client.query(query="from demo.ecommerce.data select *",
                          dates={'from': '2018-01-01 00:00:00'}, stream=False,
                          destination={"type": "donothing",
                                       "params": {
                                           "friendlyName": "devo-sdk-api-test"}})

        # Get all jobs
        result = self.client.get_jobs()
        self.assertTrue(result['object'])

        # Get job by name
        result = self.client.get_jobs(name="devo-sdk-api-test")
        self.assertTrue(result['object'])

        # Get job by type
        result = self.client.get_jobs(type="donothing")
        self.assertTrue(result['object'])

        # Get job by name and type
        result = self.client.get_jobs(name="devo-sdk-api-test",
                                      type="donothing")
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
