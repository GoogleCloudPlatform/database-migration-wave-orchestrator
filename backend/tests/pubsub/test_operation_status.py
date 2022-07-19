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

from bms_app.models import OperationStatus

from tests.factories import (
    MappingFactory, OperationDetailsFactory, OperationFactory, ProjectFactory,
    WaveFactory
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


def test_operation_status_is_optional(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr, is_running=True)
    map_1 = MappingFactory()
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=map_1,
                            operation=op_1, status=OperationStatus.STARTING)

    msg_data = {'wave_id': wave.id, 'operation_id': op_1.id}
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_1.status == OperationStatus.STARTING
    assert not op_1.completed_at
    assert wave.is_running


def test_operation_in_progress(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr, is_running=True)
    map_1 = MappingFactory()
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=map_1,
                            operation=op_1, status=OperationStatus.STARTING)

    msg_data = {'wave_id': wave.id,
                'operation_id': op_1.id,
                'status': 'IN_PROGRESS'}
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_1.status == OperationStatus.IN_PROGRESS
    assert not op_1.completed_at
    assert wave.is_running


def test_operation_complete(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    map_1 = MappingFactory()
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=map_1,
                            operation=op_1, status=OperationStatus.COMPLETE)
    map_2 = MappingFactory()
    OperationDetailsFactory(wave=wave, mapping=map_2,
                            operation=op_1, status=OperationStatus.COMPLETE)

    msg_data = {'wave_id': wave.id,
                'operation_id': op_1.id,
                'status': 'FINISHED'}
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_1.status == OperationStatus.COMPLETE
    assert op_1.completed_at
    assert not wave.is_running


def test_operation_failed(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    map_1 = MappingFactory()
    op_1 = OperationFactory(wave=wave)
    OperationDetailsFactory(wave=wave, mapping=map_1,
                            operation=op_1, status=OperationStatus.COMPLETE)
    map_2 = MappingFactory()
    OperationDetailsFactory(wave=wave, mapping=map_2,
                            operation=op_1, status=OperationStatus.FAILED)

    msg_data = {'wave_id': wave.id,
                'operation_id': op_1.id,
                'status': 'FINISHED'}
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_1.status == OperationStatus.FAILED
    assert op_1.completed_at
    assert not wave.is_running
