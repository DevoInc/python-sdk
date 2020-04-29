import os
from devo.api import Client, ClientConfig, SIMPLECOMPACT_TO_OBJ


key = os.getenv('DEVO_API_KEY', None)
secret = os.getenv('DEVO_API_SECRET', None)

api = Client(auth={"key": key, "secret": secret},
             address="https://apiv2-eu.devo.com/search/query",
             config=ClientConfig(response="json/simple/compact",
                                 stream=True, processor=SIMPLECOMPACT_TO_OBJ))


response = api.query(query="from demo.ecommerce.data select * ",
                     dates={'from': "today()-1*day()"})

for item in response:
    print(item)
