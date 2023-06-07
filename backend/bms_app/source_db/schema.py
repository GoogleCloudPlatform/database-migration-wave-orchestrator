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

from marshmallow import Schema, fields

from bms_app import ma
from bms_app.models import SourceDB
from bms_app.schema import LabelSchema
from bms_app.validators import validate_project_id


class MigvisorFileUploadSchema(Schema):
    project_id = fields.Integer(validate=validate_project_id)
    overwrite = fields.Boolean(load_default=False)


class SourceDBSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SourceDB

    db_size = fields.Float()
    project_id = fields.Integer()
    db_type = fields.Function(lambda obj: obj.db_type.value if obj.db_type else None)
    status = fields.Function(lambda obj: obj.status.value)
    is_rac = fields.Function(lambda obj: obj.is_rac)
    db_engine = fields.Function(lambda obj: obj.db_engine.value)
    wave_id = fields.Integer()

    labels = fields.Function(
        lambda obj: LabelSchema(
            only=['id', 'name'],
            many=True
        ).dump(obj.labels)
    )
