# Classes structure refactoring
Some classes were moved to avoid circular dependencies:
* COMPACT_TO_ARRAY, DEFAULT, JSON, JSON_SIMPLE, SIMPLECOMPACT_TO_ARRAY, SIMPLECOMPACT_TO_OBJ, TO_BYTES,  TO_STR, Client, ClientConfig: devo.api -> devo.api.client
* DevoClientException: devo.api -> devo.api.exception
* Sender, SenderConfigTCP, SenderConfigSSL, DevoSenderException: devo.sender -> devo.sender.data
* Lookup: devo.sender -> devo.sender.lookup
* All classes in devo.sender.transformsyslog are no longer available in devo.sender


# Lookups API
New Lookups API support added to the SDK