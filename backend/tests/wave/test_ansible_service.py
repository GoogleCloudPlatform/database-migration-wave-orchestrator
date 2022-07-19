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

import os
from unittest.mock import patch

from bms_app.models import SourceDBType
from bms_app.services.ansible import AnsibleConfigService
from bms_app.services.operations.objects import DbMapping

from tests.factories import (
    BMSServerFactory, ConfigFactory, MappingFactory, SourceDBFactory
)


excepted_inventory = """all:
  children:
    dbasm:
      hosts:
        target_1:
          ansible_ssh_extra_args: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
            -o IdentityAgent=no
          ansible_ssh_host: 172.25.9.8
          ansible_ssh_private_key_file: /root/.ssh/id_rsa_bms_toolkit
          ansible_ssh_user: customeradmin
          compatible_rdbms: a
          db_name: ORCL
          home_name: db_home19c
          oracle_edition: EE
          oracle_group: oinstall
          oracle_root: /u01/app
          oracle_user: oracle
          oracle_ver: '19'
          sm_token: sm_token_1
          swap_blk_device: /dev/sda
        target_2:
          ansible_ssh_extra_args: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
            -o IdentityAgent=no
          ansible_ssh_host: 172.25.9.9
          ansible_ssh_private_key_file: /root/.ssh/id_rsa_bms_toolkit
          ansible_ssh_user: customeradmin
          compatible_rdbms: a
          db_name: ORCL
          home_name: db_home19c
          oracle_edition: EE
          oracle_group: oinstall
          oracle_root: /u01/app
          oracle_user: oracle
          oracle_ver: '19'
          sm_token: sm_token_2
          swap_blk_device: /dev/sda
"""
excepted_inventory_provision = """all:
  children:
    dbasm:
      hosts:
        target_1:
          ansible_ssh_host: 172.25.9.8
          ansible_ssh_user: customeradmin
          sm_token: sm_token_1
        target_2:
          ansible_ssh_host: 172.25.9.9
          ansible_ssh_user: customeradmin
          sm_token: sm_token_2
"""
expected_asm_config_1 = """[
    {
        "diskgroup": "disk",
        "disks": [
            {
                "blk_device": "/dev/sdc",
                "name": "disk_1",
                "size": "20"
            }
        ],
        "au_size": "20",
        "redundancy": "a"
    }
]"""

expected_asm_config_2 = """[
    {
        "diskgroup": "disk",
        "disks": [
            {
                "blk_device": "/dev/sdc",
                "name": "disk_1",
                "size": "20"
            }
        ],
        "au_size": "20",
        "redundancy": "a"
    }
]"""
expected_data_mounts_config_1 = """[
    {
        "purpose": "software",
        "blk_device": "/dev/sdb",
        "name": "u01",
        "fstype": "xfs",
        "mount_point": "/u01",
        "mount_opts": "nofail"
    }
]"""
expected_data_mounts_config_2 = """[
    {
        "purpose": "software",
        "blk_device": "/dev/sdb",
        "name": "u01",
        "fstype": "xfs",
        "mount_point": "/u01",
        "mount_opts": "nofail"
    }
]"""

excepted_rac_inventory="""all:
  children:
    dbasm:
      hosts:
        rac_target_1:
          ansible_ssh_extra_args: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
            -o IdentityAgent=no
          ansible_ssh_host: 172.25.9.8
          ansible_ssh_private_key_file: /root/.ssh/id_rsa_bms_toolkit
          ansible_ssh_user: customeradmin
          cluster_domain: cluster_domain
          cluster_name: cluster_name
          cluster_type: RAC
          compatible_rdbms: a
          db_name: ORCL
          dg_name: dg_name
          home_name: db_home19c
          oracle_edition: EE
          oracle_group: oinstall
          oracle_root: /u01/app
          oracle_user: oracle
          oracle_ver: '19'
          private_net: private_net
          public_net: public_net
          rac_node: 1
          scan_ip1: scan_ip1
          scan_ip2: scan_ip2
          scan_ip3: scan_ip3
          scan_name: scan_name
          scan_port: scan_port
          sm_token: sm_token_1
          swap_blk_device: /dev/sda
          vip_ip: 10.0.0.1
          vip_name: vip-1
        rac_target_2:
          ansible_ssh_extra_args: -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
            -o IdentityAgent=no
          ansible_ssh_host: 172.25.9.9
          ansible_ssh_private_key_file: /root/.ssh/id_rsa_bms_toolkit
          ansible_ssh_user: customeradmin
          cluster_domain: cluster_domain
          cluster_name: cluster_name
          cluster_type: RAC
          compatible_rdbms: a
          db_name: ORCL
          dg_name: dg_name
          home_name: db_home19c
          oracle_edition: EE
          oracle_group: oinstall
          oracle_root: /u01/app
          oracle_user: oracle
          oracle_ver: '19'
          private_net: private_net
          public_net: public_net
          rac_node: 2
          scan_ip1: scan_ip1
          scan_ip2: scan_ip2
          scan_ip3: scan_ip3
          scan_name: scan_name
          scan_port: scan_port
          sm_token: sm_token_2
          swap_blk_device: /dev/sda
          vip_ip: 10.0.0.2
          vip_name: vip-2
"""
excepted_rac_inventory_provision = """all:
  children:
    dbasm:
      hosts:
        rac_target_1:
          ansible_ssh_host: 172.25.9.8
          ansible_ssh_user: customeradmin
          sm_token: sm_token_1
        rac_target_2:
          ansible_ssh_host: 172.25.9.9
          ansible_ssh_user: customeradmin
          sm_token: sm_token_2
"""
expected_rac_asm_config_1 = """[
    {
        "diskgroup": "disk",
        "disks": [
            {
                "blk_device": "/dev/sdc",
                "name": "disk_1",
                "size": "20"
            }
        ],
        "au_size": "20",
        "redundancy": "a"
    }
]"""

expected_rac_asm_config_2 = """[
    {
        "diskgroup": "disk",
        "disks": [
            {
                "blk_device": "/dev/sdc",
                "name": "disk_1",
                "size": "20"
            }
        ],
        "au_size": "20",
        "redundancy": "a"
    }
]"""
expected_rac_data_mounts_config_1 = """[
    {
        "purpose": "software",
        "blk_device": "/dev/sdb",
        "name": "u01",
        "fstype": "xfs",
        "mount_point": "/u01",
        "mount_opts": "nofail"
    }
]"""
expected_rac_data_mounts_config_2 = """[
    {
        "purpose": "software",
        "blk_device": "/dev/sdb",
        "name": "u01",
        "fstype": "xfs",
        "mount_point": "/u01",
        "mount_opts": "nofail"
    }
]"""


@patch('bms_app.services.ansible.mixins.upload_blob_from_string')
def test_ansible_si_config_generator(up_mock, client):
    db_1 = SourceDBFactory(oracle_edition='EE', oracle_version='19')
    db_2 = SourceDBFactory(oracle_edition='EE', oracle_version='19')
    ConfigFactory(source_db=db_1)
    ConfigFactory(source_db=db_2)
    bms_1 = BMSServerFactory(name='target_1', secret_name='sm_token_1', networks=[{'ipAddress': '172.25.9.8', 'name': 'nic0', 'type': 'CLIENT'}])
    bms_2 = BMSServerFactory(name='target_2', secret_name='sm_token_2', networks=[{'ipAddress': '172.25.9.9', 'name': 'nic0', 'type': 'CLIENT'}])
    mapp_1 = MappingFactory(source_db=db_1, bms=bms_1)
    mapp_2 = MappingFactory(source_db=db_2, bms=bms_2)

    db_mappings_objects = [
        DbMapping(db=db_1, mappings=[mapp_1]),
        DbMapping(db=db_2, mappings=[mapp_2])
    ]

    srv = AnsibleConfigService(
        db_mappings_objects=db_mappings_objects,
        gcs_config_dir='conf_dir'
    )
    srv.run()

    assert up_mock.called

    assert up_mock.call_args_list[0].args == (
        'test-bucket',
        os.path.normpath(os.path.normpath('conf_dir/inventory')),
        excepted_inventory
    )
    assert up_mock.call_args_list[1].args == (
        'test-bucket',
        os.path.normpath('conf_dir/inventory_temp'),
        excepted_inventory_provision
    )

    assert up_mock.call_args_list[2].args == (
        'test-bucket',
        os.path.normpath('conf_dir/asm_config/asm_disk_config_target_1.json'),
        expected_asm_config_1
    )
    assert up_mock.call_args_list[3].args == (
        'test-bucket',
        os.path.normpath('conf_dir/asm_config/asm_disk_config_target_2.json'),
        expected_asm_config_2
    )

    assert up_mock.call_args_list[4].args == (
        'test-bucket',
        os.path.normpath('conf_dir/data_mounts_config/data_mounts_config_target_1.json'),
        expected_data_mounts_config_1
    )
    assert up_mock.call_args_list[5].args == (
        'test-bucket',
        os.path.normpath('conf_dir/data_mounts_config/data_mounts_config_target_2.json'),
        expected_data_mounts_config_2
    )


@patch('bms_app.services.ansible.mixins.upload_blob_from_string')
def test_ansible_rac_config_generator(up_mock, client):
    db_1 = SourceDBFactory(
        oracle_edition='EE',
        oracle_version='19',
        db_type=SourceDBType.RAC,
        rac_nodes=2
    )
    ConfigFactory(
        source_db=db_1,
        rac_config_values={
            'cluster_name': 'cluster_name',
            'scan_ip3': 'scan_ip3',
            'scan_name': 'scan_name',
            'private_net': 'private_net',
            'vip_name': 'vip_name',
            'public_net': 'public_net',
            'scan_port': 'scan_port',
            'cluster_domain': 'cluster_domain',
            'dg_name': 'dg_name',
            'vip_ip': 'vip_ip',
            'scan_ip2': 'scan_ip2',
            'scan_ip1': 'scan_ip1',
            'rac_nodes': [
                {'vip_name': 'vip-1', 'node_id': 1, 'node_name': 'n1', 'vip_ip': '10.0.0.1'},
                {'vip_name': 'vip-2', 'node_id': 2, 'node_name': 'n3', 'vip_ip': '10.0.0.2'}
            ]
        }
    )
    bms_1 = BMSServerFactory(
        name='rac_target_1',
        secret_name='sm_token_1',
        networks=[{'ipAddress': '172.25.9.8', 'name': 'nic0', 'type': 'CLIENT'}]
    )
    bms_2 = BMSServerFactory(
        name='rac_target_2',
        secret_name='sm_token_2',
        networks=[{'ipAddress': '172.25.9.9', 'name': 'nic0', 'type': 'CLIENT'}]
    )
    mapp_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=1)
    mapp_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=2)
    db_mappings_objects = [
        DbMapping(db=db_1, mappings=[mapp_1]),
        DbMapping(db=db_1, mappings=[mapp_2])
    ]

    srv = AnsibleConfigService(
        db_mappings_objects=db_mappings_objects,
        gcs_config_dir='conf_dir'
    )
    srv.run()

    assert up_mock.called
    assert up_mock.call_args_list[0].args == (
        'test-bucket',
        os.path.normpath('conf_dir/inventory'),
        excepted_rac_inventory
    )
    assert up_mock.call_args_list[1].args == (
        'test-bucket',
        os.path.normpath('conf_dir/inventory_temp'),
        excepted_rac_inventory_provision
    )

    assert up_mock.call_args_list[2].args == (
        'test-bucket',
        os.path.normpath('conf_dir/asm_config/asm_disk_config_rac_target_1.json'),
        expected_rac_asm_config_1
    )
    assert up_mock.call_args_list[3].args == (
        'test-bucket',
        os.path.normpath('conf_dir/asm_config/asm_disk_config_rac_target_2.json'),
        expected_rac_asm_config_2
    )

    assert up_mock.call_args_list[4].args == (
        'test-bucket',
        os.path.normpath('conf_dir/data_mounts_config/data_mounts_config_rac_target_1.json'),
        expected_rac_data_mounts_config_1
    )
    assert up_mock.call_args_list[5].args == (
        'test-bucket',
        os.path.normpath('conf_dir/data_mounts_config/data_mounts_config_rac_target_2.json'),
        expected_rac_data_mounts_config_2
    )
