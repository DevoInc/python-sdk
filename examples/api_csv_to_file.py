import os
from devo.api import Client, ClientConfig, TO_BYTES


key = os.getenv('DEVO_API_KEY', None)
secret = os.getenv('DEVO_API_SECRET', None)

api = Client(auth={"key": key, "secret": secret},
             address="https://apiv2-eu.devo.com/search/query",
             config=ClientConfig(response="csv",
                                 stream=True, processor=TO_BYTES))


response = api.query(query="from demo.ecommerce.data select * limit 20",
                     dates={'from': "today()-1*day()", 'to': "today()"})

with open("example_data/example.csv", "wb") as f:
    try:
        for item in response:
            f.write(item)
            f.write(b"\n")
    except Exception as error:
        print(error)
