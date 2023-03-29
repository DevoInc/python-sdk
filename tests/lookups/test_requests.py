import json
import unittest

from devo.lookups.request import LookupRequest, Id, Recipe, Contribution, ContributionType, Key, KeyType, Source, \
    RecipeType


class TestLookupsAPIRequests(unittest.TestCase):
    payload_once = \
        {
            "id": {
                "creator": "devo_services",
                "name": "test3"
            },
            "visibility": "creator-only",
            "recipe": {
                "recipeType": "once",
                "source": {
                    "query": "from siem.logtrust.web.activity where now()-1d < eventdate < now() group by username"
                             " select username, count() as event_count, 'add' as type"
                },
                "lookupType": {
                    "type": "normal"
                },
                "append": False,
                "key": {
                    "type": "column",
                    "column": "username"
                },
                "columnFilter": [
                    "username",
                    "event_count",
                    "type"
                ],
                "contribution": {
                    "type": "col",
                    "name": "type"
                },
                "requiresDate": False
            },
            "notifyStatus": False
        }

    payload_periodic = \
        {
            "id": {
                "creator": "devo_services",
                "name": "test3"
            },
            "visibility": "creator-only",
            "recipe": {
                "recipeType": "periodic",
                "source": {
                    "query": "from siem.logtrust.web.activity where now()-1h < eventdate < now() group by username"
                             " select username, count() as event_count, 'add' as type"
                },
                "lookupType": {
                    "type": "normal"
                },
                "append": False,
                "key": {
                    "type": "column",
                    "column": "username"
                },
                "columnFilter": [
                    "username",
                    "event_count",
                    "type"
                ],
                "contribution": {
                    "type": "col",
                    "name": "type"
                },
                "refreshMillis": 60 * 60 * 1000,
                "startMillis": 24 * 60 * 60 * 1000,
                "requiresDate": False
            },
            "notifyStatus": False
        }

    def test_request_json_1(self):
        request: LookupRequest = LookupRequest(
            id=Id("devo_services", "test3"),
            recipe=Recipe("from siem.logtrust.web.activity where now()-1d < eventdate < now() group by username "
                          "select username, count() as event_count, 'add' as type",
                          column_filter=['username', 'event_count', 'type'],
                          contribution=Contribution(name="type", type=ContributionType.COL),
                          key=Key(column='username', type=KeyType.COLUMN)),
        )
        self.assertEqual(json.loads(request.toJson()), TestLookupsAPIRequests.payload_once)

    def test_request_json_2(self):
        request: LookupRequest = LookupRequest(
            id=Id("devo_services", "test3"),
            recipe=Recipe(Source("from siem.logtrust.web.activity where now()-1h < eventdate < now() group by username"
                                 " select username, count() as event_count, 'add' as type"),
                          recipe_type=RecipeType.PERIODIC,
                          column_filter=['username', 'event_count', 'type'],
                          contribution=Contribution(name="type", type=ContributionType.COL),
                          key=Key(column='username', type=KeyType.COLUMN),
                          refresh_millis=60 * 60 * 1000,
                          start_millis=24 * 60 * 60 * 1000),
        )
        self.assertEqual(json.loads(request.toJson()), TestLookupsAPIRequests.payload_periodic)
