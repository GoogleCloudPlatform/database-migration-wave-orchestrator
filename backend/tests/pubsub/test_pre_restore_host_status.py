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
from unittest.mock import patch

from bms_app.models import (
    OperationDetailsError, OperationStatus, SourceDBStatus, db
)
from bms_app.services.rman import RmanLogFileError

from tests.factories import (
    BMSServerFactory, MappingFactory, OperationDetailsErrorFactory,
    OperationDetailsFactory, OperationFactory, ProjectFactory, SourceDBFactory
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


@patch('bms_app.services.status_handlers.operation_detail.RmanLogFileParser')
def test_si_pre_restore_complete_status(file_content_mock, client):
    """Test db update status DEPLOYED -> PRE_RESTORE_COMPLETE."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, wave=None)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='PRE_RESTORE'
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.PRE_RESTORE_COMPLETE


@patch('bms_app.services.status_handlers.operation_detail.RmanLogFileParser')
def test_si_pre_restore_failed_status(rman_parser_mock, client):
    """Test operation is failed because of pubsub FAIL message."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, wave=None)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
    OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='PRE_RESTORE'
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
    assert data['status'] == 'PRE_RESTORE_FAILED'

    assert db.session.query(OperationDetailsError) \
        .filter(OperationDetailsError.message == 'bms toolkit error') \
        .count()


@patch('bms_app.services.status_handlers.operation_detail.RmanLogFileParser')
def test_si_pre_restore_failed_due_to_additional_error(rman_parser_mock, client):
    """Test db update status DEPLOYED -> PRE_RESTORE_FAILED."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, wave=None)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
    opd_1 = OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='PRE_RESTORE'
    )
    OperationDetailsErrorFactory(operation_details=opd_1)

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.PRE_RESTORE_FAILED


def test_pre_restore_in_progress_host_status(client):
    """Test IN_PROGRESS host status during PRE_RESTORE."""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(
        project=pr,
        wave=None,
        status=SourceDBStatus.DEPLOYED
    )
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
    opd_1 = OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='PRE_RESTORE'
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'IN_PROGRESS'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.DEPLOYED
    assert opd_1.status == OperationStatus.IN_PROGRESS


@patch('bms_app.services.status_handlers.operation_detail.RmanLogFileParser.log_file_exists')
@patch('bms_app.services.status_handlers.operation_detail.RmanLogFileParser.validate',
       side_effect=RmanLogFileError(['err1', 'err2']))
def test_si_pre_restore_complete_with_rman_validation_errors(rman_validate_mock, rman_exist_mock, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, wave=None)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
    op_d_1 = OperationDetailsFactory(
        wave=None,
        mapping=map_1,
        operation=op_1,
        operation_type='PRE_RESTORE'
    )

    msg_data = {
        'operation_id': op_1.id,
        'hostnames': ['oracle-bms-vm1'],
        'host_status': 'COMPLETE'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert db_1.status == SourceDBStatus.PRE_RESTORE_FAILED

    assert rman_validate_mock.called

    assert db.session.query(OperationDetailsError)\
        .filter(OperationDetailsError.operation_details_id == op_d_1.id)\
        .count() == 2


# def test_rac_pre_restore_fail_if_one_host_fail(client):
#     """Test to check the correct update of the status of the database.
#
#     Don't allow update db status to PRE_RESTORE_COMPLETE
#     if at least one of RAC db instance during migration is failed.
#     """
#     pr = ProjectFactory()
#     db_1 = SourceDBFactory(project=pr, wave=None, db_type=SourceDBType.RAC)
#     bms_1 = BMSServerFactory(name='oracle-bms-vm1')
#     bms_2 = BMSServerFactory(name='oracle-bms-vm2')
#     map_1 = MappingFactory(source_db=db_1, bms=bms_1)
#     map_2 = MappingFactory(source_db=db_1, bms=bms_2)
#     op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_1,
#         operation=op_1,
#         operation_type='PRE_RESTORE',
#         status=OperationStatus.COMPLETE
#     )
#     OperationDetailsFactory(wave=None, mapping=map_2, operation=op_1, operation_type='PRE_RESTORE')
#
#     msg_data = {
#         'operation_id': op_1.id,
#         'hostnames': [bms_2.name],
#         'host_status': 'FAILED'
#     }
#     message['message']['data'] = encode(msg_data)
#     client.post(f'/webhooks/status', json=message)
#
#     assert db_1.status == SourceDBStatus.PRE_RESTORE_FAILED
#
#
# def test_pre_restore_rac_waits_all_host_finish(client):
#     """Test to check the correct update of the status of the database.
#
#     Correct status update during RAC migration
#     when waiting for all instances.
#     """
#     pr = ProjectFactory()
#     db_1 = SourceDBFactory(project=pr, wave=None, status=SourceDBStatus.DEPLOYED, db_type=SourceDBType.RAC)
#     bms_1 = BMSServerFactory(name='oracle-bms-vm1')
#     bms_2 = BMSServerFactory(name='oracle-bms-vm2')
#     bms_3 = BMSServerFactory(name='oracle-bms-vm3')
#     map_1 = MappingFactory(source_db=db_1, bms=bms_1)
#     map_2 = MappingFactory(source_db=db_1, bms=bms_2)
#     map_3 = MappingFactory(source_db=db_1, bms=bms_3)
#     op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_1,
#         operation=op_1,
#         operation_type='PRE_RESTORE',
#         status=OperationStatus.COMPLETE
#     )
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_2,
#         operation=op_1,
#         operation_type='PRE_RESTORE',
#         status=OperationStatus.IN_PROGRESS
#     )
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_3,
#         operation=op_1,
#         operation_type='PRE_RESTORE',
#         status=OperationStatus.IN_PROGRESS
#     )
#
#     msg_data = {
#         'operation_id': op_1.id,
#         'hostnames': [bms_2.name],
#         'host_status': 'COMPLETE'
#     }
#     message['message']['data'] = encode(msg_data)
#     client.post(f'/webhooks/status', json=message)
#
#     assert db_1.status == SourceDBStatus.DEPLOYED
#
#
# def test_pre_restore_rac_all_hosts_complete(client):
#     """Test to check the correct update of the status of the database.
#
#     Correct status update during RAC migration
#     when all instances were successful.
#     """
#     pr = ProjectFactory()
#     db_1 = SourceDBFactory(project=pr, wave=None, status=SourceDBStatus.DEPLOYED, db_type=SourceDBType.RAC)
#     bms_1 = BMSServerFactory(name='oracle-bms-vm1')
#     bms_2 = BMSServerFactory(name='oracle-bms-vm2')
#     bms_3 = BMSServerFactory(name='oracle-bms-vm3')
#     map_1 = MappingFactory(source_db=db_1, bms=bms_1)
#     map_2 = MappingFactory(source_db=db_1, bms=bms_2)
#     map_3 = MappingFactory(source_db=db_1, bms=bms_3)
#     op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_1,
#         operation=op_1,
#         operation_type='PRE_RESTORE',
#         status=OperationStatus.COMPLETE
#     )
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_2,
#         operation=op_1,
#         operation_type='PRE_RESTORE',
#         status=OperationStatus.IN_PROGRESS
#     )
#     OperationDetailsFactory(
#         wave=None,
#         mapping=map_3,
#         operation=op_1,
#         operation_type='PRE_RESTORE',
#         status=OperationStatus.COMPLETE
#     )
#
#     msg_data = {
#         'operation_id': op_1.id,
#         'hostnames': [bms_2.name],
#         'host_status': 'COMPLETE'
#     }
#     message['message']['data'] = encode(msg_data)
#     client.post(f'/webhooks/status', json=message)
#
#     assert db_1.status == SourceDBStatus.PRE_RESTORE_COMPLETE
#
#
# def test_pre_restore_rac_do_not_fail_if_all_host_do_not_finish(client):
#     """RAC waiting all nodes if at least one haven't finished yet."""
#     pr = ProjectFactory()
#     rac_db = SourceDBFactory(project=pr, wave=None, db_type=SourceDBType.RAC, status=SourceDBStatus.DEPLOYED)
#     rac_map_1 = MappingFactory(source_db=rac_db)
#     rac_map_2 = MappingFactory(source_db=rac_db)
#     op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
#     OperationDetailsFactory(wave=None, mapping=rac_map_1, operation=op_1, operation_type='PRE_RESTORE')
#     OperationDetailsFactory(wave=None, mapping=rac_map_2, operation=op_1, operation_type='PRE_RESTORE')
#
#     msg_data = {
#         'operation_id': op_1.id,
#         'hostnames': [rac_map_1.bms.name],
#         'host_status': 'FAILED'
#     }
#     message['message']['data'] = encode(msg_data)
#     client.post(f'/webhooks/status', json=message)
#
#     assert rac_db.status == SourceDBStatus.DEPLOYED
#
#
# def test_pre_restore_rac_fail_if_all_host_finish(client):
#     """RAC failed if all nodes fail."""
#     pr = ProjectFactory()
#     rac_db = SourceDBFactory(project=pr, wave=None, db_type=SourceDBType.RAC, status=SourceDBStatus.DEPLOYED)
#     rac_map_1 = MappingFactory(source_db=rac_db)
#     rac_map_2 = MappingFactory(source_db=rac_db)
#     op_1 = OperationFactory(wave=None, operation_type='PRE_RESTORE')
#     OperationDetailsFactory(wave=None, mapping=rac_map_1, operation=op_1, operation_type='PRE_RESTORE')
#     OperationDetailsFactory(
#         wave=None,
#         mapping=rac_map_2,
#         operation=op_1,
#         status=OperationStatus.FAILED,
#         operation_type='PRE_RESTORE')
#
#     msg_data = {
#         'operation_id': op_1.id,
#         'hostnames': [rac_map_1.bms.name],
#         'host_status': 'FAILED'
#     }
#     message['message']['data'] = encode(msg_data)
#     client.post(f'/webhooks/status', json=message)
#
#     assert rac_db.status == SourceDBStatus.PRE_RESTORE_FAILED
