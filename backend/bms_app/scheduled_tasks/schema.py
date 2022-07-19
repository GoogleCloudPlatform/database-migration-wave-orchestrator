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

from datetime import datetime, timedelta

from marshmallow import Schema, fields

from bms_app import ma
from bms_app.models import ScheduledTask


class ScheduledTaskSchema(Schema):
    db_id = fields.Integer()
    schedule_time = fields.DateTime(
        '%Y-%m-%dT%H:%M:%S.%fZ',
        required=True,
        validate=lambda x: (datetime.utcnow() + timedelta(hours=720)) > x > datetime.utcnow()
    )


class ScheduledTaskOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ScheduledTask
        fields = ('id', 'completed', 'schedule_time', 'db_id')

    schedule_time = fields.DateTime('%Y-%m-%dT%H:%M:%S.%fZ')


class SourceDbIdSchema(Schema):
    db_id = fields.Integer(required=True)
