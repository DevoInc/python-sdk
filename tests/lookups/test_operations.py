import json
import os
import unittest
from http import HTTPStatus
from urllib.parse import quote as url_encode
import responses

from devo.lookups.api import Lookups
from devo.lookups.request import LookupRequest, Id, Recipe, Contribution, ContributionType, KeyType, Key


class TestLookupsAPIOperations(unittest.TestCase):
    def setUp(self) -> None:
        self.domain = os.getenv('DEVO_LOOKUPS_DOMAIN')
        self.lookup_name = "test3"
        self.lookup_api_url = os.getenv('DEVO_LOOKUPS_API')
        self.token = os.getenv('DEVO_LOOKUPS_TOKEN')

        self.api = Lookups(self.lookup_api_url, auth={'token': self.token})

    @responses.activate
    def test_create_lookup_operation(self):
        result = {'type': 'LookupCreationResponse', 'cid': '8a98a0fafc6b', 'code': 201, 'context': None,
                  'id': '12665d2a-cd8b-11ed-a182-151e24bba073',
                  'msg': 'Lookup sent to creation. You can check the lookup status using the provided id: /lookup/{domain}/{name}/job/{id}',
                  'lookupDeployConfig': {'id': {'creator': 'devo_services', 'name': 'test4'},
                                         'visibility': 'creator-only', 'recipe': {'recipeType': 'once',
                                                                                  'source': {'columns': [],
                                                                                             'skipPreface': None,
                                                                                             'hasHeader': None,
                                                                                             'skipEmptyLines': None,
                                                                                             'fileProvider': None,
                                                                                             'query': 'from siem.logtrust.web.activity where eq(client, "devo_services") where (lt(sub(now(), 1d), eventdate) and lt(eventdate, now())) group by username select username select (count() as event_count) select (\'add\' as type)'},
                                                                                  'lookupType': {'type': 'normal',
                                                                                                 'instantPolicy': None,
                                                                                                 'instant': None,
                                                                                                 'columnName': None},
                                                                                  'append': False,
                                                                                  'key': {'columns': [],
                                                                                          'column': 'username',
                                                                                          'type': 'column'},
                                                                                  'columnFilter': ['username',
                                                                                                   'event_count',
                                                                                                   'type'],
                                                                                  'contribution': {'type': 'col',
                                                                                                   'name': 'type'},
                                                                                  'secondaryIndexes': None,
                                                                                  'refreshMillis': None,
                                                                                  'startMillis': None,
                                                                                  'requiresDate': False},
                                         'notifyStatus': False}}
        responses.add(responses.POST, f"{self.lookup_api_url}/lookup/{url_encode(self.domain)}"
                                      f"/{url_encode(self.lookup_name)}/deploy-config", body=json.dumps(result),
                      status=HTTPStatus.CREATED)
        request: LookupRequest = LookupRequest(
            id=Id(self.domain, self.lookup_name),
            recipe=Recipe("from siem.logtrust.web.activity where now()-1d < eventdate < now() group by username "
                          "select username, count() as event_count, 'add' as type",
                          column_filter=['username', 'event_count', 'type'],
                          contribution=Contribution(name="type", type=ContributionType.COL),
                          key=Key(column='username', type=KeyType.COLUMN)),
        )
        response = self.api.create_lookup(request)

