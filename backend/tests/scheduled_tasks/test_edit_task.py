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

from unittest.mock import patch

from faker import Faker

from tests.factories import ScheduledTaskFactory, SourceDBFactory


fake = Faker()


class FakeGoogleTask:
    def __init__(self, name):
        self.name = name


@patch('bms_app.scheduled_tasks.views.create_google_task', return_value=FakeGoogleTask('g-task-name-2'))
@patch('bms_app.scheduled_tasks.views.delete_task')
def test_edit_scheduled_task(del_mock, create_mock, client):
    source_db = SourceDBFactory()
    task = ScheduledTaskFactory(
        source_db=source_db,
        completed=False,
        g_task_name='g-task-name-1'
    )

    upd_dt = fake.future_datetime()

    req = client.put(
        f'/api/scheduled-tasks/{task.id}',
        json={
            'schedule_time': upd_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'db_id': source_db.id
        }
    )

    assert req.status_code == 200

    assert task.schedule_time == upd_dt
    assert task.g_task_name == create_mock.return_value.name

    del_mock.assert_called_with('g-task-name-1')
    create_mock.assert_called_with(task)


@patch('bms_app.scheduled_tasks.views.create_google_task')
@patch('bms_app.scheduled_tasks.views.delete_task')
def test_do_not_edit_completed_scheduled_task(del_mock, create_mock, client):
    source_db = SourceDBFactory()
    past_datetime = fake.past_datetime()
    task = ScheduledTaskFactory(
        source_db=source_db,
        schedule_time=past_datetime,
        completed=True,
        g_task_name='g-task-name-1'
    )

    upd_dt = fake.future_datetime()

    req = client.put(
        f'/api/scheduled-tasks/{task.id}',
        json={
            'schedule_time': upd_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'db_id': source_db.id
        }
    )

    assert req.status_code == 400

    assert task.schedule_time == past_datetime
    assert task.g_task_name == 'g-task-name-1'

    assert not del_mock.called
    assert not create_mock.called
