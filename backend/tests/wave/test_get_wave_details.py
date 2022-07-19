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

from datetime import datetime
from unittest.mock import patch

from bms_app.wave.services.waves import LastOpWaveDetails, RunningWaveDetails

from tests.factories import (
    BMSServerFactory, ConfigFactory, MappingFactory, OperationDetailsFactory,
    OperationFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


@patch('bms_app.wave.services.waves.generate_target_gcp_logs_link', return_value='http')
def test_running_single_wave_details(mock, client):
    pr_1 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1, is_running=True)
    db_1 = SourceDBFactory(project=pr_1, wave=wave_1)
    config = ConfigFactory(source_db=db_1)
    bms_1 = BMSServerFactory()
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave_1)
    op_his_1 = OperationDetailsFactory(
        mapping=map_1,
        wave=wave_1,
        operation=op_1
    )

    wave_details = RunningWaveDetails(wave_1.id).get_extra_data()

    assert map_1.rac_node is 0

    assert wave_details == {
        'curr_operation': {
            'id': op_1.id,
            'completed_at': op_1.completed_at,
            'operation_type': op_1.operation_type.value,
            'started_at': op_1.started_at,
        },
        'mappings': [{
            'server': db_1.server,
            'db_id': db_1.id,
            'db_name': db_1.db_name,
            'db_type': db_1.db_type.value,
            'is_deployable': True,
            'operation_type': op_his_1.operation_type.value,
            'operation_status': op_1.status.value,
            'operation_id': op_his_1.operation_id,
            'is_configured': config.is_configured,
            'has_secret_name': True,
            'bms': [
                {
                    'id': bms_1.id,
                    'name': bms_1.name,
                    'operation_status': op_his_1.status.value,
                    'operation_step': op_his_1.step,
                    'logs_url': mock.return_value
                }
            ]
        }]
    }


def test_running_single_wave_details_db_deployable_status(client):
    pr_1 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1, is_running=True)
    db_1 = SourceDBFactory(project=pr_1, wave=wave_1, status='EMPTY')
    db_2 = SourceDBFactory(project=pr_1, wave=wave_1, status='DEPLOYED')
    db_3 = SourceDBFactory(project=pr_1, wave=wave_1, status='FAILED')
    db_4 = SourceDBFactory(project=pr_1, wave=wave_1, status='ROLLBACKED')
    bms_1 = BMSServerFactory()
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    map_2 = MappingFactory(source_db=db_2, bms=bms_1)
    map_3 = MappingFactory(source_db=db_3, bms=bms_1)
    map_4 = MappingFactory(source_db=db_4, bms=bms_1)
    op_1 = OperationFactory(wave=wave_1)
    OperationDetailsFactory(
        mapping=map_1,
        wave=wave_1,
        operation=op_1
    )
    OperationDetailsFactory(
        mapping=map_2,
        wave=wave_1,
        operation=op_1
    )
    OperationDetailsFactory(
        mapping=map_3,
        wave=wave_1,
        operation=op_1
    )
    OperationDetailsFactory(
        mapping=map_4,
        wave=wave_1,
        operation=op_1
    )

    req = client.get(f'/api/waves/{wave_1.id}?details=True')
    data = req.json

    assert data['mappings'][0]['is_deployable']
    assert not data['mappings'][1]['is_deployable']
    assert not data['mappings'][2]['is_deployable']
    assert data['mappings'][3]['is_deployable']
    assert data['mappings'][0]['is_configured'] is not None


@patch('bms_app.wave.services.waves.generate_target_gcp_logs_link', return_value='http')
def test_running_rac_wave_details(mock, client):
    pr_1 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1, is_running=True)
    db_1 = SourceDBFactory(project=pr_1, wave=wave_1)
    db_2 = SourceDBFactory(project=pr_1, wave=wave_1)
    config = ConfigFactory(source_db=db_1)
    config_2 = ConfigFactory(source_db=db_2)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory(secret_name=None)
    bms_3 = BMSServerFactory()
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=2)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=3)
    map_3 = MappingFactory(source_db=db_2, bms=bms_3, rac_node=2)
    op_1 = OperationFactory(wave=wave_1)
    # op_2 = OperationFactory(wave=wave_1)
    op_his_1 = OperationDetailsFactory(
        mapping=map_1,
        wave=wave_1,
        operation=op_1
    )
    op_his_2 = OperationDetailsFactory(
        mapping=map_2,
        wave=wave_1,
        operation=op_1
    )
    op_his_3 = OperationDetailsFactory(
        mapping=map_3,
        wave=wave_1,
        operation=op_1
    )

    wave_details = RunningWaveDetails(wave_1.id).get_extra_data()

    assert map_1.rac_node > 1

    assert wave_details == {
        'curr_operation': {
            'id': op_1.id,
            'completed_at': op_1.completed_at,
            'operation_type': op_1.operation_type.value,
            'started_at': op_1.started_at
        },
        'mappings': [{
            'server': db_1.server,
            'db_id': db_1.id,
            'db_name': db_1.db_name,
            'db_type': db_1.db_type.value,
            'is_deployable': True,
            'operation_type': op_his_1.operation_type.value,
            'operation_status': op_1.status.value,
            'operation_id': op_his_1.operation_id,
            'is_configured': config.is_configured,
            'has_secret_name': False,
            'bms': [
                {
                    'id': bms_1.id,
                    'name': bms_1.name,
                    'operation_status': op_his_1.status.value,
                    'operation_step': op_his_1.step,
                    'logs_url': mock.return_value
                },
                {
                    'id': bms_2.id,
                    'name': bms_2.name,
                    'operation_status': op_his_2.status.value,
                    'operation_step': op_his_2.step,
                    'logs_url': mock.return_value
                }
            ]
            },
            {
            'server': db_2.server,
            'db_id': db_2.id,
            'db_name': db_2.db_name,
            'db_type': db_2.db_type.value,
            'is_deployable': True,
            'operation_type': op_his_3.operation_type.value,
            'operation_status': op_1.status.value,
            'operation_id': op_his_3.operation_id,
            'is_configured': config_2.is_configured,
            'has_secret_name': True,
            'bms': [
                {
                    'id': bms_3.id,
                    'name': bms_3.name,
                    'operation_status': op_his_3.status.value,
                    'operation_step': op_his_3.step,
                    'logs_url': mock.return_value
                }
                ]
            }
        ]
    }


@patch('bms_app.wave.services.waves.generate_target_gcp_logs_link', return_value='http')
def test_not_running_wave_details(mock, client):
    """Test returning last mapping/operation data if present for each db."""
    pr_1 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1)
    db_1 = SourceDBFactory(project=pr_1, wave=wave_1)
    config_1 = ConfigFactory(source_db=db_1)
    bms_1 = BMSServerFactory()
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    # old operation for db_1
    OperationDetailsFactory(
        mapping=map_1,
        wave=wave_1,
        operation=OperationFactory(
            wave=wave_1,
            started_at=datetime(2022, 2, 5, 12, 10),
            completed_at=datetime(2022, 2, 5, 14, 20),
        )
    )
    # new operation for db_1
    op_1 = OperationFactory(
        wave=wave_1,
        started_at=datetime(2022, 2, 10, 12, 10),
        completed_at=datetime(2022, 2, 10, 14, 20),
    )
    op_his_1 = OperationDetailsFactory(
        mapping=map_1,
        wave=wave_1,
        operation=op_1
    )

    db_2 = SourceDBFactory(project=pr_1, wave=wave_1)
    config_2 = ConfigFactory(source_db=db_2)
    bms_2 = BMSServerFactory(secret_name=None)
    bms_3 = BMSServerFactory()
    map_2 = MappingFactory(source_db=db_2, bms=bms_2)
    map_3 = MappingFactory(source_db=db_2, bms=bms_3)

    wave_details = LastOpWaveDetails(wave_1.id).get_extra_data()

    assert wave_details['last_deployment'] == {
        'id': op_1.id,
        'completed_at': op_1.completed_at,
        'operation_type': op_1.operation_type.value,
        'started_at': op_1.started_at,
    }

    assert len(wave_details['mappings']) == 2

    assert [{
        'bms': [
            {
                'bms_id': bms_1.id,
                'bms_name': bms_1.name,
                'operation_status': op_his_1.status.value,
                'operation_step': op_his_1.step
            }
        ],
        'db_id': db_1.id,
        'db_name': db_1.db_name,
        'db_type': db_1.db_type.value,
        'is_deployable': True,
        'operation_type': op_his_1.operation_type.value,
        'operation_status': op_1.status.value,
        'operation_id': op_his_1.operation_id,
        'server': db_1.server,
        'is_configured': config_1.is_configured,
        'has_secret_name': True
        },
        {
        'bms': [
            {
                'bms_id': bms_2.id,
                'bms_name': bms_2.name,
                'operation_status': None,
                'operation_step': None
            },
            {
                'bms_id': bms_3.id,
                'bms_name': bms_3.name,
                'operation_status': None,
                'operation_step': None
            }
        ],
        'db_id': db_2.id,
        'db_name': db_2.db_name,
        'db_type': 'SI',
        'is_deployable': True,
        'operation_id': None,
        'operation_status': '',
        'operation_type': None,
        'server': db_2.server,
        'is_configured': config_2.is_configured,
        'has_secret_name': False
    }] == wave_details['mappings']
