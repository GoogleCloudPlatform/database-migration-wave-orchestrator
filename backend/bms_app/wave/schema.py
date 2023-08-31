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

import models

from marshmallow import validates, fields, Schema
from bms_app import ma
from validators import validate_project_id

class WaveResponse(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = models.Wave
        include_fk = True

    @validates('project_id')
    def validated_project_id_exists(self, value):
        validate_project_id(value)

class WaveUpdate(Schema):
    name = fields.Str(required=True)

class WaveCreate(Schema):
    name = fields.Str(required=True)
    project_id = fields.Int(required=True)

    @validates('project_id')
    def validated_project_id_exists(self, value):
        validate_project_id(value)

