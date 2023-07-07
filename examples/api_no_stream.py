import os

from devo.api import JSON, Client, ClientConfig

key = os.getenv("DEVO_API_KEY", None)
secret = os.getenv("DEVO_API_SECRET", None)

api = Client(
    auth={"key": key, "secret": secret},
    address="https://apiv2-eu.devo.com/search/query",
    config=ClientConfig(response="json", processor=JSON),
)

response = api.query(
    query="from demo.ecommerce.data select * limit 20",
    dates={"from": "today()-1*day()", "to": "today()"},
)

print(response)
