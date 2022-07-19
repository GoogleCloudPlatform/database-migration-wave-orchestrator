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

from unittest.mock import patch

import factory

from tests.factories import (
    BMSServerFactory, MappingFactory, OperationDetailsFactory,
    OperationFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


@patch('bms_app.wave.views.generate_target_gcp_logs_link', return_value='log')
def test_get_operation_details(mock, client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory()
    m_1 = MappingFactory.create(source_db=db_1, bms=bms_1)
    op = OperationFactory(wave=wave)
    op_detail_1 = OperationDetailsFactory(
        operation=op,
        mapping=m_1,
        wave=wave,
        completed_at=factory.Faker('date_object')
    )

    req = client.get(f'/api/waves/{wave.id}/operations/{op.id}/details')

    assert req.status_code == 200
    data = req.json

    assert data
    assert isinstance(data, dict)

    assert data == {
        'data':
            [{
                'status': op_detail_1.status.value,
                'operation_id': op_detail_1.operation_id,
                'operation_type': op_detail_1.operation_type.value,
                'wave_id': op_detail_1.wave_id,

                'source_db': {
                    'source_hostname': db_1.server,
                    'db_name': db_1.db_name,
                    'db_type': db_1.db_type.value,
                    'is_rac': db_1.is_rac,
                    'oracle_version': db_1.oracle_version,
                },
                'bms': [{
                    'id': bms_1.id,
                    'name': bms_1.name,
                    'logs_url': mock.return_value,
                    'started_at': op_detail_1.started_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    'completed_at': op_detail_1.completed_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                    'step': op_detail_1.step,
                    'mapping_id': op_detail_1.mapping_id
                }],

            }]
    }


@patch('bms_app.wave.views.generate_target_gcp_logs_link', return_value='log')
def test_get_operation_details_rac(mock, client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    m_1 = MappingFactory.create(source_db=db_1, bms=bms_1)
    m_2 = MappingFactory.create(source_db=db_1, bms=bms_2)
    op = OperationFactory(wave=wave)
    op_detail_1 = OperationDetailsFactory(
        operation=op,
        mapping=m_1,
        wave=wave,
        completed_at=factory.Faker('date_object')
    )
    op_detail_2 = OperationDetailsFactory(
        operation=op,
        mapping=m_2,
        wave=wave,
        completed_at=factory.Faker('date_object')
    )

    req = client.get(f'/api/waves/{wave.id}/operations/{op.id}/details')

    assert req.status_code == 200
    data = req.json

    assert data
    assert isinstance(data, dict)

    assert data == {
        'data':
            [{
                'status': op_detail_1.status.value,
                'operation_id': op_detail_1.operation_id,
                'operation_type': op_detail_1.operation_type.value,
                'wave_id': op_detail_1.wave_id,

                'source_db': {
                    'source_hostname': db_1.server,
                    'db_name': db_1.db_name,
                    'db_type': db_1.db_type.value,
                    'is_rac': db_1.is_rac,
                    'oracle_version': db_1.oracle_version,
                },
                'bms': [
                    {
                        'id': bms_1.id,
                        'name': bms_1.name,
                        'logs_url': mock.return_value,
                        'started_at': op_detail_1.started_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        'completed_at': op_detail_1.completed_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        'step': op_detail_1.step,
                        'mapping_id': op_detail_1.mapping_id
                    },
                    {
                        'id': bms_2.id,
                        'name': bms_2.name,
                        'logs_url': mock.return_value,
                        'started_at': op_detail_2.started_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        'completed_at': op_detail_2.completed_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                        'step': op_detail_2.step,
                        'mapping_id': op_detail_2.mapping_id
                    },
                ]
            }]}
