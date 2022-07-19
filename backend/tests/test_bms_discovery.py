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

from unittest.mock import patch

from bms_app.models import BMSServer, db

from .factories import BMSServerFactory


bms_api_data = [{'id': 'at-207685681-svr001',
    'luns': [{'bootLun': True,
            'name': 'projects/epam-bms-dev/locations/europe-west3/volumes/at-207685681-svr001-vol000/luns/at-207685681-svr001-lun000',
            'sizeGb': '200',
            'state': 'READY',
            'storageType': 'SSD',
            'storageVolume': 'at-207685681-svr001-vol000',
            'wwid': '600a098038314344345d4f7274665541'},
           {'name': 'projects/epam-bms-dev/locations/europe-west3/volumes/at-207685681-vol001/luns/at-6420816-lun001',
            'shareable': True,
            'sizeGb': '100',
            'state': 'READY',
            'storageType': 'SSD',
            'storageVolume': 'at-207685681-vol001',
            'wwid': '600a098038314344345d4f7274665531'},
           {'name': 'projects/epam-bms-dev/locations/europe-west3/volumes/at-207685681-vol001/luns/at-6420816-lun002',
            'shareable': True,
            'sizeGb': '200',
            'state': 'READY',
            'storageType': 'SSD',
            'storageVolume': 'at-207685681-vol002',
            'wwid': '600a098038314344345d4f7274665532'}],
    'machineType': 'o2-standard-32-metal',
    'name': 'projects/epam-bms-dev/locations/europe-west3/instances/bms-epam-si-01',
    'networks': [{'id': 'at-6420816-vlan002',
                'ipAddress': '10.0.0.128',
                'macAddress': ['34:80:0D:0D:54:8C', '34:80:0D:0D:5B:28'],
                'name': 'projects/epam-bms-dev/locations/europe-west3/networks/bms-epam-client-network',
                'type': 'CLIENT'},
               {'id': 'at-6420816-vlan001',
                'ipAddress': '172.0.0.128',
                'macAddress': ['34:80:0D:0D:54:8D', '34:80:0D:0D:5B:29'],
                'name': 'projects/epam-bms-dev/locations/europe-west3/networks/bms-epam-private-network',
                'type': 'PRIVATE'}],
    'state': 'RUNNING'},
    {'id': 'at-207685681-svr002',
    'luns': [{'bootLun': True,
            'name': 'projects/epam-bms-dev/locations/europe-west3/volumes/at-207685681-svr002-vol000/luns/at-207685681-svr002-lun000',
            'sizeGb': '200',
            'state': 'READY',
            'storageType': 'SSD',
            'storageVolume': 'at-207685681-svr002-vol000',
            'wwid': '600a098038314344345d4f7274665542'}],
   'machineType': 'o2-standard-32-metal',
   'name': 'projects/epam-bms-dev/locations/europe-west3/instances/bms-epam-si-02',
   'networks': [{'id': 'at-6420816-vlan002',
                'ipAddress': '10.0.0.129',
                'macAddress': ['34:80:0D:85:0B:DE', '34:80:0D:0D:50:9C'],
                'name': 'projects/epam-bms-dev/locations/europe-west3/networks/bms-epam-client-network',
                'type': 'CLIENT'},
               {'id': 'at-6420816-vlan001',
                'ipAddress': '172.0.0.129',
                'macAddress': ['34:80:0D:85:0B:DF', '34:80:0D:0D:50:9D'],
                'name': 'projects/epam-bms-dev/locations/europe-west3/networks/bms-epam-private-network',
                'type': 'PRIVATE'}],
   'state': 'RUNNING'}
]


@patch('bms_app.inventory_manager.views.fetch_bms_instances', return_value=bms_api_data)
def test_bms_discovery(mock, client):
    req = client.post('/api/targets/discovery')
    assert req.status_code == 201

    assert mock.called

    bms_servers = db.session.query(BMSServer).all()
    assert len(bms_servers) == 2

    assert {x.name for x in bms_servers} == {'at-207685681-svr001', 'at-207685681-svr002'}

    bms = next((x for x in bms_servers if x.name == 'at-207685681-svr001'))
    assert bms.luns == [
        {
            'name': 'at-6420816-lun001',
            'size_gb': '100',
            'storage_type': 'SSD',
            'storage_volume': '/dev/mapper/3600a098038314344345d4f7274665531'
        },
        {
            'name': 'at-6420816-lun002',
            'size_gb': '200',
            'storage_type': 'SSD',
            'storage_volume': '/dev/mapper/3600a098038314344345d4f7274665532'
        },
    ]
    assert bms.networks == [
        {
            'ipAddress': '10.0.0.128',
            'name': 'bms-epam-client-network',
            'type': 'CLIENT',
        },
        {
            'ipAddress': '172.0.0.128',
            'name': 'bms-epam-private-network',
            'type': 'PRIVATE'
        },
    ]
    assert bms.machine_type
    assert bms.state
    assert bms.cpu
    assert bms.ram
    assert bms.socket
    assert bms.location == 'europe-west3'
    assert not bms.deleted
    assert bms.created_at


@patch('bms_app.inventory_manager.views.fetch_bms_instances', return_value=bms_api_data)
def test_bms_discovery_overwrite(mock, client):
    bms = BMSServerFactory(
        name='at-207685681-svr001',
        machine_type='abc',
        luns=[],
        networks=[],
    )
    req = client.post('/api/targets/discovery', data={'overwrite': 'True'})
    assert req.status_code == 201

    assert mock.called

    assert bms.luns
    assert bms.networks
    assert bms.machine_type == 'o2-standard-32-metal'


@patch('bms_app.inventory_manager.views.fetch_bms_instances', return_value=bms_api_data)
def test_bms_discovery_not_overwrite(mock, client):
    bms = BMSServerFactory(
        name='at-207685681-svr001',
        machine_type='abc',
        luns=[],
        networks=[],
    )
    req = client.post('/api/targets/discovery')
    assert req.status_code == 201

    assert mock.called

    assert not bms.luns
    assert not bms.networks
    assert bms.machine_type == 'abc'
