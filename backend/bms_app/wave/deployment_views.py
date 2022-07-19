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
from marshmallow import Schema, fields

from bms_app.services.operations import DeploymentService, RollbackService
from bms_app.wave import bp


class SourceDBIdsSchema(Schema):
    db_ids = fields.List(fields.Integer, required=True)


class OptionalSourceDBIdsSchema(Schema):
    db_ids = fields.List(fields.Integer, load_default=None)


@bp.route('/<int:wave_id>/deployment', methods=['POST'])
def run_deployment(wave_id):
    """Run deployment.

    Optionally accept database ids that should be deployed.
    """
    validated_data = OptionalSourceDBIdsSchema().load(request.json)
    DeploymentService().run(wave_id, validated_data['db_ids'])

    return {}, 201


@bp.route('/<int:wave_id>/rollback', methods=['POST'])
def run_rollback(wave_id):
    """Run rollback/cleanup on specific db only."""
    validated_data = SourceDBIdsSchema().load(request.json)
    RollbackService().run(wave_id, validated_data['db_ids'])

    return {}, 201
