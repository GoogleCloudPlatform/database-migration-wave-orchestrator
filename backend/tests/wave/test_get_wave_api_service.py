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

from bms_app.wave.services.waves import GetWaveService

from tests.factories import (
    BMSServerFactory, MappingFactory, OperationDetailsFactory,
    OperationFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


@patch('bms_app.wave.services.waves.generate_target_gcp_logs_link')
def test_get_wave_api_service(mock, client):
    pr_1 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1, is_running=True)
    db_1 = SourceDBFactory(project=pr_1, wave=wave_1)
    bms_1 = BMSServerFactory()
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave_1)
    OperationDetailsFactory(
        mapping=map_1,
        wave=wave_1,
        operation=op_1,
    )

    data = GetWaveService.run(wave_1.id)

    assert data == {
        'id': wave_1.id,
        'is_running': True,
        'name': wave_1.name,
        'project_id': wave_1.project_id,
        'step': {
            'curr_step': 1,
            'total_steps': 5,
        },
        'status_rate': {
            'undeployed': 1,
            'deployed': 0,
            'failed': 0
        }
    }
