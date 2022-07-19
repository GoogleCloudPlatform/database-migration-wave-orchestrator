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

import base64
import json

from bms_app.models import OperationStatus, SourceDBStatus, SourceDBType

from tests.factories import (
    BMSServerFactory, MappingFactory, OperationDetailsFactory,
    OperationFactory, ProjectFactory, SourceDBFactory, WaveFactory
)


message = {
    'message': {
        'attributes': {
            'key': 'value'
        },
        'data': {},
        'messageId': '2070443601311540',
        'message_id': '2070443601311540',
        'publishTime': '2021-02-26T19:13:55.749Z',
        'publish_time': '2021-02-26T19:13:55.749Z',
    },
    'subscription': 'projects/myproject/subscriptions/mysubscription'
}


def encode(data):
    """Function to encode data for pubsub message"""
    data = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return data


def test_si_deployed_status(client):
    """Test correct db status update EMPTY -> DEPLOYED."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=map_1, operation=op_1)

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DEPLOYED


def test_si_failed_status(client):
    """Test correct db status update EMPTY -> FAILED."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=map_1, operation=op_1)

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'FAILED'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    req = client.get(f'/api/source-dbs/{db_1.id}')

    assert req.status_code == 200
    data = req.json

    assert data
    assert data['status'] == 'FAILED'


def test_si_rollback_status(client):
    """Test correct db status update DEPLOYED -> ROLLBACK."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave, status=SourceDBStatus.DEPLOYED)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave, operation_type='ROLLBACK')
    OperationDetailsFactory(wave=wave, mapping=map_1, operation=op_1, operation_type='ROLLBACK')

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.ROLLBACKED


def test_si_rollback_failed_status(client):
    """Test correct db status update DEPLOYED -> FAILED."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave, status=SourceDBStatus.DEPLOYED)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave, operation_type='ROLLBACK')
    OperationDetailsFactory(wave=wave, mapping=map_1, operation=op_1, operation_type='ROLLBACK')

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'FAILED'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.FAILED


def test_rac_fail_if_one_host_fail(client):
    """Test to check the correct update of the status of the database.

    Don't allow update db status to COMPLETE
    if at least one of RAC db instance during migration is failed.
    """
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave, db_type=SourceDBType.RAC)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    op_1 = OperationFactory(wave=wave, operation_type='DEPLOYMENT')
    OperationDetailsFactory(wave=wave, mapping=map_1, operation=op_1, status=OperationStatus.COMPLETE)
    OperationDetailsFactory(wave=wave, mapping=map_2, operation=op_1)

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'FAILED'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.FAILED


def test_rac_waits_all_host_finish(client):
    """Test to check the correct update of the status of the database.

    Correct status update during RAC migration
    when waiting for all instances.
    """
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave, status=SourceDBStatus.EMPTY, db_type=SourceDBType.RAC)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    bms_3 = BMSServerFactory(name='oracle-bms-vm3')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    map_3 = MappingFactory(source_db=db_1, bms=bms_3, rac_node=2)
    op_1 = OperationFactory(wave=wave, operation_type='DEPLOYMENT')
    OperationDetailsFactory(
        wave=wave,
        mapping=map_1,
        operation=op_1,
        operation_type='DEPLOYMENT',
        status=OperationStatus.COMPLETE
    )
    OperationDetailsFactory(
        wave=wave,
        mapping=map_2,
        operation=op_1,
        operation_type='DEPLOYMENT',
        status=OperationStatus.IN_PROGRESS
    )
    OperationDetailsFactory(
        wave=wave,
        mapping=map_3,
        operation=op_1,
        operation_type='DEPLOYMENT',
        status=OperationStatus.IN_PROGRESS
    )

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.EMPTY


def test_rac_all_hosts_complete(client):
    """Test to check the correct update of the status of the database.

    Correct status update during RAC migration
    when all instances were successful.
    """
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave, status=SourceDBStatus.EMPTY, db_type=SourceDBType.RAC)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    bms_3 = BMSServerFactory(name='oracle-bms-vm3')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    map_3 = MappingFactory(source_db=db_1, bms=bms_3, rac_node=2)
    op_1 = OperationFactory(wave=wave, operation_type='DEPLOYMENT')
    OperationDetailsFactory(
        wave=wave,
        mapping=map_1,
        operation=op_1,
        operation_type='DEPLOYMENT',
        status=OperationStatus.COMPLETE
    )
    OperationDetailsFactory(
        wave=wave,
        mapping=map_2,
        operation=op_1,
        operation_type='DEPLOYMENT',
        status=OperationStatus.IN_PROGRESS
    )
    OperationDetailsFactory(
        wave=wave,
        mapping=map_3,
        operation=op_1,
        operation_type='DEPLOYMENT',
        status=OperationStatus.COMPLETE
    )

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DEPLOYED


def test_si_failed_to_rollbacked(client):
    """Test to check the correct update of the status of the database.

    Don't allow update db status to COMPLETE
    if at least one of RAC db instance during migration is failed.
    """
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave, status=SourceDBStatus.FAILED)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave, operation_type='ROLLBACK')
    OperationDetailsFactory(wave=wave, mapping=map_1, operation=op_1, operation_type='ROLLBACK')

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': [bms_1.name],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.ROLLBACKED


def test_rac_status_calucation(client):
    """Check if only RAC nodes statuses are taken into account."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    si_db = SourceDBFactory(project=pr, wave=wave, status=SourceDBStatus.FAILED)
    rac_db = SourceDBFactory(project=pr, wave=wave, db_type=SourceDBType.RAC)
    si_map = MappingFactory(source_db=si_db)
    rac_map_1 = MappingFactory(source_db=rac_db, rac_node=0)
    rac_map_2 = MappingFactory(source_db=rac_db, rac_node=1)
    op_1 = OperationFactory(wave=wave)
    si_oph = OperationDetailsFactory(wave=wave, mapping=si_map, operation=op_1, status=OperationStatus.FAILED)
    rac_oph_1 = OperationDetailsFactory(wave=wave, mapping=rac_map_1, operation=op_1)
    rac_oph_2 = OperationDetailsFactory(wave=wave, mapping=rac_map_2, operation=op_1)

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': [rac_map_1.bms.name, rac_map_2.bms.name],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert si_oph.status == OperationStatus.FAILED
    assert rac_oph_1.status == OperationStatus.COMPLETE
    assert rac_oph_2.status == OperationStatus.COMPLETE

    assert si_db.status == SourceDBStatus.FAILED
    assert rac_db.status == SourceDBStatus.DEPLOYED


def test_rac_do_not_fail_if_all_host_do_not_finish(client):
    """RAC failed if all nodes fail."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    rac_db = SourceDBFactory(project=pr, wave=wave, db_type=SourceDBType.RAC)
    rac_map_1 = MappingFactory(source_db=rac_db, rac_node=0)
    rac_map_2 = MappingFactory(source_db=rac_db, rac_node=1)
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=rac_map_1, operation=op_1)
    OperationDetailsFactory(wave=wave, mapping=rac_map_2, operation=op_1)

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': [rac_map_1.bms.name],
        'host_status': 'FAILED'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert rac_db.status == SourceDBStatus.EMPTY


def test_rac_fail_if_all_host_finish(client):
    """RAC failed if all nodes fail."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    rac_db = SourceDBFactory(project=pr, wave=wave, db_type=SourceDBType.RAC)
    rac_map_1 = MappingFactory(source_db=rac_db, rac_node=0)
    rac_map_2 = MappingFactory(source_db=rac_db, rac_node=1)
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=rac_map_1, operation=op_1)
    OperationDetailsFactory(wave=wave, mapping=rac_map_2, operation=op_1, status=OperationStatus.FAILED)

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': [rac_map_1.bms.name],
        'host_status': 'FAILED'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert rac_db.status == SourceDBStatus.FAILED


def test_in_progress_host_status(client):
    """Test IN_PROGRESS host status."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave)
    opd_1 = OperationDetailsFactory(wave=wave, mapping=map_1, operation=op_1)

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'IN_PROGRESS'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    req = client.get(f'/api/source-dbs/{db_1.id}')

    assert req.status_code == 200
    data = req.json

    assert data
    assert data['status'] == SourceDBStatus.EMPTY.value

    assert opd_1.status == OperationStatus.IN_PROGRESS
