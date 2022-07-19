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

from flask import abort, request
from marshmallow import ValidationError

from bms_app.models import SourceDB
from bms_app.restore import bp
from bms_app.restore.schema import (
    RestoreConfigOutputSchema, RestoreConfigSchema
)
from bms_app.restore.services import (
    CreateOrUpdateRestoreConfig, DeleteConfigFileService,
    SaveConfigFileService, merge_validations
)
from bms_app.schema import BinaryFileSchema, TextFileSchema
from bms_app.services.gcs import create_file_link
from bms_app.services.restore_config import get_pfile_content


FILES_MAP = {
    'pfile': {
        'file_name': 'pfile.ora',
        'field_name': 'pfile_file',
        'schema': TextFileSchema,
    },
    'pwd_file': {
        'file_name': 'pwd_file.ora',
        'field_name': 'pwd_file',
        'schema': BinaryFileSchema,
    },
    'tnsnames_file': {
        'file_name': 'tnsnames_file.ora',
        'field_name': 'tnsnames_file',
        'schema': TextFileSchema,
    },
    'listener_file': {
        'file_name': 'listener_file.ora',
        'field_name': 'listener_file',
        'schema': TextFileSchema,
    },
}


@bp.route('/source-dbs/<int:db_id>/config', methods=['GET'])
def get_restore_configs(db_id):
    """Return restore-configs."""
    source_db = SourceDB.query.get_or_404(db_id)

    config = source_db.config

    if not config:
        raise ValidationError({None: ['db config does not exist']})

    restore_config = source_db.restore_config

    response = {
        'db_name': config.db_params_values['db_name'],
    }

    if restore_config:
        if restore_config.pfile_file:
            pfile_content = get_pfile_content(restore_config)
        else:
            pfile_content = ''

        response['pfile_content'] = pfile_content
        response.update(
            RestoreConfigOutputSchema().dump(restore_config)
        )

    response['validations'] = merge_validations(response.get('validations'))

    return response, 200


@bp.route('/source-dbs/<int:db_id>/config', methods=['POST'])
def new_restore_configs(db_id):
    """Create/Update db restore_configs."""
    source_db = SourceDB.query.get_or_404(db_id)

    validated_data = RestoreConfigSchema().load(request.json)

    CreateOrUpdateRestoreConfig.run(source_db, validated_data)

    return {}, 201


@bp.route('/source-dbs/<int:db_id>/config/pfile', methods=['POST'])
def save_pfile_file(db_id):
    """Save pfile file to bucket and it's link to db restore_configs."""
    validated_files = TextFileSchema().load(request.files)

    file_obj = validated_files['file']

    gcs_key = SaveConfigFileService.run(
        db_id,
        file_obj,
        file_name='pfile.ora',
        config_field_name='pfile_file'
    )

    file_obj.seek(0)

    data = {
        'url': create_file_link(gcs_key),
        'content': file_obj.read().decode()
    }
    return data, 201


@bp.route('/source-dbs/<int:db_id>/config/<fname>', methods=['POST'])
def upload_config_files(db_id, fname):
    """Upload restore config files."""
    if fname not in FILES_MAP:
        abort(404)

    schema_cls = FILES_MAP[fname]['schema']
    validated_files = schema_cls().load(request.files)

    file_obj = validated_files['file']

    gcs_key = SaveConfigFileService.run(
        db_id,
        file_obj,
        file_name=FILES_MAP[fname]['file_name'],
        config_field_name=FILES_MAP[fname]['field_name']
    )

    file_obj.seek(0)

    return {'url': create_file_link(gcs_key)}, 201


@bp.route('/source-dbs/<int:db_id>/config/<fname>', methods=['DELETE'])
def delete_config_file(db_id, fname):
    """Delete RestoreConfig files."""
    if fname not in FILES_MAP:
        abort(404)

    source_db = SourceDB.query.get_or_404(db_id)

    if source_db.restore_config:
        DeleteConfigFileService.run(
            source_db.restore_config,
            file_name=FILES_MAP[fname]['file_name'],
            config_field_name=FILES_MAP[fname]['field_name']
        )

    return {}, 204
