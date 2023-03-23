ERROR_MSGS = {
    "no_query": "Error: Not query provided.",
    "no_auth": "Client don't have key&secret or auth token/jwt",
    "no_endpoint": "Endpoint 'address' not found",
    "to_but_no_from": "If you use end dates for the query 'to' it is "
                      "necessary to use start date 'from'",
    "binary_format_requires_output": "Binary format like `msgpack` and `xls` requires output"
                                     " parameter",
    "wrong_processor": "processor must be lambda/function or one of the defaults API processors.",
    "default_keepalive_only": "Mode '%s' always uses default KeepAlive Token",
    "keepalive_not_supported": "Mode '%s' does not support KeepAlive Token",
    "stream_mode_not_supported": "Mode '%s' does not support stream mode",
    "future_queries_not_supported": "Modes 'xls' and 'msgpack' does not support future queries"
                                    " because KeepAlive tokens are not available for those "
                                    "resonses type",
    "missing_api_key": "You need a API Key and API secret to make this",
    "data_query_error": "Error while receiving query data: %s ",
    "connection_error": "Failed to establish a new connection",
    "other_errors": "Error while invoking query",
    "error_no_detail": "Error code %d while invoking query"
}