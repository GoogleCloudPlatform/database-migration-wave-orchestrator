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
    """Function to encode data for pubsub message."""
    data['timestamp'] = 123456789
    data = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
    return data


def test_step_is_optional(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db_1 = SourceDBFactory(project=pr, wave=wave)
    bms_1 = BMSServerFactory(name='oracle-bms-vm1')
    map_1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=wave)
    op_details = OperationDetailsFactory(
        wave=wave,
        mapping=map_1,
        operation=op_1
    )

    msg_data = {'wave_id': wave.id, 'operation_id': op_1.id}
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_details.step == 'PRE_DEPLOYMENT'


def test_correct_host_update(client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    bms_1 = BMSServerFactory()
    bms_2 = BMSServerFactory()
    bms_3 = BMSServerFactory()
    map_1 = MappingFactory(bms=bms_1)
    map_2 = MappingFactory(bms=bms_2)
    map_3 = MappingFactory(bms=bms_3)
    op_1 = OperationFactory(wave=wave)
    op_details_1 = OperationDetailsFactory(
        wave=wave,
        mapping=map_1,
        operation=op_1
    )
    op_details_2 = OperationDetailsFactory(
        wave=wave,
        mapping=map_2,
        operation=op_1
    )
    op_details_3 = OperationDetailsFactory(
        wave=wave,
        mapping=map_3,
        operation=op_1
    )

    msg_data = {'wave_id': wave.id,
                'operation_id': op_1.id,
                'hostnames': [bms_2.name, bms_3.name],
                'step': 'STEP1'}
    message['message']['data'] = encode(msg_data)

    client.post(f'/webhooks/status', json=message)

    assert op_details_1.step == 'PRE_DEPLOYMENT'
    assert op_details_2.step == 'STEP1'
    assert op_details_3.step == 'STEP1'

    assert not op_details_1.step_upd_at
    assert op_details_2.step_upd_at
    assert op_details_3.step_upd_at
