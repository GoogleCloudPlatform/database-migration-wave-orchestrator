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

from unittest.mock import MagicMock, patch

from bms_app import settings
from bms_app.scheduled_tasks.services import create_google_task

from tests.factories import ScheduledTaskFactory


@patch('bms_app.scheduled_tasks.services.settings.GCP_OAUTH_CLIENT_ID', '12345', create=True)
@patch('bms_app.scheduled_tasks.services.settings.GCP_LB_URL', 'https://abc.com', create=True)
@patch('bms_app.scheduled_tasks.services.get_cloud_run_service_object',)
@patch('bms_app.scheduled_tasks.services.create_task')
def test_create_task_with_authentication(create_task_mock, cr_obj_mock, client):
    task = ScheduledTaskFactory()

    create_google_task(task)

    assert not cr_obj_mock.called

    create_task_mock.assert_called_with(
        settings.GCP_CLOUD_TASKS_QUEUE,
        task.schedule_time,
        f'https://abc.com/api/scheduled-tasks/{task.id}/run',
        service_account_email=settings.GCP_SERVICE_ACCOUNT,
        audience='12345'
    )



@patch('bms_app.scheduled_tasks.services.settings.GCP_OAUTH_CLIENT_ID', new=None)
@patch('bms_app.scheduled_tasks.services.settings.GCP_LB_URL', new=None, )
@patch('bms_app.scheduled_tasks.services.get_cloud_run_service_object', return_value=MagicMock(uri='https://cr.uri'))
@patch('bms_app.scheduled_tasks.services.create_task')
def test_create_task_without_authentication(create_task_mock, cr_obj_mock, client):
    task = ScheduledTaskFactory()

    create_google_task(task)

    create_task_mock.assert_called_with(
        settings.GCP_CLOUD_TASKS_QUEUE,
        task.schedule_time,
        f'https://cr.uri/api/scheduled-tasks/{task.id}/run',
    )
