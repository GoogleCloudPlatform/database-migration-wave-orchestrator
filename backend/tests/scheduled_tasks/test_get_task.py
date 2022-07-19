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

from faker import Faker

from bms_app.models import SourceDBStatus

from tests.factories import ScheduledTaskFactory, SourceDBFactory


fake = Faker()


def test_get_task(client):
    """Test get scheduled task"""
    source_db = SourceDBFactory(status=SourceDBStatus.DT)
    # already completed task
    ScheduledTaskFactory(
        source_db=source_db,
        completed=True,
        schedule_time=fake.past_datetime()
    )
    # relevant task
    task = ScheduledTaskFactory(source_db=source_db, completed=False)

    req = client.get(f'/api/scheduled-tasks?db_id={source_db.id}')
    data = req.json

    assert req.status_code == 200

    assert data == {
        "data": [
            {
                "completed": False,
                "id": task.id,
                "db_id": source_db.id,
                "schedule_time": task.schedule_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        ]
    }
