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

from bms_app.models import OperationStatus, OperationType

from .factories import (
    BMSServerFactory, MappingFactory, OperationDetailsFactory,
    OperationFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


DATE_FMT = '%a, %d %b %Y %H:%M:%S GMT'


@patch('bms_app.source_db.services.generate_target_gcp_logs_link', return_value='logs_url')
def test_source_db_operations_history(mock, client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    db_1 = SourceDBFactory(wave=wave, project=pr)
    mapp_1 = MappingFactory(source_db=db_1, bms=bms_1)
    mapp_2 = MappingFactory(source_db=db_1, bms=bms_2)
    op_1 = OperationFactory(
        wave=wave,
        started_at=datetime(2022, 1, 10, 14, 10),
        completed_at=datetime(2022, 1, 10, 15, 20),
    )
    op_h_1 = OperationDetailsFactory(
        operation=op_1,
        mapping=mapp_1,
        wave=wave,
        status=OperationStatus.COMPLETE,
        operation_type=OperationType.DEPLOYMENT,
    )
    op_h_2 = OperationDetailsFactory(
        operation=op_1,
        mapping=mapp_2,
        wave=wave,
    )

    # another db that should be filtered out
    bms_3 = BMSServerFactory()
    db_3 = SourceDBFactory(wave=wave, project=pr)
    mapp_3 = MappingFactory(source_db=db_3, bms=bms_3)
    OperationDetailsFactory(mapping=mapp_3, wave=wave)

    req = client.get(f'/api/source-dbs/{db_1.id}/operations_history')

    assert req.status_code == 200

    assert req.json == {
        'id': db_1.id,
        'source_hostname': db_1.server,
        'db_name': db_1.db_name,
        'oracle_version': db_1.oracle_version,
        'db_type': db_1.db_type.value,
        'operations': [
            {
                'wave_id': op_h_1.wave_id,
                'operation_type': op_h_1.operation_type.value,
                'started_at': op_1.started_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                'completed_at': op_1.completed_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                'bms': [
                    {
                        'id': bms_1.id,
                        'name': bms_1.name,
                        'logs_url': 'logs_url',
                        'operation_status': op_h_1.status.value
                    },
                    {
                        'id': bms_2.id,
                        'name': bms_2.name,
                        'logs_url': 'logs_url',
                        'operation_status': op_h_2.status.value
                    },
                ]
            }
        ]
    }
