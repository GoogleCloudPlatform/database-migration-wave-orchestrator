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

import bms_app.wave.schema as schema

from http import HTTPStatus
from flask import request
from bms_app.wave.services import WaveService


@bp.route('', methods=['GET'])
def list_waves():
    project_id = request.args.get('project_id', type=int)

    return WaveService().list(project_id=project_id)


@bp.route('/<int:wave_id>', methods=['GET'])
def get_wave(wave_id):
    fetch_details = request.args.get('details', type=bool)
    
    return WaveService().get(id=wave_id, fetch_details=fetch_details)


@bp.route('/<int:wave_id>', methods=['DELETE'])
def delete_wave(wave_id):
    WaveService().delete(id=wave_id)

    return HTTPStatus.NO_CONTENT


@bp.route('/<int:wave_id>', methods=['PUT'])
def edit_wave(wave_id):
    update = schema.WaveUpdate().load(request.json)

    updated_wave = WaveService().update(id=wave_id, update=update)

    return updated_wave


@bp.route('', methods=['POST'])
def add_wave():
    """Add wave."""
    create = schema.WaveCreate.load(request.json)

    created_wave = WaveService().create(create=create)

    return created_wave
