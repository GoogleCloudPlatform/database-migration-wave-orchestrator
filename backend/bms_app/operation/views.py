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

from flask import jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from bms_app.models import Operation, OperationDetails, OperationType, Wave, db
from bms_app.operation import bp
from bms_app.services.operations.restore import (
    FailOverOperation, PreRestoreOperation, RestoreOperation,
    RollbackRestoreOperation
)
from bms_app.services.rman import RmanLogFileParser
from bms_app.services.scheduled_tasks import (
    delete_planned_task, get_planned_task
)

from .schema import SourceDBIdSchema


@bp.route('', methods=['GET'])
def get_deployment_operations():
    """Return only deployed operations."""
    total_mappings = db.session.query(Operation.id, func.count()) \
        .join(OperationDetails, Operation.id == OperationDetails.operation_id) \
        .filter(Operation.operation_type == OperationType.DEPLOYMENT) \
        .group_by(Operation.id) \
        .all()
    total_mappings = dict(total_mappings)

    query = db.session.query(Wave, Operation) \
        .join(Operation, Wave.id == Operation.wave_id) \
        .filter(Operation.operation_type == OperationType.DEPLOYMENT)

    # Return only deployed operations for particular project
    project_id = request.args.get('project_id', type=int)
    if project_id:
        query = query.filter(Wave.project_id == project_id)

    deployments = query.all()

    data = []
    for row in deployments:
        data.append({
            'wave_id': row.Wave.id,
            'wave_name': row.Wave.name,
            'id': row.Operation.id,
            'started_at': row.Operation.started_at,
            'completed_at': row.Operation.completed_at,
            'status': row.Operation.status.value,
            'mappings_count': total_mappings.get(row.Operation.id, 0),
        })

    return {
        'data': data
    }


@bp.route('/pre-restores', methods=['POST'])
def pre_restore():
    validated_data = SourceDBIdSchema().load(request.json)

    PreRestoreOperation().run(db_id=validated_data['db_id'])

    return {}, 201


@bp.route('/restores', methods=['POST'])
def restore():
    """Start RESTORE operation."""
    validated_data = SourceDBIdSchema().load(request.json)

    # delete scheduled task if exists
    task = get_planned_task(validated_data['db_id'])
    if task:
        delete_planned_task(task)

    RestoreOperation().run(db_id=validated_data['db_id'])

    return {}, 201


@bp.route('/rollback-restores', methods=['POST'])
def rollback_restore():
    validated_data = SourceDBIdSchema().load(request.json)

    RollbackRestoreOperation().run(db_id=validated_data['db_id'])

    return {}, 201


@bp.route('/dt-failover', methods=['POST'])
def fail_over_restore():
    """Start FailOver operation."""
    validated_data = SourceDBIdSchema().load(request.json)

    FailOverOperation().run(db_id=validated_data['db_id'])

    return {}, 201


@bp.route('/<int:operation_id>/errors', methods=['GET'])
def get_operation_errors(operation_id):
    """Return Pre-restore operation errors."""

    # Pre-restore operaiton is run only for one db
    # there is only one OperationDetails
    operaion_details = db.session.query(OperationDetails) \
        .options(joinedload(OperationDetails.errors)) \
        .filter(OperationDetails.operation_id == operation_id) \
        .first()

    data = []

    rman_parser = RmanLogFileParser(operaion_details.operation_id)

    for err in operaion_details.errors:
        if err.message.startswith('rman '):
            details = rman_parser.get_cmd_output(err.message)
        else:
            details = ''

        data.append({
            'name': err.message,
            'details': details
        })

    return jsonify(data)
