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

from marshmallow import ValidationError

from bms_app.models import ScheduledTask, db
from bms_app.services.gcloud_tasks import delete_task


def get_planned_task(db_id):
    """Return active scheduled task."""
    tasks = db.session.query(ScheduledTask) \
        .filter(ScheduledTask.db_id == db_id) \
        .filter(ScheduledTask.completed.is_(False)) \
        .all()

    if len(tasks) > 1:
        raise ValidationError(
            {'db_id': [f'unexpected number of active tasks: {len(tasks)}']}
        )

    return tasks[0] if tasks else None


def delete_planned_task(scheduled_task):
    delete_task(scheduled_task.g_task_name)

    db.session.delete(scheduled_task)
    db.session.commit()
