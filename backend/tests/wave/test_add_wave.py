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

from bms_app.models import SourceDBType, Wave, db

from tests.factories import (
    MappingFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


def test_add_wave_without_db_assigment(client):
    """Test adding new wave"""
    pr = ProjectFactory()

    add_wave_data = {
        'name': 'wave-1',
        'project_id': pr.id,
    }

    req = client.post('/api/waves', json=add_wave_data)
    assert req.status_code == 201

    assert db.session.query(Wave).filter(
        Wave.name == add_wave_data['name'],
        Wave.project_id == add_wave_data['project_id']
    ).first()


def test_add_new_wave_with_db_assignment(client):
    """Test adding new wave"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='EMPTY')
    db_2 = SourceDBFactory(project=pr, status='EMPTY')
    MappingFactory(source_db=db_1)
    MappingFactory(source_db=db_2)

    add_wave_data = {
        'name': 'wave-1',
        'project_id': pr.id,
        'db_ids': [db_1.id, db_2.id]
    }

    req = client.post('/api/waves', json=add_wave_data)
    assert req.status_code == 201

    wave = db.session.query(Wave).filter(
        Wave.name == add_wave_data['name'],
        Wave.project_id == add_wave_data['project_id']
    ).first()

    assert wave

    assert db_1.wave is wave
    assert db_2.wave is wave

    assert req.json == {'assigned': 2, 'skipped': 0, 'unmapped': 0}


def test_add_existing_wave_and_assign_db(client):
    """Test adding existing wave and assign db"""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr, is_running=False)
    db_1 = SourceDBFactory(project=pr, status='EMPTY')
    db_2 = SourceDBFactory(project=pr, status='EMPTY')
    MappingFactory(source_db=db_1)
    MappingFactory(source_db=db_2)

    add_wave_data = {
        'name': wave.name,
        'project_id': wave.project_id,
        'db_ids': [db_1.id, db_2.id]
    }

    req = client.post('/api/waves', json=add_wave_data)
    assert req.status_code == 201

    assert db_1.wave == wave
    assert db_2.wave == wave

    assert db.session.query(Wave).count() == 1

    assert req.json == {'assigned': 2, 'skipped': 0, 'unmapped': 0}


def test_reassign_db(client):
    """Test adding existing wave and reassigning db"""
    pr = ProjectFactory()
    wave_1 = WaveFactory(project=pr, is_running=False)
    db_1 = SourceDBFactory(project=pr, status='EMPTY', wave=wave_1)
    db_2 = SourceDBFactory(project=pr, status='EMPTY', wave=wave_1)
    MappingFactory(source_db=db_1)
    MappingFactory(source_db=db_2)

    add_wave_data = {
        'name': 'new_wave',
        'project_id': pr.id,
        'db_ids': [db_1.id, db_2.id]
    }

    req = client.post('/api/waves', json=add_wave_data)
    assert req.status_code == 201

    new_wave = db.session.query(Wave) \
        .filter(Wave.name == 'new_wave', Wave.project_id == pr.id) \
        .first()

    assert new_wave

    assert db_1.wave_id == new_wave.id
    assert db_2.wave_id == new_wave.id

    assert req.json == {'assigned': 2, 'skipped': 0, 'unmapped': 0}


def test_assigned_skipped_unmapped_db(client):
    pr = ProjectFactory()
    wave_1 = WaveFactory(project=pr, is_running=False)
    db_1 = SourceDBFactory(
        project=pr,
        status='EMPTY',
        wave=wave_1,
        db_type=SourceDBType.RAC
    )
    db_2 = SourceDBFactory(
        project=pr,
        status='EMPTY',
        wave=wave_1
    )
    db_3 = SourceDBFactory(
        project=pr,
        status='DEPLOYED',
        wave=wave_1
    )
    MappingFactory(source_db=db_1)
    MappingFactory(source_db=db_1)
    MappingFactory(source_db=db_3)

    add_wave_data = {
        'name': 'new_wave',
        'project_id': pr.id,
        'db_ids': [db_1.id, db_2.id, db_3.id]
    }

    req = client.post('/api/waves', json=add_wave_data)
    assert req.status_code == 201

    new_wave = db.session.query(Wave) \
        .filter(Wave.name == 'new_wave') \
        .first()

    assert new_wave

    assert new_wave.name == add_wave_data['name']
    assert new_wave.project_id == add_wave_data['project_id']

    assert db_1.wave_id == new_wave.id
    assert db_2.wave_id != new_wave.id
    assert db_3.wave_id != new_wave.id

    assert req.json == {'assigned': 1, 'skipped': 1, 'unmapped': 1}


def test_add_wave_error(client):
    req = client.post('/api/waves', json={})
    assert req.status_code == 400

    assert 'name' in req.json['errors']
    assert 'project_id' in req.json['errors']
