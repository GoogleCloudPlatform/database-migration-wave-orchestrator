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


def test_create_and_assign_label(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)

    req = client.post(
        f'/api/source-dbs/{db_1.id}/labels',
        json={'name': 'dev'}
    )

    label = db.session.query(Label) \
        .filter(Label.name == 'dev', Label.project_id == pr.id) \
        .first()

    assert req.status_code == 201
    assert req.json == {
        'id': label.id,
        'name': label.name,
        'project_id': pr.id,
    }

    assert len(db_1.labels) == 1

    assert label
    assert len(label.source_dbs) == 1


def test_assign_existing_label(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    label = LabelFactory(project=pr)

    req = client.post(
        f'/api/source-dbs/{db_1.id}/labels',
        json={'name': label.name}
    )

    assert req.status_code == 201
    assert req.json == {
        'id': label.id,
        'name': label.name,
        'project_id': pr.id,
    }

    assert len(db_1.labels) == 1
    assert len(label.source_dbs) == 1

    assert db.session.query(Label).count() == 1


def test_too_long_label_name(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)

    req = client.post(
        f'/api/source-dbs/{db_1.id}/labels',
        json={'name': 'x' * 16}
    )

    assert req.status_code == 400
    assert not db.session.query(Label).count()


def test_unassign_label(client):
    pr = ProjectFactory()
    label_1 = LabelFactory(project=pr)
    label_2 = LabelFactory(project=pr)

    db_1 = SourceDBFactory(project=pr)
    db_1.labels.append(label_1)
    db_1.labels.append(label_2)

    req = client.delete(f'/api/source-dbs/{db_1.id}/labels/{label_1.id}')

    assert req.status_code == 204

    assert db_1.labels == [label_2]

    assert db.session.query(Label).get(label_1.id)

    assert label_2.source_dbs == [db_1]
    assert not label_1.source_dbs
