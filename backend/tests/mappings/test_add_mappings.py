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

from bms_app.models import Mapping, SourceDB

from tests.factories import (
    BMSServerFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


def test_add_single_mapping(client):
    """Test adding mapping with single instance"""
    pr = ProjectFactory()

    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    bms_1 = BMSServerFactory()
    wave = WaveFactory()

    add_mapping_data = {
        'db_id': db_1.id,
        'bms_id': [bms_1.id],
        'wave_id': wave.id,
        'fe_rac_nodes': 0
    }

    req = client.post('/api/mappings', json=add_mapping_data)

    assert req.status_code == 201
    assert 'data' in req.json

    mapping = Mapping.query.filter(Mapping.db_id == db_1.id).first()

    assert mapping
    assert mapping.bms_id == bms_1.id
    assert mapping.rac_node is None

    source_db_1 = SourceDB.query.get(db_1.id)
    assert source_db_1.wave_id == wave.id

    data = req.json['data']
    assert data == {
        'bms': [{'id': bms_1.id, 'name': bms_1.name}],
        'db_id': db_1.id,
        'db_name': db_1.db_name,
        'db_type': db_1.db_type.value,
        'fe_rac_nodes': add_mapping_data['fe_rac_nodes'],
        'id': mapping.id,
        'is_rac': db_1.is_rac,
        'oracle_version': db_1.oracle_version,
        'oracle_release': db_1.oracle_release,
        'source_hostname': db_1.server,
        'wave_id': wave.id,
        'is_configured': False,
        'labels': [],
        'is_deployed': True,
        'editable': True,
    }


def test_add_single_mapping_no_wave(client):
    """Test adding mapping with single instance"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    bms_1 = BMSServerFactory()

    add_mapping_data = {
        'db_id': db_1.id,
        'bms_id': [bms_1.id],
        'fe_rac_nodes': 0
    }

    req = client.post('/api/mappings', json=add_mapping_data)

    assert req.status_code == 201
    assert 'data' in req.json

    mapping = Mapping.query.filter(Mapping.db_id == db_1.id).first()

    assert mapping
    assert mapping.bms_id == bms_1.id
    assert mapping.rac_node is None

    data = req.json['data']
    assert data == {
        'bms': [{'id': bms_1.id, 'name': bms_1.name}],
        'db_id': db_1.id,
        'db_name': db_1.db_name,
        'db_type': db_1.db_type.value,
        'fe_rac_nodes': add_mapping_data['fe_rac_nodes'],
        'id': mapping.id,
        'is_rac': db_1.is_rac,
        'oracle_version': db_1.oracle_version,
        'oracle_release': db_1.oracle_release,
        'source_hostname': db_1.server,
        'wave_id': None,
        'is_configured': False,
        'labels': [],
        'is_deployed': True,
        'editable': True,
    }


def test_add_rac_mapping(client):
    """Test adding mapping"""
    pr = ProjectFactory()

    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    wave = WaveFactory()

    add_mapping_data = {
        'db_id': db_1.id,
        'bms_id': [bms_1.id, bms_2.id],
        'wave_id': wave.id,
        'fe_rac_nodes': 0
    }

    req = client.post('/api/mappings', json=add_mapping_data)

    assert req.status_code == 201
    assert 'data' in req.json

    mapping = Mapping.query.filter(Mapping.db_id == db_1.id).first()
    assert mapping

    assert mapping.rac_node is None

    source_db_1 = SourceDB.query.get(db_1.id)
    assert source_db_1.wave_id == wave.id

    data = req.json['data']
    assert data == {
        'bms': [
            {'id': bms_1.id, 'name': bms_1.name},
            {'id': bms_2.id, 'name': bms_2.name}
        ],
        'db_id': db_1.id,
        'db_name': db_1.db_name,
        'db_type': db_1.db_type.value,
        'fe_rac_nodes': add_mapping_data['fe_rac_nodes'],
        'id': mapping.id,
        'is_rac': db_1.is_rac,
        'oracle_version': db_1.oracle_version,
        'oracle_release': db_1.oracle_release,
        'source_hostname': db_1.server,
        'wave_id': wave.id,
        'is_configured': False,
        'labels': [],
        'is_deployed': True,
        'editable': True,
    }
