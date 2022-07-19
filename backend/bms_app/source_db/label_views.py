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

from bms_app.models import Label, SourceDB, db
from bms_app.schema import LabelSchema
from bms_app.source_db import bp


@bp.route('<int:db_id>/labels', methods=['POST'])
def assign_label(db_id):
    validated_data = LabelSchema(only=['name']).load(request.json)

    source_db = SourceDB.query.get_or_404(db_id)

    label = db.session.query(Label)\
        .filter(
            Label.name == validated_data['name'],
            Label.project_id == source_db.project_id) \
        .first()

    if not label:
        label = Label(
            name=validated_data['name'],
            project_id=source_db.project_id
        )

    source_db.labels.append(label)

    db.session.commit()

    return LabelSchema(only=['id', 'name', 'project_id']).dump(label), 201


@bp.route('<int:db_id>/labels/<int:label_id>', methods=['DELETE'])
def unassign_label(db_id, label_id):
    source_db = SourceDB.query.get_or_404(db_id)

    label = db.session.query(Label)\
        .filter(
            Label.id == label_id,
            Label.project_id == source_db.project_id) \
        .first()

    if label and label in source_db.labels:
        source_db.labels.remove(label)
        db.session.commit()

    return {}, 204
