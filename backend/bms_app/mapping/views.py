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
from marshmallow import Schema, ValidationError, fields

from bms_app.mapping import bp
from bms_app.mapping.services import (
    AddMappingService, EditMappingService, GetMappingsService
)
from bms_app.models import Mapping, OperationDetails, SourceDB, db
from bms_app.services.source_db import (
    clear_bms_target_params, does_db_have_operation
)


MAPPING_IS_USED = 'Mapping is already involved in some operation' \
                  ' and can not be changed'


class EditMappingSchema(Schema):
    db_id = fields.Int(required=True)
    wave_id = fields.Int(allow_none=True)
    bms_id = fields.List(fields.Int())
    fe_rac_nodes = fields.Int()


class CreateMappingSchema(Schema):
    db_id = fields.Int(required=True)
    wave_id = fields.Int(allow_none=True)
    bms_id = fields.List(fields.Int())
    fe_rac_nodes = fields.Int()


@bp.route('', methods=['GET'])
def list_mappings():
    """Return all available mappings."""
    # get all within current project
    project_id = request.args.get('project_id', type=int)
    # get for specific db
    db_id = request.args.get('db_id', type=int)

    response = GetMappingsService.run(
        project_id=project_id,
        db_id=db_id
    )
    return {'data': response}


@bp.route('', methods=['POST'])
def add_mapping():
    """Add mapping(s)."""
    validated_data = CreateMappingSchema().load(request.json)
    AddMappingService.run(
        db_id=validated_data['db_id'],
        bms_ids=validated_data['bms_id'],  # to keep old schema on FE
        wave_id=validated_data.get('wave_id'),
        fe_rac_nodes=validated_data.get('fe_rac_nodes'),
    )

    mappings_data = GetMappingsService.run(db_id=validated_data['db_id'])
    data = mappings_data[0] if mappings_data else {}

    return {'data': data}, 201


# @bp.route('/<int:db_id>', methods=['GET'])
# def get_mapping(mapping_id):
#     """Return mapping."""
#     # db_id = request.args['db_id', type=int]
#     # if not db_id:
#     #     raise ValidationError({'db_id': 'required'})
#     validated_data = DBIdSchema().load(request.args)
#     mappings_data = GetMappingsService.run(db_id=validated_data['db_id'])
#     return {'data': mappings_data[0]}, 200


@bp.route('/<int:mapping_id>/operations', methods=['GET'])
def get_mapping_operation(mapping_id):
    """Return operation's histories for specific mapping."""
    mapping_data = []
    query = (
        db.session.query(Mapping, OperationDetails, SourceDB)
        .join(OperationDetails)
        .join(SourceDB)
        .filter(Mapping.id == mapping_id)
    )

    for mapping, operation_details, source_db in query:
        mapping_data.append({
            'id': mapping.id,
            'db_id': mapping.db_id,
            'bms_id': mapping.bms_id,
            'wave_id': source_db.wave_id,
            'operation': operation_details.operation_type.value,
            'started_at': operation_details.started_at,
            'completed_at': operation_details.completed_at,
            'status': operation_details.status.value
        })

    return {'data': mapping_data}, 200


@bp.route('', methods=['DELETE'])
def delete_mapping():
    """Delete mapping."""
    db_id = request.args.get('db_id', type=int)
    if db_id:
        source_db = SourceDB.query.get_or_404(db_id)

        # check of any operation exists
        operation_exists = db.session.query(OperationDetails) \
            .join(Mapping) \
            .filter(Mapping.db_id == db_id) \
            .count()

        if operation_exists:
            return {'errors': MAPPING_IS_USED}, 400

        # clear config
        config = source_db.config
        if source_db.config:
            clear_bms_target_params(config)

        db.session.query(Mapping).filter(Mapping.db_id == db_id).delete()

        db.session.commit()

    return {}, 204


@bp.route('', methods=['PUT'])
def edit_mapping():
    """Update mapping."""
    validated_data = EditMappingSchema().load(request.json)

    db_id = validated_data['db_id']
    new_bms_ids = validated_data['bms_id']
    wave_id = validated_data.get('wave_id')
    fe_rac_nodes = validated_data.get('fe_rac_nodes')

    if does_db_have_operation(db_id):
        raise ValidationError({'db_id': [MAPPING_IS_USED]})

    EditMappingService.run(
        db_id=db_id,
        new_bms_ids=new_bms_ids,
        wave_id=wave_id,
        fe_rac_nodes=fe_rac_nodes
    )

    mappings_data = GetMappingsService.run(db_id=db_id)
    data = mappings_data[0] if mappings_data else {}

    return {'data': data}, 201
