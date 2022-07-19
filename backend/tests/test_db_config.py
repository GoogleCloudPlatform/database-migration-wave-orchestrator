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

import factory

from bms_app.models import Config, db

from .factories import ConfigFactory, ProjectFactory, SourceDBFactory


def test_get_config(client):
    """Test for returning config."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    conf = ConfigFactory(source_db=db_1, created_at=factory.Faker('date_object'))

    req = client.get(f'/api/source-dbs/{db_1.id}/config')

    assert req.status_code == 200
    data = req.json

    assert data
    assert isinstance(data, dict)

    fields = {
        'db_id', 'install_config_values', 'db_params_values',
        'data_mounts_values', 'asm_config_values', 'rac_config_values',
        'misc_config_values', 'created_at', 'is_configured'
    }
    assert fields == set(data.keys())

    assert data == {
        'db_id': conf.db_id,
        'install_config_values': conf.install_config_values,
        'db_params_values': conf.db_params_values,
        'data_mounts_values': conf.data_mounts_values,
        'asm_config_values': conf.asm_config_values,
        'rac_config_values': conf.rac_config_values,
        'misc_config_values': conf.misc_config_values,
        'created_at': conf.created_at.strftime("%Y-%m-%dT%H:%M:%S"),
        'is_configured': conf.is_configured
    }


def test_delete_a_config(client):
    """Test for checking config deletion."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr)
    conf = ConfigFactory(source_db=db_1)

    req = client.delete(f'/api/source-dbs/{db_1.id}/config')

    assert req.status_code == 204
    assert not db.session.query(Config).get(conf.id)


def test_add_config(client):
    """Test adding config"""
    pr = ProjectFactory.create()
    db_1 = SourceDBFactory(project=pr)

    add_config_data = {
        'install_config_values': {"oracle_user": "oracle", "oracle_group": "oinstall", "home_name": "db_home19c",
                                  "grid_user": "grid", "grid_group": "asmadmin"},
        'db_params_values': {"db_name": "ORCL"},
        'data_mounts_values': [{'blk_device': 'blk', 'fstype': 'xfs', 'mount_opts': 'nofail', 'mount_point': '/u01',
                                'name': 'u01', 'purpose': 'software'}],
        'asm_config_values': [{'au_size': '20', 'diskgroup': 'disk', 'disks': [{'blk_device': 'blk', 'name': 'n',
                                                                                'size': '20'}], 'redundancy': 'a'}],
        'rac_config_values': {'cluster_domain': 'a', 'cluster_name': 'a', 'dg_name': 'a', 'private_net': 'eth1',
                              'public_net': 'eth0', 'rac_nodes': [{'node_id': 1, 'node_ip': '1', 'node_name': 'a',
                                                                   'vip_ip': '1', 'vip_name': 'a'}], 'scan_ip1': '1',
                              'scan_ip2': '1', 'scan_ip3': '1', 'scan_name': 'SCAN', 'scan_port': 1521, 'vip_ip': '1',
                              'vip_name': 'a'},
        'misc_config_values': {"swap_blk_device": "a", "oracle_root": "/u01/app", "ntp_preferred": "/etc/ntp.conf",
                               "role_separation": True, "compatible_asm": "a", "compatible_rdbms": "a",
                               "asm_disk_management": "a", "is_swap_configured": True},
        'is_configured': True
    }

    req = client.post(
        f'/api/source-dbs/{db_1.id}/config',
        json=add_config_data
    )
    assert req.status_code == 201
    assert 'db_id' in req.json

    config_db = Config.query.filter(Config.db_id == db_1.id)
    assert config_db

    config = Config.query.get(req.json['db_id'])
    assert config.is_configured is add_config_data['is_configured']

    assert config.install_config_values == add_config_data['install_config_values']
    assert config.db_params_values == add_config_data['db_params_values']
    assert config.data_mounts_values == add_config_data['data_mounts_values']
    assert config.asm_config_values == add_config_data['asm_config_values']
    assert config.rac_config_values == add_config_data['rac_config_values']
    assert config.misc_config_values == add_config_data['misc_config_values']



def test_draft_config(client):
    """Test no validation/default values."""
    pr = ProjectFactory.create()
    db_1 = SourceDBFactory(project=pr)

    draft_data = {
        'install_config_values': {"oracle_user": "oracle"},
        'db_params_values': {"db_name": "ORCL"},
        'data_mounts_values': [{'blk_device': 'blk'}],
        'misc_config_values': {"swap_blk_device": "/dev/sda"},
        'is_configured': False
    }

    req = client.post(
        f'/api/source-dbs/{db_1.id}/config',
        json=draft_data,
    )
    assert req.status_code == 201
    assert 'db_id' in req.json

    config = db.session.query(Config).filter(Config.db_id == db_1.id).first()
    assert config

    assert config.is_configured == draft_data['is_configured']

    assert config.install_config_values == draft_data['install_config_values']
    assert config.db_params_values == draft_data['db_params_values']
    assert config.data_mounts_values == draft_data['data_mounts_values']
    assert config.misc_config_values == draft_data['misc_config_values']

    assert not config.rac_config_values
    assert not config.asm_config_values


def test_str_type_false_config(client):
    """Test adding str type config with false value"""
    pr = ProjectFactory.create()
    db_1 = SourceDBFactory(project=pr)

    add_config_data = {
        'is_configured': 'false'
    }

    req = client.post(
        f'/api/source-dbs/{db_1.id}/config',
        json=add_config_data
    )
    assert req.status_code == 201
    assert 'db_id' in req.json

    config_db = Config.query.filter(Config.db_id == db_1.id)
    assert config_db

    config = Config.query.get(req.json['db_id'])

    if not isinstance(add_config_data['is_configured'], bool):
        add_config_data['is_configured'] = False if add_config_data['is_configured'] == 'false' else True

    assert config.is_configured is add_config_data['is_configured']


def test_str_type_true_config(client):
    """Test adding str type config with any value except false"""
    pr = ProjectFactory.create()
    db_1 = SourceDBFactory(project=pr)

    add_config_data = {
        'is_configured': 'true'
    }

    req = client.post(
        f'/api/source-dbs/{db_1.id}/config',
        json=add_config_data
    )
    assert req.status_code == 201
    assert 'db_id' in req.json

    config_db = Config.query.filter(Config.db_id == db_1.id)
    assert config_db

    config = Config.query.get(req.json['db_id'])

    if not isinstance(add_config_data['is_configured'], bool):
        add_config_data['is_configured'] = False if add_config_data['is_configured'] == 'false' else True

    assert config.is_configured is add_config_data['is_configured']
