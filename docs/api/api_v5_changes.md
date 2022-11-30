# Devo Api Client v4 to v5

## `timeout` parameter set as 300 seconds by default

* `timeout` parameter is set as `300` seconds by default, instead of `30`. If set to `None`, it means queries are indefinitely blocked by default until server answers.

## Retry mechanism delay configurable

* There is a new `retry_delay` parameter with default value of `5` seconds, that represents the base delay for the exponential backoff algorithm with rate reduction of `2`. In former versions it was the same value of `timeout` parameter

## `DevoClientException` improvements

* `DevoClientException` detailed fields for precise information
* In query error detection (when the server error arises in the middle of the query processing) and feedback through `DevoClientException`