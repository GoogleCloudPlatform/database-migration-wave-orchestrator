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

from bms_app.labels import bp
from bms_app.models import Label, db
from bms_app.schema import LabelSchema, ProjectIdSchema


@bp.route('', methods=['GET'])
def list_labels():
    validated_data = ProjectIdSchema().load(request.args)

    labels = db.session.query(Label) \
        .filter(Label.project_id == validated_data['project_id']) \
        .all()

    return {'data': LabelSchema(many=True).dump(labels)}


@bp.route('<int:label_id>', methods=['DELETE'])
def delete_label(label_id):
    label = Label.query.get_or_404(label_id)
    db.session.delete(label)
    db.session.commit()

    return {}, 204


@bp.route('<int:label_id>', methods=['GET'])
def get_label(label_id):
    label = Label.query.get_or_404(label_id)

    data = LabelSchema().dump(label)

    if request.args.get('db_count'):
        data['db_count'] = len(label.source_dbs)

    return data


@bp.route('<int:label_id>', methods=['PUT'])
def edit_label(label_id):
    validated_data = LabelSchema(only=['name']).load(request.json)

    label = Label.query.get_or_404(label_id)
    label.name = validated_data['name']
    db.session.add(label)
    db.session.commit()

    return {}
