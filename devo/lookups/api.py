import json
import os
import time
from pprint import pprint

import requests
from urllib.parse import quote as url_encode

from devo.api.exception import DevoClientException, DevoClientRequestException
from devo.common.auth.common import get_request_headers, AuthenticationMode
from devo.lookups.request import LookupRequest

NO_CREDENTIALS_IN_AUTH = "Token credentials not present in 'auth' parameter"

ERROR_INVOKING_REQUEST = "Error invoking request"

ERROR_JSON_RESPONSE_EXPECTED = "JSON response expected but received: %s"

ERROR_PROCESSING_REQUEST = "Error processing request: %s"


class Lookups:
    def __init__(self, base_url, auth: dict = None, verify: bool = True, timeout: int = 30):
        self.base_url = base_url
        self.verify = verify
        self.timeout = timeout
        if not auth or 'token' not in auth:
            raise DevoClientException(NO_CREDENTIALS_IN_AUTH)
        else:
            self.token = auth['token']

    def get_lookups(self, domain: str):
        return self.__request(f"{self.base_url}/lookup/{url_encode(domain)}", method='get')

    def describe_lookup(self, domain: str, lookup: str):
        return self.__request(f"{self.base_url}/lookup/{url_encode(domain)}/{url_encode(lookup)}", method='get')

    def delete_lookup(self, domain: str, lookup: str):
        return self.__request(f"{self.base_url}/lookup/{url_encode(domain)}/{url_encode(lookup)}", method='delete')

    def get_lookup_job(self, domain: str, lookup: str, id: str):
        return self.__request(f"{self.base_url}/lookup/{url_encode(domain)}/{url_encode(lookup)}/job/{url_encode(id)}",
                              method='get')

    def get_last_lookup_job(self, domain: str, lookup: str):
        return self.__request(f"{self.base_url}/lookup/{url_encode(domain)}/{url_encode(lookup)}/job",
                              method='get')


    def create_lookup(self, request: LookupRequest):
        domain = request.id.creator
        lookup = request.id.name
        payload = request.toJson()
        return self.__request(f"{self.base_url}/lookup/{url_encode(domain)}/{url_encode(lookup)}/deploy-config",
                              method='post', payload=payload)

    def update_lookup(self, domain: str, lookup: str, request):
        payload = json.dumps(request)
        return self.__request(f"{self.base_url}/lookup/{url_encode(domain)}/{url_encode(lookup)}/deploy-config",
                              method='put', payload=payload)

    def __request(self, url, method: str = 'get', payload=None):
        try:
            response = getattr(requests, method)(url,
                                                 data=payload,
                                                 headers=get_request_headers(
                                                     AuthenticationMode.TOKEN,
                                                     payload if payload else '',
                                                     token=self.token),
                                                 verify=self.verify,
                                                 timeout=self.timeout)
            if response.status_code not in [200, 201]:
                try:
                    message = response.json().get('error', {}).get('message', response.text)
                    raise DevoClientRequestException(response)
                except requests.exceptions.JSONDecodeError:
                    raise DevoClientException(ERROR_PROCESSING_REQUEST % response.text)
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                DevoClientException(ERROR_JSON_RESPONSE_EXPECTED % response.text)
        except DevoClientException as error:
            raise error
        except Exception as error:
            raise DevoClientException(ERROR_INVOKING_REQUEST) from error


domain = "devo_services"
lookup_name = "test3"
lookup_api = "https://api.stage.devo.com/lookup-api"

lookups = Lookups(lookup_api, auth={'token': os.getenv('DEVO_LOOKUPS_TOKEN')})

# pprint(lookups.get_lookups(domain))
payload_once = \
    {
        "id": {
            "creator": domain,
            "name": lookup_name
        },
        "visibility": "creator-only",
        "recipe": {
            "recipeType": "once",
            "source": {
                "query": "from siem.logtrust.web.activity where now()-1d < eventdate < now() group by username select username, count() as event_count, 'add' as type"
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
            # "secondaryIndexes": {},
            #"refreshMillis": 60 * 60 * 1000,
            #"startMillis": round(time.time() * 1000) - 24 * 60 * 60 * 1000,
            "requiresDate": False
        },
        "notifyStatus": False
    }
payload_periodic = \
    {
        "id": {
            "creator": domain,
            "name": lookup_name
        },
        "visibility": "creator-only",
        "recipe": {
            "recipeType": "periodic",
            "source": {
                "query": "from siem.logtrust.web.activity where now()-1h < eventdate < now() group by username select username, count() as event_count, 'add' as type"
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
            # "secondaryIndexes": {},
            "refreshMillis": 60 * 60 * 1000,
            "startMillis": round(time.time() * 1000) - 24 * 60 * 60 * 1000,
            "requiresDate": False
        },
        "notifyStatus": False
    }
# creation_result = lookups.create_lookup(domain, lookup_name, payload_periodic)
# pprint(creation_result)
# lookup_id = creation_result['id']
# while True:
#     job = lookups.get_lookup_job(domain, lookup_name, lookup_id)
#     pprint(job)
#     if job['jobs']:
#         break
#     time.sleep(30)
# if job['jobs'][0]['msg'] == 'Lookup successfully created':
#     pprint(lookups.describe_lookup(domain, lookup_name))
#    pprint(lookups.delete_lookup(domain, lookup_name))