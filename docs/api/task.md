# TASK OPERATIONS

## Check Status Of a Job

These method is used to check the status of a Query Job.

```python
from devo.api.client import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query")
              
job_id = "aaaaa-bbbbb-ccccc-dddd"
response = api.get_job(job_id)
```

##### Request parameter
  - **jobId**: is the unique identifier returned when the query is launched.

##### Response parameters

| FieldName | Type    | Description                                                            |
|-----------|---------|------------------------------------------------------------------------|
| msg       | String  | Message Description in case of error                                   |
| status    | Integer | Numeric value  that especify the error code.0 - OK 1 - Invalid request |
| object    | Object  | Job_Status Object, containing the current status of the Job            |


    - Job_Status Object: Object that contains the information needed to check the status of the Query that is forwarding the response to the targets.
    (**Warning:** This Object contains information as we actually consider is needed, probably this object will be extended in the future depending of the needs and experience gained)

| Field Name   | Type   | Description                                                                                                  |
|--------------|--------|--------------------------------------------------------------------------------------------------------------|
| status       | String | (NOTE: object.status values are described in Background/Async Tasks  Section at the bottom of this document) |
| lastDatetime | long   | value of milliseconds of last date of an event received by malote                                            |
| type         | String | "redis", the type of the task                                                                                |
| friendlyName | String | Name given by the user to this task                                                                          |
| query        | String | LinQ or QueryId of the Query associated to this task                                                         |
| error        | list   | List of errors on any, when running the task                                                                 |
| extra        | object | custom object that returns data that the Task want to share                                                  |

##### Response example:

```json
{
    "status": 0,
    "cid": "0uRuSH6Rnt",
    "timestamp": 1527783750851,
    "object": {
        "status": "COMPLETED",
        "id": "ea62e2fd-4819-4a52-b5a2-ac7d92ec65a1",
        "eventGenerated": 37733,
        "eventsSent": 37733,
        "lastDatetime": 1525794913948,
        "error": []
    }
}
```

## Find All Jobs

These method is used to get the status of all the Jobs the Domain has launched and are currently running.

```python
from devo.api.client import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query")
response = api.get_jobs()
```


##### Response

| FieldName | Type    | Description                                                                            |
|-----------|---------|----------------------------------------------------------------------------------------|
| msg       | String  | Message Description in case of error                                                   |
| status    | Integer | Numeric value  that especify the error code.0 - OK 1 - Invalid request                 |
| object    | List    | list of all the Job_Status Object, containing the current status of the Jobs requested |

##### Response example:

```json
{
    "status": 0,
    "cid": "0uRuSH6Rnt",
    "timestamp": 1527783750851,
    "object": [
        {
            "status": "COMPLETED",
            "id": "ea62e2fd-4819-4a52-b5a2-ac7d92ec65a1",
            "eventGenerated": 37733,
            "eventsSent": 37733,
            "lastDatetime": 1525794913948,
            "error": []
        },
        {
            "status": "COMPLETED",
            "id": "1f37ed42-d0be-49cb-9b8a-eff7c2f0b5e6",
            "eventGenerated": 4783,
            "eventsSent": 4783,
            "lastDatetime": 1525960711885,
            "error": []
        }
    ]
}
```

## Find all jobs by type

Find All Jobs with a specific type.
These method is used to get the status of all the Jobs the Domain has launched and are currently running.

```python
from devo.api.client import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query")
response = api.get_jobs(type="donothing")
```


##### Response parameters

| FieldName | Type | Description |
|-----------|------|-------------|
| msg | String | Message Description in case of error |
| status | Integer | Numeric value  that especify the error code.0 - OK 1 - Invalid request |
| object | List | list of all the Job_Status Object, containing the current status of the Jobs requested |

## Find all jobs By Type And Name

Find All Jobs with a specific type and Name ( find all that start with the name requested)
These method is used to get the status of all the Jobs the Domain has launched and are currently running.

```python
from devo.api.client import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query")
response = api.get_jobs(type="donothing", name="devo-sdk-test")
```

##### Response parameters

| FieldName | Type | Description |
|-----------|------|-------------|
| msg | String | Message Description in case of error |
| status | Integer | Numeric value  that especify the error code.0 - OK 1 - Invalid request |
| object | List | list of all the Job_Status Object, containing the current status of the Jobs requested |

## Stop a Job

These method is used to Stop a currently running Job.

```python
from devo.api.client import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query")
job_id = "aaaaa-bbbbb-ccccc-dddd"
response = api.stop_job(job_id)
```

##### Request parameter

  - **jobId**: is the unique identifier returned when the query is launched.

##### Response

| FieldName | Type    | Description                                                                 |
|-----------|---------|-----------------------------------------------------------------------------|
| msg       | String  | Message Description in case of error                                        |
| status    | Integer | Numeric value  that especify the error code. 0 - OK or see task error table |
| object    | Object  | Job_Status Object, containing the current status of the Job                 |

##### Response example:

```json
{
    "status": 0,
    "cid": "0uRuSH6Rnt",
    "timestamp": 1527783750851,
    "object": {
        "status": "STOPPED",
        "id": "04426977-a37e-45b8-b8d2-da6a5608d713",
        "lastDatetime": 1526846001907,
        "error": []
    }
}
```

## Start a Job (Restart a stopped job)

These method is used to Start a Job that was previously stopped.

The Job Start Date will be from the last last_datetime  saved information.

```python
from devo.api.client import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query")
job_id = "aaaaa-bbbbb-ccccc-dddd"
response = api.start_job(job_id)
```

##### Request parameter 

  - **jobId**: is the unique identifier returned when the query is launched.

##### Response

| FieldName | Type    | Description                                                                 |
|-----------|---------|-----------------------------------------------------------------------------|
| msg       | String  | Message Description in case of error                                        |
| status    | Integer | Numeric value  that especify the error code. 0 - OK or see task error table |
| object    | Object  | Job_Status Object, containing the current status of the Job                 |

##### Response example:

```json
{
    "status": 0,
    "cid": "0uRuSH6Rnt",
    "timestamp": 1527783750851,    
    "object": {
        "status": "RUNNING",
        "id": "04426977-a37e-45b8-b8d2-da6a5608d713",
        "lastDatetime": 1526846001907,
        "error": []
    }
}
```

## Remove a Job

These method is used to remove a Job, a removed Job can not be started again.

```python
from devo.api.client import Client

api = Client(key="myapikey",
              secret="myapisecret",
              url="https://apiv2-eu.devo.com/search/query")
job_id = "aaaaa-bbbbb-ccccc-dddd"
response = api.remove_job(job_id)
```

##### Request parameter

  - **jobId**: is the unique identifier returned when the query is launched.

##### Response

| FieldName | Type    | Description                                                                 |
|-----------|---------|-----------------------------------------------------------------------------|
| msg       | String  | Message Description in case of error                                        |
| status    | Integer | Numeric value  that especify the error code. 0 - OK or see task error table |
| object    | Object  | Job_Status Object, containing the current status of the Job                 |

##### Example:

```json
{
    "status": 0,
    "cid": "0uRuSH6Rnt",
    "timestamp": 1527783750851,
    "object": {
        "status": "REMOVED",
        "id": "04426977-a37e-45b8-b8d2-da6a5608d713",
        "lastDatetime": 1526846382483,
        "error": []
    }
}
```

## Task Error Codes

| ID                                 | Code | Msg                                 |
|------------------------------------|------|-------------------------------------|
| TASK_OK                            | 0    | Ok                                  |
| TASK_NOT_FOUND                     | 100  | Task not found                      |
| TASK_STATUS_NOT_CHANGE             | 101  | Cannot change the status of task    |
| TASK_REMOVE_DB_ERROR               | 102  | Cannot remove task on database      |
| TASK_STOP_RUNNING_ERROR            | 108  | Cannot stop task a non running task |
| TASK_STOP_DB_ERROR                 | 103  | Cannot stop task on database        |
| TASK_RESTART_DB_ERROR              | 104  | Cannot restart task on database     |
| TASK_REMOTE_MSG_RESPONSE_NOT_FOUND | 105  | Remote msg response not found       |
| TASK_REMOTE_MSG_RESPONSE           | 106  | Remote msg response problem         |
| TASK_REMOTE_MSG                    | 107  | Remote msg call problem             |

## Task Status

| Status       | Description                                                                                                                           |
|--------------|---------------------------------------------------------------------------------------------------------------------------------------|
| CREATED      | Initial internal state, it's a temporal state before start first time the task                                                        |
| RUNNING      | Running task                                                                                                                          |
| COMPLETED    | Completed task by returning all elements. A query without 'to' date can't be completed                                                |
| STOPPED      | A stopped task. Can be restarted by user. A task can be stopped by user or by and error                                               |
| RECONNECTING | A temporal internal state on a loss connection with malote. It will be started when reconnect or stopped if cannot recover connection |
| REMOVED      | A stopped and delete task. **Deprecated** In future versions all removed task will be deleted and It cannot be found                  |
| PAUSED       | A internal state on stopped servers. It will be auto started after the server start again                                             |
