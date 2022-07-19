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

import json

from flask import request
from marshmallow import ValidationError
from sqlalchemy import or_

from bms_app import settings
from bms_app.inventory_manager import bp
from bms_app.inventory_manager.bms_api import fetch_bms_instances
from bms_app.inventory_manager.schema import BMSServerSchema
from bms_app.inventory_manager.services import (
    insert_discovered_servers, insert_uploaded_servers
)
from bms_app.models import BMSServer, Mapping, SourceDB, db
from bms_app.schema import FileSchema
from bms_app.utils import update_object


@bp.route('', methods=['GET'])
def servers_list():
    """Return all available bms targets.

    possible filters (sql 'or' condition):
    project_id - servers mapped to source db from specific project
    unmapped - servers that are not mapped
    """
    qs = db.session.query(BMSServer).filter(BMSServer.deleted.is_(False))

    project_id = request.args.get('project_id')
    unmapped = request.args.get('unmapped')

    qf = []
    if project_id:
        qf.append((SourceDB.project_id == project_id))
    if unmapped:
        qf.append((SourceDB.project_id.is_(None)))

    if qf:
        qs = qs.outerjoin(Mapping) \
            .outerjoin(SourceDB, Mapping.db_id == SourceDB.id) \
            .filter(or_(*qf))

    return {
        'data': BMSServerSchema(
            only=['id', 'name', 'cpu', 'socket', 'ram', 'secret_name', 'client_ip',
                  'created_at', 'location'],
            many=True
            ).dump(qs.all())
        }


@bp.route('/<int:server_id>', methods=['GET'])
def server(server_id):
    """Return server."""
    bms_server = BMSServer.query.get_or_404(server_id)
    return BMSServerSchema().dump(bms_server)


@bp.route('/<int:server_id>', methods=['DELETE'])
def server_delete(server_id):
    """Delete server."""
    bms_server = BMSServer.query.get_or_404(server_id)
    db.session.delete(bms_server)
    db.session.commit()
    return {}, 204


@bp.route('/<int:server_id>', methods=['PUT'])
def server_edit(server_id):
    """Update server."""
    validated_data = BMSServerSchema(only=['secret_name']).load(request.json)
    bms_server = BMSServer.query.get_or_404(server_id)

    update_object(bms_server, validated_data)

    db.session.add(bms_server)
    db.session.commit()

    return BMSServerSchema().dump(bms_server)


@bp.route('/discovery', methods=['POST'])
def discover_bms_servers():
    overwrite = request.form.get(
        'overwrite',
        default=False,
        type=lambda v: v.lower() == 'true'
    )

    discovered_instances = fetch_bms_instances(settings.GCP_PROJECT_NAME)
    insert_discovered_servers(discovered_instances, overwrite)

    return {}, 201


@bp.route('/upload', methods=['POST'])
def upload_servers():
    validated_files = FileSchema().load(request.files)
    data = validated_files['file'].read()
    try:
        uploaded_instances = json.loads(data)
    except json.decoder.JSONDecodeError:
        raise ValidationError({'file': ['incorrect json format']})

    overwrite = request.form.get(
        'overwrite',
        False,
        type=lambda v: v.lower() == 'true'
    )

    insert_uploaded_servers(uploaded_instances, overwrite)

    return {}, 201
