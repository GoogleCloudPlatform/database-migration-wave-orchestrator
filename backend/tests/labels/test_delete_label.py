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

from bms_app.models import Label, db

from tests.factories import LabelFactory, ProjectFactory, SourceDBFactory


def test_delete(client):
    """Delete lables with assossiated source_dbs."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    label = LabelFactory(project=pr)
    db_1.labels.append(label)

    req = client.delete(f'api/labels/{label.id}')

    assert req.status_code == 204

    assert not db.session.query(Label).count()
    assert not db_1.labels


def test_404(client):
    """Delete incorrect label."""
    req = client.delete(f'api/labels/1')

    assert req.status_code == 404
