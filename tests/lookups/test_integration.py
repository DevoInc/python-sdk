import os
import re
import time
import unittest
import timeout_decorator

from devo.lookups.api import Lookups
from devo.lookups.request import LookupRequest, Id, Recipe, Contribution, ContributionType, KeyType, Key


class TestLookupsAPIIntegration(unittest.TestCase):
    def setUp(self) -> None:
        if os.getenv('RUN_INTEGRATION_TEST', 'False').upper() != 'TRUE':
            self.skipTest('Skipped as integration test is not enabled')

        self.domain = os.getenv('DEVO_LOOKUPS_DOMAIN')
        self.lookup_api_url = os.getenv('DEVO_LOOKUPS_API')
        self.token = os.getenv('DEVO_LOOKUPS_TOKEN')

        self.api = Lookups(self.lookup_api_url, auth={'token': self.token})

    @timeout_decorator.timeout(2400)
    def test_integration(self):
        try:
            # Lis
            response = self.api.get_lookups(self.domain)
            i = 0
            for lookup in response['lookups']:
                match = re.fullmatch('test(\d+)', lookup['name'])
                if match is not None:
                    i = max(int(match[1])+1, i)
            lookup_name = 'test%d' % i
            response = self.api.create_lookup(LookupRequest(
                id=Id(self.domain, lookup_name),
                recipe=Recipe("from siem.logtrust.web.activity where now()-1d < eventdate < now() group by username "
                              "select username, count() as event_count, 'creation' as when, 'add' as type",
                              column_filter=['username', 'event_count', 'when', 'type'],
                              contribution=Contribution(name="type", type=ContributionType.COL),
                              key=Key(column='username', type=KeyType.COLUMN)),
            ))
            self.assertIsNotNone(response['lookupDeployConfig'])
            job_id = response['id']
            while True:
                response = self.api.get_lookup_job(self.domain, lookup_name, job_id)
                if response['jobs']:
                    break
                time.sleep(10)
            response = self.api.describe_lookup(self.domain, lookup_name)
            response = self.api.update_lookup(LookupRequest(
                id=Id(self.domain, lookup_name),
                recipe=Recipe(
                    "from siem.logtrust.web.activity where now()-1d < eventdate < now() group by username "
                    "select username, count() as event_count, 'update' as when, 'add' as type",
                    column_filter=['username', 'event_count', 'when', 'type'],
                    contribution=Contribution(name="type", type=ContributionType.COL),
                    key=Key(column='username', type=KeyType.COLUMN)),
            ))
            job_id = response['id']
            while True:
                response = self.api.get_lookup_job(self.domain, lookup_name, job_id)
                if response['jobs']:
                    break
                time.sleep(10)
            response = self.api.describe_lookup(self.domain, lookup_name)
        finally:
            response = self.api.delete_lookup(self.domain, lookup_name)
