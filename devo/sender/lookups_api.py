from pprint import pprint

import requests

from devo.common.auth.common import get_request_headers, AuthenticationMode


class Lookups:
    def __init__(self, base_url, verify: bool = True, timeout: int = 30):
        self.base_url = base_url
        self.verify = verify
        self.timeout = timeout

    def get_lookups(self, domain: str):
        return requests.get(f"{self.base_url}/lookup/{domain}",
                            headers=get_request_headers(
                                AuthenticationMode.TOKEN,
                                '',
                            token=""),
                            verify=self.verify,
                            timeout=self.timeout)

lookups = Lookups("https://api-us.devo.com/lookup-api")

pprint(lookups.get_lookups("devo_services").content)