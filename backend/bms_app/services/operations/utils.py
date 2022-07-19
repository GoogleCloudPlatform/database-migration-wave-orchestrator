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

from bms_app.models import (
    PRE_RESTORE_ALLOWED_STATUSES, RESTORE_ALLOWED_STATUSES, SourceDBStatus
)


def is_restore_allowed(source_db):
    """Check is restore operation is allowed for the database.

    Restore is allowed if:
    - restore config is configured
    - if run_pre_restore == True and it is complete
    - if run_pre_restore == False and source db status is DEPLOYED or higher
    """
    if not source_db.restore_config \
            or not source_db.restore_config.is_configured:
        return False

    run_pre_restore = source_db.restore_config.run_pre_restore

    if run_pre_restore:
        allowed_statuses = [SourceDBStatus.PRE_RESTORE_COMPLETE]
    else:
        allowed_statuses = PRE_RESTORE_ALLOWED_STATUSES

    return source_db.status in allowed_statuses + RESTORE_ALLOWED_STATUSES


def is_pre_restore_allowed(source_db):
    """Check is pre_restore operation is allowed for the database."""
    return source_db.restore_config \
        and source_db.restore_config.is_configured \
        and source_db.restore_config.run_pre_restore \
        and source_db.status in PRE_RESTORE_ALLOWED_STATUSES
