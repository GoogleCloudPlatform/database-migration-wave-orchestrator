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

from tests.factories import LabelFactory, ProjectFactory, SourceDBFactory


def test_get_label(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    db_2 = SourceDBFactory(project=pr)
    label = LabelFactory(project=pr)
    db_1.labels.append(label)
    db_2.labels.append(label)

    req = client.get(f'api/labels/{label.id}')

    assert req.status_code == 200

    assert req.json == {
        'id': label.id,
        'name': label.name,
        'project_id': pr.id,
    }


def test_get_label_with_db_count(client):
    """Test 'db_count' query arg."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    db_2 = SourceDBFactory(project=pr)
    label = LabelFactory(project=pr)
    db_1.labels.append(label)
    db_2.labels.append(label)

    req = client.get(f'api/labels/{label.id}?db_count=true')

    assert req.status_code == 200

    assert req.json == {
        'id': label.id,
        'name': label.name,
        'project_id': pr.id,
        'db_count': 2,
    }


def test_404(client):
    req = client.get(f'api/labels/1')

    assert req.status_code == 404
