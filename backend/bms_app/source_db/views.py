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
from http import HTTPStatus

from bms_app.models import SourceDB, db
from bms_app.schema import FileSchema, LabelSchema
from bms_app.source_db import bp
from bms_app.source_db.parsers import MigvisorFileError, MigvisorParser
from bms_app.source_db.schema import MigvisorFileUploadSchema, SourceDBSchema
from bms_app.source_db.services import save_source_dbs


@bp.route('', methods=['GET'])
def list_source_dbs():
    """Return all available source_dbs."""
    project_id = request.args.get('project_id', type=int)
    qf = {'project_id': project_id} if project_id else {}

    source_dbs = SourceDB.query.filter_by(**qf).all()

    data = SourceDBSchema(many=True).dump(source_dbs)

    return {
        'data': data
    }


@bp.route('/<int:source_db_id>', methods=['GET'])
def get_source_db(source_db_id):
    """Return source_db."""
    source_db = SourceDB.query.get_or_404(source_db_id)
    return SourceDBSchema().dump(source_db)


@bp.route('/<int:source_db_id>', methods=['DELETE'])
def delete_source_db(source_db_id):
    """Delete source_db."""
    source_db = SourceDB.query.get_or_404(source_db_id)
    db.session.delete(source_db)
    db.session.commit()
    return {}, 204

@bp.route('', methods=["POST"])
def create():
    source_db = SourceDBSchema().load(request.json)
    db.session.add(source_db)
    db.session.commit()
    db.session.flush()
    return SourceDBSchema().dump(source_db), HTTPStatus.CREATED


@bp.route('/migvisor', methods=['POST'])
def process_migvisor_assessment():
    """Generate new source_db based on uploaded files."""
    validated_form_data = MigvisorFileUploadSchema().load(request.form)
    validated_files = FileSchema().load(request.files)

    parser = MigvisorParser(validated_files['file'])

    try:
        parsed_dbs_data = parser.parse()
    except MigvisorFileError as exc:
        raise ValidationError({'file': str(exc)})

    upload_result = save_source_dbs(
        parsed_dbs_data,
        overwrite=validated_form_data['overwrite'],
        project_id=validated_form_data['project_id']
    )

    return upload_result, 201
