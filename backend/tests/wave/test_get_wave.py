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

from tests.factories import (
    OperationDetailsFactory, OperationFactory, ProjectFactory, WaveFactory
)


def test_get_all_waves(client):
    pr = ProjectFactory()
    wave_1 = WaveFactory(project=pr)
    wave_2 = WaveFactory(project=pr)
    req = client.get('/api/waves')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 2

    assert {
        'id': wave_1.id,
        'name': wave_1.name,
        'project_id': wave_1.project_id,
        'is_running': False,
        'status_rate': {
            'undeployed': 0,
            'deployed': 0,
            'failed': 0
        }
    } in data

    assert {
        'id': wave_2.id,
        'name': wave_2.name,
        'project_id': wave_2.project_id,
        'is_running': False,
        'status_rate': {
            'undeployed': 0,
            'deployed': 0,
            'failed': 0
        }
    } in data


def test_filter_waves_by_project_id(client):
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1)
    wave_2 = WaveFactory(project=pr_2)

    req = client.get(f'/api/waves?project_id={pr_1.id}')

    assert req.status_code == 200
    data = req.json.get('data')

    assert data
    assert isinstance(data, list)
    assert len(data) == 1

    assert data[0]['id'] == wave_1.id


def test_get_a_wave(client):
    pr = ProjectFactory()
    wave_1 = WaveFactory.create(project=pr)
    WaveFactory.create()

    req = client.get(f'/api/waves/{wave_1.id}')

    assert req.status_code == 200
    data = req.json

    assert data
    assert isinstance(data, dict)
    assert data == {
        'id': wave_1.id,
        'name': wave_1.name,
        'project_id': wave_1.project_id,
        'is_running': False,
        'status_rate': {
            'undeployed': 0,
            'deployed': 0,
            'failed': 0
        }
    }


def test_step_data_if_running_wave(client):
    """Step data is present if wave is runnig."""
    wave = WaveFactory.create(is_running=True)
    op = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, operation=op)

    req = client.get('/api/waves')

    assert req.status_code == 200
    data = req.json.get('data')
    step_data = data[0].get('step')
    assert step_data == {'curr_step': 1, 'total_steps': 5}
