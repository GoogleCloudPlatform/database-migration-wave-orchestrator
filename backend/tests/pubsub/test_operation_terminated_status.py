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

from bms_app.models import OperationStatus, SourceDBStatus

from tests.factories import (
    MappingFactory, OperationDetailsFactory, OperationFactory, ProjectFactory,
    SourceDBFactory, WaveFactory
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
    '''Function to encode data for pubsub message'''
    data = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return data


def test_terminated_msg_status_if_operation_is_already_finished(client):
    """Nothing is affected by TERMINATED status."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr, is_running=True)
    db_1 = SourceDBFactory(status=SourceDBStatus.DEPLOYED)
    op_1 = OperationFactory(wave=wave, status=OperationStatus.COMPLETE)
    oph_1 = OperationDetailsFactory(
        wave=wave,
        operation=op_1,
        status=OperationStatus.COMPLETE,
        mapping=MappingFactory(source_db=db_1)
    )

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'status': 'TERMINATED'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_1.status == OperationStatus.COMPLETE
    assert oph_1.status == OperationStatus.COMPLETE
    assert db_1.status == SourceDBStatus.DEPLOYED


def test_finish_operation_by_terminated_msg(client):
    """Set all operation to FAILED."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr, is_running=True)
    op_1 = OperationFactory(wave=wave, status=OperationStatus.IN_PROGRESS)
    oph_1 = OperationDetailsFactory(
        wave=wave,
        operation=op_1,
        status=OperationStatus.IN_PROGRESS
    )
    oph_2 = OperationDetailsFactory(
        wave=wave,
        operation=op_1,
        status=OperationStatus.COMPLETE
    )

    msg_data = {
        'wave_id': wave.id,
        'operation_id': op_1.id,
        'status': 'TERMINATED'
    }
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_1.status == OperationStatus.FAILED
    assert op_1.completed_at
    assert oph_1.status == OperationStatus.FAILED
    assert oph_1.completed_at
    assert oph_2.status == OperationStatus.FAILED
    assert oph_2.completed_at
