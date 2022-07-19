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
    OperationFactory, ProjectFactory, SourceDBFactory
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


def test_si_restore_complete_status(client):
    """Test correct db status update PRE_RESTORE_COMPLETE -> DT_COMPLETE."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        status='PRE_RESTORE_COMPLETE'
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE'
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DT_COMPLETE


def test_si_restore_failed_status(client):
    """Test correct db status update RE_RESTORE_COMPLETE -> DT_FAILED."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        status='PRE_RESTORE_COMPLETE'
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE'
    )

    msg_data = {
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
    assert data['status'] == 'DT_FAILED'


def test_restore_rac_complete_partially_if_first_host_complete_before_second_fail(client):
    """Test to check the correct update of the status of the database.

    Update db status to COMPLETE_PARTIALLY
    if first of RAC db instance is complete but at least one other failed.
    """
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        db_type=SourceDBType.RAC,
        status='PRE_RESTORE_COMPLETE'
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.COMPLETE)
    OperationDetailsFactory(
        wave=None,
        mapping=map_2,
        operation=op_1,
        operation_type='BACKUP_RESTORE'
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'FAILED'
    }
    assert msg_data
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DT_PARTIALLY


def test_restore_rac_complete_partially_if_first_host_complete_after_second_fail(client):
    """Test to check the correct update of the status of the database.

    Update db status to COMPLETE_PARTIALLY
    if first of RAC db instance is complete but at least one other failed.
    """
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        db_type=SourceDBType.RAC,
        status='PRE_RESTORE_COMPLETE'
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_2,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.FAILED)

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': [bms_1.name],
        'host_status': 'COMPLETE'
    }
    assert msg_data
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DT_PARTIALLY


def test_restore_rac_failed_if_first_host_fail_before_second_complete(client):
    """Test to check the correct update of the status of the database.

    Update db status to DT_FAILED
    if first of RAC db instance is failed.
    """
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        db_type=SourceDBType.RAC,
        status='PRE_RESTORE_COMPLETE'
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.FAILED)
    OperationDetailsFactory(
        wave=None,
        mapping=map_2,
        operation=op_1,
        operation_type='BACKUP_RESTORE'
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'COMPLETE'
    }
    assert msg_data
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DT_FAILED


def test_restore_rac_failed_if_first_host_fail_after_second_complete(client):
    """Test to check the correct update of the status of the database.

    Update db status to DT_FAILED
    if first of RAC db instance is failed.
    """
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        db_type=SourceDBType.RAC,
        status='PRE_RESTORE_COMPLETE'
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_2,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status='COMPLETE')

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': [bms_1.name],
        'host_status': 'FAILED'
    }
    assert msg_data
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DT_FAILED


def test_restore_rac_if_all_hosts_fail(client):
    """Test to check the correct update of the status of the database.

    Update db status to DT_FAILED
    if first of RAC db instance is failed.
    """
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        db_type=SourceDBType.RAC,
        status='PRE_RESTORE_COMPLETE'
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.FAILED)
    OperationDetailsFactory(
        wave=None,
        mapping=map_2,
        operation=op_1,
        operation_type='BACKUP_RESTORE'
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'FAILED'
    }
    assert msg_data
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DT_FAILED


def test_restore_rac_waits_all_host_finish(client):
    """Test to check the correct update of the status of the database.

    Correct status update during RAC migration
    when first instance was successful but next failed.
    """
    pr = ProjectFactory()

    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        status=SourceDBStatus.PRE_RESTORE_COMPLETE,
        db_type=SourceDBType.RAC
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    bms_3 = BMSServerFactory(name='oracle-bms-vm3')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    map_3 = MappingFactory(source_db=db_1, bms=bms_3, rac_node=2)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.COMPLETE
    )
    OperationDetailsFactory(
        wave=None,
        mapping=map_2,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.IN_PROGRESS
    )
    OperationDetailsFactory(
        wave=None,
        mapping=map_3,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.IN_PROGRESS
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.PRE_RESTORE_COMPLETE


def test_restore_rac_all_hosts_complete(client):
    """Test to check the correct update of the status of the database.

    Correct status update during RAC migration
    when all instances were successful.
    """
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        status=SourceDBStatus.PRE_RESTORE_COMPLETE,
        db_type=SourceDBType.RAC
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    bms_2 = BMSServerFactory(name='oracle-bms-vm2')
    bms_3 = BMSServerFactory(name='oracle-bms-vm3')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
    map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
    map_3 = MappingFactory(source_db=db_1, bms=bms_3, rac_node=2)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.COMPLETE
    )
    OperationDetailsFactory(
        wave=None,
        mapping=map_2,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.IN_PROGRESS
    )
    OperationDetailsFactory(
        wave=None,
        mapping=map_3,
        operation=op_1,
        operation_type='BACKUP_RESTORE',
        status=OperationStatus.COMPLETE
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': [bms_2.name],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)
    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DT_COMPLETE
