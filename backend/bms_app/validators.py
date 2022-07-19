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

"""Utils."""

from marshmallow import ValidationError

from bms_app.models import Project, SourceDB, db


def validate_project_id(project_id):
    """Raise an exception if project_id does not exist."""
    if not db.session.query(Project.id) \
            .filter(Project.id == project_id).count():
        raise ValidationError('invalid project_id')


def validate_source_db_id(db_id):
    """Raise an exception if source_db_id does not exist."""
    if not db.session.query(SourceDB.id) \
            .filter(SourceDB.id == db_id).count():
        raise ValidationError('invalid source_db_id')


def check_if_text(file_object):
    """Check if file format is text"""
    try:
        file_object.read().decode()
        file_object.seek(0)
    except UnicodeDecodeError:
        return False
    else:
        return True
