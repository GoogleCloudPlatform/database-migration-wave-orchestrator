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

from .factories import (
    BMSServerFactory, MappingFactory, ProjectFactory, SourceDBFactory,
    WaveFactory
)


def test_whole_wave_deployment(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    db_2 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    MappingFactory(source_db=db_1, bms=bms_1)
    MappingFactory(source_db=db_2, bms=bms_2)

    with patch('bms_app.services.operations.wave.DeploymentService.run') as mock:
        req = client.post(f'/api/waves/{wave.id}/deployment', json={})

        assert req.status_code == 201
        assert req.json == {}

        mock.assert_called_with(1, None)


def test_specific_db_deployment(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    db_2 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    MappingFactory(source_db=db_1, bms=bms_1)
    MappingFactory(source_db=db_2, bms=bms_2)

    with patch('bms_app.services.operations.wave.DeploymentService.run') as mock:
        req = client.post(f'/api/waves/{wave.id}/deployment',
                          json={'db_ids': [db_1.id]})

        assert req.status_code == 201
        assert req.json == {}

        mock.assert_called_with(1, [db_1.id])
