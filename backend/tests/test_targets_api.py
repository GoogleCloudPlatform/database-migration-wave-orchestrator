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

import io

from bms_app.models import BMSServer, SourceDBStatus, db

from .factories import (
    BMSServerFactory, ConfigFactory, MappingFactory, ProjectFactory,
    SourceDBFactory
)


post_data = b"""[
    {
        "name": "bms-t",
        "state": "RUNNING",
        "machineType": "o2-standard-16-metal",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"},
            {"name": "persistent-disk-2", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdd"},
            {"name": "persistent-disk-3", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdb"}
        ],
        "networks": [
            {"ipAddress": "172.25.9.2", "name": "nic0", "type": "CLIENT"},
            {"ipAddress": "2001:0db8:85a3:0000:0000:8a2e:0370:7334", "name": "nic0", "type": "PRIVATE"}
        ],
        "cpu": "4",
        "socket": "2",
        "ram": "32",
        "location": "europe-west-3"
    },
    {
        "name": "bms-t2",
        "machineType": "o2-standard-8-metal",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"},
            {"name": "persistent-disk-2", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdd"},
            {"name": "persistent-disk-3", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdb"}
        ],
        "networks": [
            {"ipAddress": "172.25.9.12", "name": "nic0", "type": "CLIENT"},
            {"ipAddress": "10.0.0.12", "name": "nic0", "type": "PRIVATE"}
        ],
        "cpu": "4",
        "socket": "2",
        "ram": "32",
        "location": "europe-west-3"
    }
]
"""

post_wrong_data = b"""[
    {
        name": "bms-t",
        "machineType": "o2-standard-16-metal",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"},
            {"name": "persistent-disk-2", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdd"},
            {"name": "persistent-disk-3", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdb"}
        ],
        "networks": [
            {"ipAddress": "172.25.9.2", "name": "nic0", "type": "CLIENT"},
            {"ipAddress": "10.0.0.2", "name": "nic0", "type": "PRIVATE"}
        ],
        "cpu": "4",
        "socket": "2",
        "ram": "32",
        "location": "europe-west-3"
    }
]
"""

post_data_without_location = b"""[
    {
        "name": "bms-t",
        "machineType": "o2-standard-16-metal",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"}
        ],
        "networks": [
            {"ipAddress": "172.25.9.2", "name": "nic0", "type": "CLIENT"},
            {"ipAddress": "10.0.0.2", "name": "nic0", "type": "PRIVATE"}
        ]
    }
]
"""


post_data_without_cpu = b"""[
    {
        "name": "bms-t",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"}
        ],
        "networks": [
            {"ipAddress": "172.25.9.2", "name": "nic0", "type": "CLIENT"}
        ],
        "socket": "2",
        "ram": "32",
        "location": "europe-west-3"
    }
]
"""


post_data_without_client_network = b"""[
    {
        "name": "bms-t",
        "machineType": "o2-standard-16-metal",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"}
        ],
        "networks": [
            {"ipAddress": "172.25.9.2", "name": "nic0", "type": "PRIVATE"},
            {"ipAddress": "10.0.0.2", "name": "nic0", "type": "PRIVATE"}
        ],
        "location": "europe-west-3"
    }
]
"""

post_data_with_wrong_ipAddress = b"""[
    {
        "name": "bms-t",
        "machineType": "o2-standard-16-metal",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"}
        ],
        "networks": [
            {"ipAddress": "aabbcc", "name": "nic0", "type": "CLIENT"},
            {"ipAddress": "10.0.0.2", "name": "nic0", "type": "PRIVATE"}
        ],
        "location": "europe-west-3"
    }
]
"""

post_data_with_wrong_network_type = b"""[
    {
        "name": "bms-t",
        "machineType": "o2-standard-16-metal",
        "luns": [
            {"name": "persistent-disk-1", "size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdc"}
        ],
        "networks": [
            {"ipAddress": "aabbcc", "name": "nic0", "type": "CLIENT"},
            {"ipAddress": "10.0.0.2", "name": "nic0", "type": "ABC"}
        ],
        "location": "europe-west-3"
    }
]
"""

post_data_with_storage_volume_duplicates = b"""[
    {
        "name": "os_37",
        "create_time": "2021-12-15 12:12:34.000000",
        "state": "RUNNING",
        "machineType": "n2-standard-4",
        "luns": [
            {"name": "persistent-disk-4", "size_gb": "50", "storage_type": "PERSISTENT", "storage_volume": "/dev/sde"},
            {"name": "persistent-disk-4", "size_gb": "50", "storage_type": "PERSISTENT", "storage_volume": "/dev/sde"}
        ],
        "networks": [{"ipAddress": "172.25.9.39", "name": "eth0", "type": "CLIENT"}],
        "location": "europe-west4",
        "secret_name": "aaa",
        "cpu": "4",
        "socket": "a",
        "ram": "16"
    }
]
"""

post_data_with_unknown_and_without_some_fields_ = b"""[
    {
        "name": "bms-test-1",
        "luns": [
            {"size_gb": "10", "storage_type": "PERSISTENT"},
            {"size_gb": "10", "storage_type": "PERSISTENT"},
            {"size_gb": "10", "storage_type": "PERSISTENT", "storage_volume": "/dev/sdb", "names":"test_data"}
        ],
        "networks": [
            {"ipAddress": "2001:0db8:85a3:0000:0000:8a2e:0370:7334", "name": "nic0", "type": "CLIENT"},
            {"ipAddress": "10.0.0.2", "type": "PRIVATE"}
        ],
    "cpu": "2",
    "socket": "2",
    "ram": "2"
    }
]
"""


def test_add_wrong_json_format_err(client):
    data = {
        'file': (io.BytesIO(post_wrong_data), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )

    assert req.status_code == 400


def test_add_data_with_storage_volume_duplicates(client):
    data = {
        'file': (io.BytesIO(post_data_with_storage_volume_duplicates), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )

    assert req.status_code == 400


def test_adding_bms_server(client):
    data = {
        'file': (io.BytesIO(post_data), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 201

    bms_servers = db.session.query(BMSServer).all()
    assert len(bms_servers) == 2

    assert bms_servers[0].created_at


def test_list_bms_servers(client):
    BMSServerFactory()
    BMSServerFactory()

    req = client.get('/api/targets')

    assert req.status_code == 200

    targets = req.json['data']

    assert len(targets) == 2

    fields = {
        'id', 'name', 'cpu', 'socket', 'ram', 'secret_name',
        'client_ip', 'created_at', 'location'
    }
    assert fields == set(targets[0].keys())

    assert targets[0]['client_ip'] == '172.25.9.8'


def test_list_bms_servers_with_filters(client):
    """Test bms list filters.

    Returns only severs mapped to db from the specific project
    or servers that are not mapped yet.
    """
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    db_1 = SourceDBFactory(project=pr_1)
    db_2 = SourceDBFactory(project=pr_2)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    unmapped_bms = BMSServerFactory()

    MappingFactory(source_db=db_1, bms=bms_1)
    MappingFactory(source_db=db_2, bms=bms_2)

    req = client.get(f'/api/targets?project_id={pr_1.id}&unmapped=True')

    assert req.status_code == 200

    targets = req.json['data']

    assert len(targets) == 2
    assert {x['id'] for x in targets} == {bms_1.id, unmapped_bms.id}


def test_getting_bms_servers(client):
    bms = BMSServerFactory()

    req = client.get(f'/api/targets/{bms.id}')

    assert req.status_code == 200

    data = req.json

    fields = {
        'id', 'name', 'cpu', 'socket', 'ram', 'secret_name',
        'client_ip', 'client_ip', 'luns', 'networks', 'machine_type',
        'state', 'deleted', 'created_at', 'location'
    }
    assert fields == set(data.keys())

    assert data['client_ip'] == '172.25.9.8'


def test_overwrite_false(client):
    bms = BMSServerFactory(
        name='bms-t',
        machine_type='abc',
        luns=[],
        networks=[]
    )

    data = {
        'file': (io.BytesIO(post_data), 'targets.json'),
        'overwrite': False,
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 201

    assert bms.machine_type == 'abc'
    assert not bms.luns
    assert not bms.networks


def test_overwrite_mapped_but_not_deployed_bms_server(client):
    source_db = SourceDBFactory()
    bms = BMSServerFactory(
        name='bms-t',
        machine_type='abc',
        luns=[],
        networks=[]
    )
    config = ConfigFactory(
        source_db=source_db,
        asm_config_values={'k': 'v'},
        data_mounts_values={'k': 'v'},
        rac_config_values={'k': 'v'},
        misc_config_values={'swap_blk_device': 'x', 'oracle_root': 'y'}
    )
    MappingFactory(source_db=source_db, bms=bms)

    data = {
        'file': (io.BytesIO(post_data), 'targets.json'),
        'overwrite': True,
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 201

    assert bms.machine_type == 'o2-standard-16-metal'
    assert len(bms.luns) == 3
    assert len(bms.networks) == 2
    assert not config.asm_config_values
    assert not config.data_mounts_values
    assert not config.rac_config_values
    assert not config.misc_config_values['swap_blk_device']
    assert not config.misc_config_values['oracle_root']


def test_not_overwrite_deployed_bms_server(client):
    source_db = SourceDBFactory(status=SourceDBStatus.DEPLOYED)
    bms = BMSServerFactory(
        name='bms-t',
        machine_type='abc',
        luns=[],
        networks=[]
    )
    config = ConfigFactory(
        source_db=source_db,
        asm_config_values={'k': 'v'},
        data_mounts_values={'k': 'v'},
        rac_config_values={'k': 'v'},
        misc_config_values={'swap_blk_device': 'x', 'oracle_root': 'y'}
    )
    mapping = MappingFactory(source_db=source_db, bms=bms)

    data = {
        'file': (io.BytesIO(post_data), 'targets.json'),
        'overwrite': True,
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 201

    assert bms.machine_type == 'abc'
    assert not bms.luns
    assert not bms.networks
    assert config.asm_config_values
    assert config.data_mounts_values
    assert config.rac_config_values
    assert config.misc_config_values == {'swap_blk_device': 'x', 'oracle_root': 'y'}


def test_edit_bms_server(client):
    """Test updating secret name."""
    bms = BMSServerFactory(secret_name='')

    req = client.put(f'/api/targets/{bms.id}', json={'secret_name': 'secret'})

    assert req.status_code == 200
    assert bms.secret_name == 'secret'


def test_adding_bms_server_without_required_field(client):
    data = {
        'file': (io.BytesIO(post_data_without_location), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 400

    assert not db.session.query(BMSServer).count()


def test_adding_bms_server_without_cpu(client):
    data = {
        'file': (io.BytesIO(post_data_without_cpu), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 400

    assert not db.session.query(BMSServer).count()


def test_adding_bms_server_without_client_network(client):
    data = {
        'file': (io.BytesIO(post_data_without_client_network), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 400

    assert not db.session.query(BMSServer).all()


def test_adding_server_with_wrong_ip(client):
    data = {
        'file': (io.BytesIO(post_data_with_wrong_ipAddress), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 400

    assert not db.session.query(BMSServer).all()


def test_adding_server_with_wrong_network_type(client):
    data = {
        'file': (io.BytesIO(post_data_with_wrong_network_type), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 400

    assert not db.session.query(BMSServer).all()


def test_adding_server_with_errors(client):
    data = {
        'file': (io.BytesIO(post_data_with_unknown_and_without_some_fields_), 'targets.json'),
    }

    req = client.post(
        '/api/targets/upload',
        data=data,
        content_type='multipart/form-data',
    )
    assert req.status_code == 400

    errors = req.json['errors']

    assert len(errors) == 2

    assert sorted(req.json['errors']['Missing data for required field.']) == sorted([
        'location',
        'networks.name',
        'luns.storage_volume',
        'luns.name'
    ])
    assert req.json['errors']['Unknown field.'] == ['luns.names']

    assert not db.session.query(BMSServer).all()
