# Devo Api Client v4 to v5

## `timeout` parameter set as 300 seconds by default

* `timeout` parameter is set as `300` seconds by default. If set to `None`, it means queries are indefinitely blocked by default until server answers.

## Retry mechanism delay configurable

* There is a new `retry_delay` parameter with default value of `5` seconds, that represents the base delay for the exponential backoff algorithm with rate reduction of `2`

