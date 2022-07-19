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

from faker import Faker

from bms_app.models import Wave, db

from tests.factories import ProjectFactory, WaveFactory


fk = Faker()


def test_upd_duplicate_wave_name_in_different_projects(client):
    """Test wave update with duplicate name from another project.

    Wave name is unique only within one porject."""
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    wave_1 = WaveFactory(project=pr_1)
    wave_2 = WaveFactory(project=pr_2)

    edit_wave_data = {
        'name': wave_1.name,
        'project_id': pr_2.id,
    }

    req = client.put(f'/api/waves/{wave_2.id}', json=edit_wave_data)

    assert req.status_code == 200


def test_edit_wave_update_the_same_name(client):
    """Test that edit wave with the same name works."""
    wave_1 = WaveFactory()

    edit_wave_data = {
        'name': wave_1.name,
        'project_id': wave_1.project.id,
    }

    req = client.put(f'/api/waves/{wave_1.id}', json=edit_wave_data)

    assert req.status_code == 200


def test_edit_a_project(client):
    wave_1 = WaveFactory.create()
    edit_wave_data = {
        'name': fk.word(),
        'project_id': wave_1.project.id,
    }

    req = client.put(f'/api/waves/{wave_1.id}', json=edit_wave_data)

    assert req.status_code == 200
    assert req.json
    assert isinstance(req.json, dict)

    db_wave = db.session.query(Wave).get(wave_1.id)

    assert db_wave.name == edit_wave_data['name']


def test_do_not_edit_wave_project(client):
    """Test that project can not be changed."""
    pr1 = ProjectFactory()
    pr2 = ProjectFactory()
    wave_1 = WaveFactory.create(project=pr1)

    edit_wave_data = {
        'name': fk.word(),
        'project_id': pr2.id,
    }

    req = client.put(f'/api/waves/{wave_1.id}', json=edit_wave_data)

    assert req.status_code == 200
    assert req.json
    assert isinstance(req.json, dict)

    db_wave = db.session.query(Wave).get(wave_1.id)

    assert db_wave.project_id == pr1.id


def test_unique_name_edit_err_within_the_project(client):
    """Test wave name duplicate err in the same project."""
    pr = ProjectFactory()
    wave_1 = WaveFactory(project=pr)
    wave_2 = WaveFactory(project=pr)

    edit_wave_data = {
        'name': wave_2.name,
        'project_id': wave_1.project.id,
    }

    req = client.put(f'/api/waves/{wave_1.id}', json=edit_wave_data)

    assert req.status_code == 400
