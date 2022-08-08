# Devo Api Client v3 to v4

## Main Changes
The Client object now manages amount of retries in a different way and some responses types/format are returned in `bytes` binary structure

### XLS and msgpack types are returned in `bytes`

`xls` and `msgpack` responses types are now returned in `bytes`structures instead of `str`. It makes sense after the binary nature of data

### Stream mode support

After analysis, it has been considered that stream mode only makes sense for `csv`, `tsv`, `json/simple`, `json/simple/compact` response modes. `xls` and `msgpack` do not support anymore.

### Retry mechanism semantics changed

* The retry mechanism is now disabled by default (it was 3 retries by default before). The `retries` parameter is set to `0`by default
* In order to enable it, you must set up the `retries` parameter with a value bigger or equals than `1`. The regular action/command is not considered a retry, only the additional attempts.

### Keep Alive mechanism by API server now supported

Some queries may require a big time to start returning data, because of the calculations required, the load of the platform or just because the data belongs to the future.
In such a cases, as the client is a common HTTP client, there is a timeout for the server for start returning data. When this timeout is over the client cancels the request, and it returns a timeout error.
In order to avoid this timeout errors, the server returns tokens every little time to reset the timeout control in the client. Client now supports the processing of these tokens to not spoil the data.
