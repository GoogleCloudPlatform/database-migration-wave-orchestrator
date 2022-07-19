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

def test_wave_steps(client):
    """Test wave-steps api.

    Although they are hardcoded it makes sense to check
    if changes are not accident
    """
    req = client.get('/api/metadata/wave-steps')

    assert req.status_code == 200

    data = req.json
    assert isinstance(data, dict)
    assert len(data) == 2

    deployment_steps = data.get('deployment')
    assert len(deployment_steps) == 5

    rollback_steps = data.get('rollback')
    assert len(rollback_steps) == 3

    for steps in deployment_steps, rollback_steps:
        assert all([set(item.keys()) == {'id', 'name', 'description'}
                    for item in steps])
        assert all([isinstance(item['description'], str) for item in steps])
        assert all([isinstance(item['id'], str) for item in steps])
        assert all([isinstance(item['name'], str) for item in steps])
