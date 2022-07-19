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

from bms_app.models import SourceDBStatus

from tests.factories import ScheduledTaskFactory, SourceDBFactory


@patch('bms_app.scheduled_tasks.views.RestoreOperation.run')
def test_run_task(op_mock, client):
    source_db = SourceDBFactory(status=SourceDBStatus.DT)
    task = ScheduledTaskFactory(source_db=source_db)

    req = client.post(f'/api/scheduled-tasks/{task.id}/run')

    assert req.status_code == 201

    assert task.completed
    op_mock.assert_called_with(db_id=source_db.id)


@patch('bms_app.scheduled_tasks.views.RestoreOperation.run')
def test_not_run_completed_task(op_mock, client):
    source_db = SourceDBFactory(status=SourceDBStatus.PRE_RESTORE_COMPLETE)
    task = ScheduledTaskFactory(source_db=source_db, completed=True)

    req = client.post(f'/api/scheduled-tasks/{task.id}/run')

    assert req.status_code == 201

    not op_mock.called
