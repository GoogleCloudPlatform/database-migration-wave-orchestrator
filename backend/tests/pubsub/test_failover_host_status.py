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

from bms_app.models import OperationType, SourceDBStatus

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


def test_si_failover_complete_status(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, wave=None, status='DT_COMPLETE')
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(
        wave=None,
        operation_type=OperationType.DB_FAILOVER
    )
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type=OperationType.DB_FAILOVER
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.FAILOVER_COMPLETE


def test_si_failover_failed_status(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, wave=None, status='DT_COMPLETE')
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(
        wave=None,
        operation_type=OperationType.DB_FAILOVER
    )
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type=OperationType.DB_FAILOVER
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'FAILED'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.FAILOVER_FAILED


# def test_rollback_restore_rac_failed_if_one_host_fail(client):
#     """Test to check the correct update of the status of the database.

#     # TODO: should be update after confirmation of RAC_rollback_restore logic
#     """
#     pr = ProjectFactory()
#     db_1 = SourceDBFactory(project=pr, wave=None, db_type=SourceDBType.RAC, status='DT_COMPLETE')
#     bms_1 = BMSServerFactory(name='oracle-bms-vm1')
#     bms_2 = BMSServerFactory(name='oracle-bms-vm2')
#     map_1 = MappingFactory(source_db=db_1, bms=bms_1, rac_node=0)
#     map_2 = MappingFactory(source_db=db_1, bms=bms_2, rac_node=1)
#     op_1 = OperationFactory(wave=None, operation_type='ROLLBACK_RESTORE')
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_1,
#         operation=op_1,
#         operation_type='ROLLBACK_RESTORE',
#         status=OperationStatus.FAILED)
#     OperationDetailsFactory(wave=None, mapping=map_2, operation=op_1, operation_type='ROLLBACK_RESTORE')

#     msg_data = {
#         'operation_id': op_1.id,
#         'hostnames': [bms_2.name],
#         'host_status': 'COMPLETE'
#     }
#     assert msg_data
#     message['message']['data'] = encode(msg_data)
#     client.post(f'/webhooks/status', json=message)


# def test_rollback_restore_rac_all_hosts_complete(client):
#     """Test to check the correct update of the status of the database.

#     Correct status update during RAC migration
#     when all instances were successful.
#     """
#     pr = ProjectFactory()
#     db_1 = SourceDBFactory(project=pr, wave=None, status=SourceDBStatus.DT_COMPLETE, db_type=SourceDBType.RAC)
#     bms_1 = BMSServerFactory(name='oracle-bms-vm1')
#     bms_2 = BMSServerFactory(name='oracle-bms-vm2')
#     bms_3 = BMSServerFactory(name='oracle-bms-vm3')
#     map_1 = MappingFactory(source_db=db_1, bms=bms_1)
#     map_2 = MappingFactory(source_db=db_1, bms=bms_2)
#     map_3 = MappingFactory(source_db=db_1, bms=bms_3)
#     op_1 = OperationFactory(wave=None, operation_type='ROLLBACK_RESTORE')
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_1,
#         operation=op_1,
#         operation_type='ROLLBACK_RESTORE',
#         status=OperationStatus.COMPLETE
#     )
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_2,
#         operation=op_1,
#         operation_type='ROLLBACK_RESTORE',
#         status=OperationStatus.IN_PROGRESS
#     )
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_3,
#         operation=op_1,
#         operation_type='ROLLBACK_RESTORE',
#         status=OperationStatus.COMPLETE
#     )

#     msg_data = {
#         'operation_id': op_1.id,
#         'hostnames': [bms_2.name],
#         'host_status': 'COMPLETE'
#     }
#     message['message']['data'] = encode(msg_data)
#     client.post(f'/webhooks/status', json=message)
