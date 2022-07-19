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

from tests.factories import LabelFactory, ProjectFactory


def test_list(client):
    proj_1 = ProjectFactory()
    proj_2 = ProjectFactory()

    label_1 = LabelFactory(project=proj_1)
    label_2 = LabelFactory(project=proj_1)
    LabelFactory(project=proj_2)

    req = client.get(f'api/labels?project_id={proj_1.id}')

    assert req.status_code == 200

    data = req.json.get('data')

    assert data
    assert isinstance(data, list)

    assert data == [
        {
            'id': label_1.id,
            'name': label_1.name,
            'project_id': label_1.project_id,
        },
        {
            'id': label_2.id,
            'name': label_2.name,
            'project_id': label_2.project_id,
        }
    ]


def test_list_requires_project_id(client):
    LabelFactory()

    req = client.get('api/labels')

    assert req.status_code == 400
