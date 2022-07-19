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

from tests.factories import (
    BMSServerFactory, ConfigFactory, LabelFactory, MappingFactory,
    OperationDetailsFactory, OperationFactory, ProjectFactory, SourceDBFactory,
    WaveFactory
)


def test_get_all_mappings(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    db_2 = SourceDBFactory(project=pr, status='EMPTY')
    ConfigFactory(source_db=db_1, is_configured=True)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    bms_3 = BMSServerFactory()
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)  # single instance
    map_2 = MappingFactory(source_db=db_2, bms=bms_2, rac_node=2)  # RAC
    map_3 = MappingFactory(source_db=db_2, bms=bms_3, rac_node=1)  # RAC
    label_1 = LabelFactory(project=pr, source_dbs=[db_1, db_2])
    label_2 = LabelFactory(project=pr, source_dbs=[db_1])

    OperationDetailsFactory(mapping=map_1)

    req = client.get('/api/mappings')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 2

    assert {
        'id': map_1.id,
        'db_id': db_1.id,
        'bms': [
            {
                'id': bms_1.id,
                'name': bms_1.name
            }
        ],
        'wave_id': db_1.wave_id,
        'source_hostname': db_1.server,
        'db_name': db_1.db_name,
        'oracle_version': db_1.oracle_version,
        'oracle_release': db_1.oracle_release,
        'db_type': db_1.db_type.value,
        'is_rac': db_1.is_rac,
        'fe_rac_nodes': db_1.fe_rac_nodes,
        'is_configured': True,
        'labels': [
            {
                'id': label_1.id,
                'name': label_1.name
            },
            {
                'id': label_2.id,
                'name': label_2.name
            }
        ],
        'is_deployed': True,
        'editable': False,
    } in data

    # rac
    assert {
        'id': map_3.id,
        'db_id': db_2.id,
        'bms': [
            {
                'id': bms_3.id,
                'name': bms_3.name
            },
            {
                'id': bms_2.id,
                'name': bms_2.name
            },
        ],
        'wave_id': db_2.wave_id,
        'source_hostname': db_2.server,
        'db_name': db_2.db_name,
        'oracle_version': db_2.oracle_version,
        'oracle_release': db_2.oracle_release,
        'db_type': db_2.db_type.value,
        'is_rac': db_2.is_rac,
        'fe_rac_nodes': db_2.fe_rac_nodes,
        'is_configured': False,
        'labels': [
            {
                'id': label_1.id,
                'name': label_1.name
            }
        ],
        'is_deployed': False,
        'editable': True,
    } in data


def test_filter_mappings_by_project(client):
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    db_1 = SourceDBFactory(project=pr_1)
    db_2 = SourceDBFactory(project=pr_2)
    MappingFactory(source_db=db_1, bms=BMSServerFactory())
    MappingFactory(source_db=db_2, bms=BMSServerFactory())

    req = client.get(f'/api/mappings?project_id={pr_2.id}')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 1

    assert data[0]['db_id'] == db_2.id


def test_filter_mappings_by_db(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    db_2 = SourceDBFactory(project=pr)
    MappingFactory(source_db=db_1, bms=BMSServerFactory())
    MappingFactory(source_db=db_2, bms=BMSServerFactory())

    req = client.get(f'/api/mappings?db_id={db_1.id}')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 1

    assert data[0]['db_id'] == db_1.id


def test_filter_mappings_by_project_and_db(client):
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    db_11 = SourceDBFactory(project=pr_1)
    db_12 = SourceDBFactory(project=pr_1)
    db_21 = SourceDBFactory(project=pr_2)
    db_22 = SourceDBFactory(project=pr_2)
    MappingFactory(source_db=db_11)
    MappingFactory(source_db=db_12)
    MappingFactory(source_db=db_21)
    MappingFactory(source_db=db_22)

    req = client.get(f'/api/mappings?project_id={pr_2.id}&db_id={db_22.id}')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 1

    assert data[0]['db_id'] == db_22.id


def test_get_operations_details_for_mapping(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    m_1 = MappingFactory(source_db=db_1)

    op = OperationFactory(wave_id=wave.id)
    op_detail_1 = OperationDetailsFactory(
        operation=op,
        mapping=m_1,
        wave=wave,
        completed_at=factory.Faker('date_object')
    )
    op_detail_2 = OperationDetailsFactory(
        operation=op,
        mapping=m_1,
        wave=wave,
        completed_at=factory.Faker('date_object')
    )

    req = client.get(f'/api/mappings/{m_1.id}/operations')

    assert req.status_code == 200
    response = req.json

    assert response
    assert isinstance(response, dict)
    assert len(response['data']) == 2

    assert {
        'id': m_1.id,
        'db_id': m_1.db_id,
        'bms_id': m_1.bms_id,
        'wave_id': db_1.wave_id,
        'operation': op_detail_1.operation_type.value,
        'started_at': op_detail_1.started_at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'completed_at': op_detail_1.completed_at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'status': op_detail_1.status.value
    } in response['data']

    assert {
        'id': m_1.id,
        'db_id': m_1.db_id,
        'bms_id': m_1.bms_id,
        'wave_id': db_1.wave_id,
        'operation': op_detail_2.operation_type.value,
        'started_at': op_detail_2.started_at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'completed_at': op_detail_2.completed_at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'status': op_detail_2.status.value
    } in response['data']
