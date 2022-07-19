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

from bms_app.models import Mapping, db

from tests.factories import (
    BMSServerFactory, MappingFactory, ProjectFactory, SourceDBFactory,
    WaveFactory
)


def test_edit_single_db_mapping(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=None)
    MappingFactory(source_db=db_1, bms=BMSServerFactory())
    bms_1 = BMSServerFactory()

    edit_mapping_data = {
        'db_id': db_1.id,
        'bms_id': [bms_1.id],
        'wave_id': wave.id,
        'fe_rac_nodes': 1
    }

    req = client.put('/api/mappings', json=edit_mapping_data)

    assert req.status_code == 201
    assert req.json
    assert isinstance(req.json, dict)

    qs = db.session.query(Mapping).filter(Mapping.db_id == db_1.id)
    assert qs.count() == 1
    assert db_1.wave_id == wave.id
    assert db_1.fe_rac_nodes == edit_mapping_data['fe_rac_nodes']
    assert qs.first().bms_id == bms_1.id


def test_edit_mapping_without_bms_ids(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=None)
    bms_1 = BMSServerFactory()
    MappingFactory(source_db=db_1, bms=bms_1)

    edit_mapping_data = {
        'db_id': db_1.id,
        'bms_id': [],
        'wave_id': wave.id,
        'fe_rac_nodes': 0
    }

    req = client.put('/api/mappings', json=edit_mapping_data)

    assert req.status_code == 201

    assert not db_1.wave_id


def test_edit_rac_db_mapping(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=None)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    MappingFactory(source_db=db_1, bms=BMSServerFactory())  # should be removed
    MappingFactory(source_db=db_1, bms=bms_1)

    edit_mapping_data = {
        'db_id': db_1.id,
        'bms_id': [bms_1.id, bms_2.id],
        'wave_id': wave.id,
        'fe_rac_nodes': 2
    }

    req = client.put('/api/mappings', json=edit_mapping_data)

    assert req.status_code == 201
    assert req.json
    assert isinstance(req.json, dict)

    qs = db.session.query(Mapping).filter(Mapping.db_id == db_1.id)
    assert qs.count() == 2
    db_maps = qs.all()
    assert {m.bms_id for m in db_maps} == set([bms_1.id, bms_2.id])
