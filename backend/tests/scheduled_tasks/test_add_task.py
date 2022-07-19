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

from datetime import timedelta
from unittest.mock import patch

from faker import Faker

from bms_app.models import ScheduledTask, SourceDBStatus, db

from tests.factories import (
    RestoreConfigFactory, ScheduledTaskFactory, SourceDBFactory
)


fake = Faker()


class FakeGoogleTask:
    def __init__(self, name):
        self.name = name


@patch('bms_app.scheduled_tasks.views.create_google_task', return_value=FakeGoogleTask('g-task-name-1'))
def test_add_task(create_mock, client):
    """Test add scheduled task"""
    source_db = SourceDBFactory(status=SourceDBStatus.DT_COMPLETE)
    RestoreConfigFactory(source_db=source_db, is_configured=True)
    planned_at = fake.future_datetime()
    add_task_data = {
        'db_id': source_db.id,
        'schedule_time': planned_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    req = client.post(f'/api/scheduled-tasks', json=add_task_data)

    assert req.status_code == 201

    task = db.session.query(ScheduledTask) \
        .filter(ScheduledTask.db_id == add_task_data['db_id'],
                ScheduledTask.schedule_time == planned_at) \
        .first()
    assert task

    create_mock.assert_called_with(task)


@patch('bms_app.scheduled_tasks.views.create_google_task')
def test_do_not_create_task_with_time_more_than_thirty_days(create_mock, client):
    """Test do not create scheduled task when time is more than 30 days in advance"""
    source_db = SourceDBFactory(status=SourceDBStatus.PRE_RESTORE_COMPLETE)
    RestoreConfigFactory(source_db=source_db, is_configured=True, run_pre_restore=True)
    planned_at = fake.future_datetime() + timedelta(hours=720)
    add_task_data = {
        'db_id': source_db.id,
        'schedule_time': planned_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    req = client.post(f'/api/scheduled-tasks', json=add_task_data)

    assert req.status_code == 400
    assert req.json['errors']['schedule_time']

    assert not db.session.query(ScheduledTask).count()
    assert not create_mock.called


@patch('bms_app.scheduled_tasks.views.create_google_task')
def test_do_not_create_task_for_db_with_not_allowed_status(create_mock, client):
    """Test do not create scheduled task when DB in wrong status"""
    source_db = SourceDBFactory(status=SourceDBStatus.EMPTY)
    RestoreConfigFactory(source_db=source_db)

    planned_at = fake.future_datetime()
    add_task_data = {
        'db_id': source_db.id,
        'schedule_time': planned_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    req = client.post(f'/api/scheduled-tasks', json=add_task_data)

    assert req.status_code == 400
    assert req.json['errors']['db_id']

    assert not db.session.query(ScheduledTask).count()
    assert not create_mock.called


@patch('bms_app.scheduled_tasks.views.create_google_task')
def test_do_not_create_task_with_time_in_past(create_mock, client):
    """Test do not create scheduled task when DB in wrong status"""
    source_db = SourceDBFactory(status=SourceDBStatus.DT_COMPLETE)

    planned_at = fake.past_datetime()
    add_task_data = {
        'db_id': source_db.id,
        'schedule_time': planned_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    req = client.post(f'/api/scheduled-tasks', json=add_task_data)

    assert req.status_code == 400
    assert req.json['errors']['schedule_time']

    assert not db.session.query(ScheduledTask).count()
    assert not create_mock.called


@patch('bms_app.scheduled_tasks.views.create_google_task')
def test_do_not_create_task_with_wrong_db_id(create_mock, client):
    """Test do not create scheduled task when SourceDB.id is wrong"""
    SourceDBFactory(status=SourceDBStatus.DT_COMPLETE)

    planned_at = fake.future_datetime()
    add_task_data = {
        'db_id': 2,
        'schedule_time': planned_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    req = client.post(f'/api/scheduled-tasks', json=add_task_data)

    assert req.status_code == 400
    assert req.json['errors']['db_id']

    assert not db.session.query(ScheduledTask).count()
    assert not create_mock.called


@patch('bms_app.scheduled_tasks.views.create_google_task')
def test_do_not_create_task_for_db_that_already_has_uncompleted_scheduled_task(create_mock, client):
    """Test do not create scheduled task when DB has scheduled, uncompleted task"""
    source_db = SourceDBFactory(status=SourceDBStatus.PRE_RESTORE_COMPLETE)
    ScheduledTaskFactory(source_db=source_db, completed=False)
    planned_at = fake.future_datetime()
    add_task_data = {
        'db_id': source_db.id,
        'schedule_time': planned_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    }

    req = client.post(f'/api/scheduled-tasks', json=add_task_data)

    assert req.status_code == 400
    assert req.json['errors']['db_id']

    tasks = db.session.query(ScheduledTask).count()
    assert tasks == 1

    assert not create_mock.called
