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

from bms_app.models import Project, db
from bms_app.project import bp
from bms_app.project.services import (
    DeleteProjectService, validate_name_is_unique
)
from bms_app.schema import ProjectSchema


@bp.route('', methods=['GET'])
def list_projects():
    """Return all available projects."""
    all_projects = Project.query.all()
    return {
        'data': ProjectSchema(many=True).dump(all_projects)
    }


@bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Return project."""
    project = Project.query.get_or_404(project_id)
    return ProjectSchema().dump(project)


@bp.route('', methods=['POST'])
def add_project():
    """Add project."""
    validated_data = ProjectSchema(exclude=['id']).load(request.json)

    validate_name_is_unique(validated_data['name'])

    project = Project(
        name=validated_data['name'],
        vpc=validated_data['vpc'],
        subnet=validated_data['subnet'],
        description=validated_data['description']
    )
    db.session.add(project)
    db.session.commit()

    return ProjectSchema().dump(project), 201


@bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete project."""
    force = request.args.get(
        'force',
        default=False,
        type=lambda v: v.lower() == 'true'
    )
    srv = DeleteProjectService(project_id, force)

    if srv.can_be_deleted():
        srv.delete()
    else:
        return {'errors': 'PROJECT_IS_NOT_EMPTY'}, 400

    return {}, 204


@bp.route('/<int:project_id>', methods=['PUT'])
def edit_project(project_id):
    """Update project."""
    validated_data = ProjectSchema(exclude=['id']).load(request.json)
    project = Project.query.get_or_404(project_id)

    validate_name_is_unique(
        validated_data['name'],
        exclude_project_id=project_id
    )

    project.name = validated_data['name']
    project.vpc = validated_data['vpc']
    project.subnet = validated_data['subnet']
    project.description = validated_data['description']

    db.session.add(project)
    db.session.commit()

    return ProjectSchema().dump(project)
