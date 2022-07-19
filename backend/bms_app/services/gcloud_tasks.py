# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2


def create_task(queue_path, schedule_dt, url,
                service_account_email=None, audience=None):
    """Create Google Task (HTTP Target).

    Params:
    - queue_path: full GoogleTasks queue name.
    - schedule_dt: datetime in the future when it should be executed.
    - url: url that will be requested with GET method.
    """
    # Create a client.
    client = tasks_v2.CloudTasksClient()

    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(schedule_dt)

    # Construct the request body.
    task = {
        'http_request': {  # Specify the type of request.
            'http_method': tasks_v2.HttpMethod.POST,
            'url': url,  # The full url path that the task will be sent to.
        },
        'schedule_time': timestamp,
    }

    if service_account_email and audience:
        task['http_request']['oidc_token'] = {
            'service_account_email': service_account_email,
            'audience': audience
        }

    # Use the client to build and send the task.
    response = client.create_task(
        request={
            'parent': queue_path,
            'task': task
        }
    )

    return response


def delete_task(task_path):
    """Delete a task from Google Tasks.

    Params:
    - task_path - full task name, e.g. projects/<project>/locations/<location>/queues/<queue>/tasks/<task_name>
    """
    # Create a client
    client = tasks_v2.CloudTasksClient()
    # Initialize request argument(s)
    request = tasks_v2.DeleteTaskRequest(
        name=task_path,
    )
    # Make the request
    client.delete_task(request=request)
