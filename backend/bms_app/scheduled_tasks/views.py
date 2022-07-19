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

from flask import request
from marshmallow import ValidationError

from bms_app.models import ScheduledTask, db
from bms_app.scheduled_tasks import bp
from bms_app.scheduled_tasks.schema import (
    ScheduledTaskOutputSchema, ScheduledTaskSchema, SourceDbIdSchema
)
from bms_app.scheduled_tasks.services import (
    add_record_to_db, create_google_task, validate_source_db
)
from bms_app.services.gcloud_tasks import delete_task
from bms_app.services.operations.restore import RestoreOperation
from bms_app.services.scheduled_tasks import (
    delete_planned_task, get_planned_task
)


@bp.route('<int:task_id>/run', methods=['POST'])
def run(task_id):
    task = ScheduledTask.query.get_or_404(task_id)

    if not task.completed:
        task.completed = True
        db.session.add(task)
        db.session.commit()

        RestoreOperation().run(db_id=task.source_db.id)

    return {}, 201


@bp.route('', methods=['POST'])
def add_scheduled_task():
    """Add schedule task."""
    validated_data = ScheduledTaskSchema().load(request.json)

    validate_source_db(validated_data['db_id'])

    scheduled_task = add_record_to_db(
        db_id=validated_data['db_id'],
        schedule_time=validated_data['schedule_time']
    )

    google_task = create_google_task(scheduled_task)

    scheduled_task.g_task_name = google_task.name
    db.session.commit()

    return {}, 201


@bp.route('/<int:task_id>', methods=['DELETE'])
def delete_scheduled_task(task_id):
    """Delete scheduled task from GoogleTask and ScheduledTask db"""
    scheduled_task = ScheduledTask.query.get_or_404(task_id)

    if scheduled_task.completed:
        raise ValidationError(
            {'_schema': ['completed task can not be deleted']}
        )

    delete_planned_task(scheduled_task)

    return {}, 204


@bp.route('', methods=['GET'])
def get_task():
    validated_data = SourceDbIdSchema().load(request.args)

    task = get_planned_task(validated_data['db_id'])

    return {'data': [ScheduledTaskOutputSchema().dump(task)]}


@bp.route('<int:task_id>', methods=['PUT'])
def edit_scheduled_task(task_id):
    """Edit schedule task.

    GoogleTask does not support task edit.
    It is needed to remove old GoogleTask and create new one.
    """
    validated_data = ScheduledTaskSchema().load(request.json)

    task = ScheduledTask.query.get_or_404(task_id)

    # only incomplete task can be edited
    if task.completed:
        raise ValidationError({'_schema': 'Completed task can not be edited'})

    # delete GoogleTask
    delete_task(task.g_task_name)

    # update time
    task.schedule_time = validated_data['schedule_time']

    # create new google task
    google_task = create_google_task(task)

    # update google task name
    task.g_task_name = google_task.name

    db.session.add(task)
    db.session.commit()

    return ScheduledTaskOutputSchema().dump(task)
