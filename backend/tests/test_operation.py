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

import factory

from bms_app.models import db

from .factories import (
    BMSServerFactory, MappingFactory, OperationDetailsFactory,
    OperationFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


def test_get_all_operations(client):
    pr_1 = ProjectFactory.create()
    wave_1 = WaveFactory.create(project=pr_1)
    db_1 = SourceDBFactory.create(project=pr_1, wave=wave_1)
    bms_1 = BMSServerFactory.create()
    map_1 = MappingFactory.create(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory.create(wave=wave_1,  completed_at=factory.Faker('date_object'))
    op_2 = OperationFactory.create(wave=wave_1, status='COMPLETE', completed_at=factory.Faker('date_object'))
    OperationDetailsFactory.create(
        mapping=map_1,
        wave=wave_1,
        operation=op_1,
    )
    OperationDetailsFactory.create(
        mapping=map_1,
        wave=wave_1,
        operation=op_1
    )
    OperationDetailsFactory.create(
        mapping=map_1,
        wave=wave_1,
        operation=op_1
    )
    db.session.commit()

    req = client.get('/api/operations')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 2

    assert {
        'id': op_1.id,
        'wave_id': op_1.wave.id,
        'wave_name': wave_1.name,
        'status': 'STARTING',
        'started_at': op_1.started_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        'completed_at': op_1.completed_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        'mappings_count': 3
    } in data

    assert {
        'id': op_2.id,
        'wave_id': op_2.wave.id,
        'wave_name': wave_1.name,
        'status': 'COMPLETE',
        'started_at': op_2.started_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        'completed_at': op_2.completed_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        'mappings_count': 0
    } in data
