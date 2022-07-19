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

from urllib.parse import urljoin

from marshmallow import ValidationError

from bms_app import settings
from bms_app.models import ScheduledTask, SourceDB, db
from bms_app.services.cloud_run import get_cloud_run_service_object
from bms_app.services.gcloud_tasks import create_task
from bms_app.services.operations.utils import is_restore_allowed
from bms_app.services.scheduled_tasks import get_planned_task


def get_webhook_url(domain_name, scheduled_task):
    return urljoin(
        domain_name,
        f'/api/scheduled-tasks/{scheduled_task.id}/run'
    )


def create_google_task(scheduled_task):
    """Create Google Cloud task."""
    domain_name = getattr(settings, 'GCP_LB_URL', None)
    oauth_client_id = getattr(settings, 'GCP_OAUTH_CLIENT_ID', None)

    kwargs = {}

    # if we have specified domain name and Oauth CloudId
    # it means that IAP is configued
    # so CloudTasks should make request with authentication
    if domain_name and oauth_client_id:
        url = get_webhook_url(domain_name, scheduled_task)

        kwargs.update({
            'service_account_email': settings.GCP_SERVICE_ACCOUNT,
            'audience': oauth_client_id,
        })
    else:
        cloud_run_service_obj = get_cloud_run_service_object(
            settings.GCP_CLOUD_RUN_SERVICE_NAME
        )
        url = get_webhook_url(cloud_run_service_obj.uri, scheduled_task)

    google_task = create_task(
        settings.GCP_CLOUD_TASKS_QUEUE,
        scheduled_task.schedule_time,
        url,
        **kwargs
    )

    return google_task


def validate_source_db(db_id):
    """Check whether new task can be created."""
    source_db = SourceDB.query.get(db_id)

    if not source_db:
        raise ValidationError({'db_id': ['incorrect db_id']})

    # only one incomplete task is allowed
    if get_planned_task(db_id):
        raise ValidationError(
            {'db_id': ['The database already has a scheduled task']}
        )

    # db should be in a status allowed to restore
    if not is_restore_allowed(source_db):
        raise ValidationError(
            {'db_id': [f'wrong db status: {source_db.status}']}
        )


def add_record_to_db(db_id, schedule_time):
    scheduled_task = ScheduledTask(
        schedule_time=schedule_time,
        db_id=db_id,
    )
    db.session.add(scheduled_task)
    db.session.flush()

    return scheduled_task
