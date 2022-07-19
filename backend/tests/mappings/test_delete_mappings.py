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

from bms_app.models import Config, Mapping, SourceDB, db

from tests.factories import (
    ConfigFactory, MappingFactory, OperationDetailsFactory, OperationFactory,
    ProjectFactory, SourceDBFactory, WaveFactory
)


def test_delete_a_mapping(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    MappingFactory(source_db=db_1)

    req = client.delete(f'/api/mappings?db_id={db_1.id}')

    assert req.status_code == 204
    assert not db.session.query(Mapping).filter(Mapping.db_id == db_1.id).count()


def test_not_delete_mapping_with_operation(client):
    """Mapping containing operation can not be deleted."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    m_1 = MappingFactory(source_db=db_1)

    op = OperationFactory(wave_id=wave.id)
    OperationDetailsFactory(operation=op, mapping=m_1, wave=wave)

    req = client.delete(f'/api/mappings?db_id={db_1.id}')

    assert req.status_code == 400
    assert db.session.query(Mapping).filter(Mapping.db_id == db_1.id).count() == 1


def test_clear_bms_target_params(client):
    """Test clear config parameters related to bms target"""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    conf = ConfigFactory(source_db=db_1)

    req = client.delete(f'/api/mappings?db_id={db_1.id}')
    assert req.status_code == 204

    source_db = SourceDB.query.get(db_1.id)
    assert source_db.config

    config = Config.query.get(conf.id)

    assert not config.data_mounts_values
    assert not config.asm_config_values
    assert not config.rac_config_values
    assert not config.misc_config_values['swap_blk_device']
    assert not config.misc_config_values['oracle_root']
    assert not db.session.query(Mapping).filter(Mapping.db_id == db_1.id).count()
