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

from bms_app.models import (
    BMSServer, Mapping, Operation, OperationDetails, SourceDB, SourceDBType,
    Wave, db
)
from bms_app.schema import AddWaveSchema, WaveSchema
from bms_app.services.utils import generate_target_gcp_logs_link
from bms_app.wave import bp
from bms_app.wave.services import (
    GetWaveService, list_waves_service, validate_wave_name_is_unique
)
from bms_app.wave.services.waves import assign_source_db_wave


@bp.route('', methods=['GET'])
def list_waves():
    """Return all available waves."""
    project_id = request.args.get('project_id', type=int)

    data = list_waves_service(project_id)

    return {
        'data': data
    }


@bp.route('/<int:wave_id>', methods=['GET'])
def get_wave(wave_id):
    """Return wave."""
    return GetWaveService.run(
        wave_id=wave_id,
        return_details=request.args.get('details')
    )


@bp.route('/<int:wave_id>/operations/<int:operation_id>/details', methods=['GET'])
def get_operation_details(wave_id, operation_id):
    """Return details/histories of the particular operation."""
    query = db.session.query(OperationDetails, SourceDB, BMSServer) \
        .join(Mapping, OperationDetails.mapping_id == Mapping.id) \
        .join(SourceDB, Mapping.db_id == SourceDB.id) \
        .join(BMSServer, Mapping.bms_id == BMSServer.id) \
        .filter(OperationDetails.operation_id == operation_id) \
        .all()

    response = {}
    for op_details, source_db, bms_server in query:
        db_id = source_db.id
        if db_id not in response:
            response[db_id] = {
                'status': op_details.status.value,
                'operation_id': op_details.operation_id,
                'operation_type': op_details.operation_type.value,
                'wave_id': op_details.wave_id,
                'source_db': {
                    'source_hostname': source_db.server,
                    'db_name': source_db.db_name,
                    'db_type': source_db.db_type.value,
                    'is_rac': source_db.db_type == SourceDBType.RAC,
                    'oracle_version': source_db.oracle_version,
                },
                'bms': []
            }
        logs_url = generate_target_gcp_logs_link(op_details, bms_server)
        response[db_id]['bms'].append({
            'id': bms_server.id,
            'name': bms_server.name,
            'logs_url': logs_url,
            'started_at': op_details.started_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'completed_at': op_details.completed_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'step': op_details.step,
            'mapping_id': op_details.mapping_id
        })

    return {'data': list(response.values())}


@bp.route('/<int:wave_id>', methods=['DELETE'])
def delete_wave(wave_id):
    """Delete wave."""
    operation_exists = db.session.query(Wave, Operation) \
        .filter(Operation.wave_id == Wave.id) \
        .filter(Wave.id == wave_id).count()
    if operation_exists:
        raise ValidationError({'wave_id': ['wave is not empty']})

    SourceDB.query.filter(SourceDB.wave_id == wave_id).update({'wave_id': None})

    wave = Wave.query.get_or_404(wave_id)
    db.session.delete(wave)
    db.session.commit()

    return {}, 204


@bp.route('/<int:wave_id>', methods=['PUT'])
def edit_wave(wave_id):
    """Update wave."""
    validated_data = WaveSchema(only=['name', 'project_id']).load(request.json)
    wave = Wave.query.get_or_404(wave_id)

    validate_wave_name_is_unique(
        validated_data['name'],
        wave.project_id,
        exclude_wave_id=wave_id
    )

    wave.name = validated_data['name']

    db.session.add(wave)
    db.session.commit()

    return WaveSchema().dump(wave)


@bp.route('', methods=['POST'])
def add_wave():
    """Add wave."""
    validated_data = AddWaveSchema().load(request.json)

    wave = db.session.query(Wave).filter(
        Wave.name == validated_data['name'],
        Wave.project_id == validated_data['project_id']
    ).first()

    if not wave:
        wave = Wave(
            name=validated_data['name'],
            project_id=validated_data['project_id']
        )

        db.session.add(wave)
        db.session.commit()

    response = {}

    if validated_data.get('db_ids'):
        assigment_result = assign_source_db_wave(
            wave=wave,
            db_ids=validated_data['db_ids']
        )
        response.update(assigment_result)

    return response, 201
