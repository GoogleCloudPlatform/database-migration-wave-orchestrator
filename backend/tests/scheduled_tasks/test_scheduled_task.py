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

from bms_app.models import ScheduledTask, SourceDBStatus, db

from tests.factories import ScheduledTaskFactory, SourceDBFactory


@patch('bms_app.services.scheduled_tasks.delete_task')
def test_delete_task(delete_task_mock, client):
    """Test delete scheduled task"""
    source_db = SourceDBFactory(status=SourceDBStatus.DT)
    task = ScheduledTaskFactory(source_db=source_db, completed=False)

    assert not task.completed

    req = client.delete(f'/api/scheduled-tasks/{task.id}')

    assert req.status_code == 204

    assert not db.session.query(ScheduledTask).filter(ScheduledTask.id == task.id).count()


def test_do_not_delete_task(client):
    """Test do not delete scheduled task when it is completed"""
    source_db = SourceDBFactory(status=SourceDBStatus.DT)
    task = ScheduledTaskFactory(source_db=source_db, completed=True)

    assert task.completed

    req = client.delete(f'/api/scheduled-tasks/{task.id}')

    assert req.status_code == 400
