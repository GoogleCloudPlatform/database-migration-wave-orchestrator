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

from datetime import datetime
from unittest.mock import patch

from bms_app.services.utils import generate_target_gcp_logs_link

from tests.factories import BMSServerFactory, OperationDetailsFactory


def test_generate_logs_url(client):
    bms = BMSServerFactory()
    op_details = OperationDetailsFactory(
        started_at=datetime(2022, 1, 11, 11, 10, 10),
        completed_at=datetime(2022, 1, 11, 12, 12, 30),
    )

    url = generate_target_gcp_logs_link(op_details, bms)

    assert url == (
        'https://console.cloud.google.com/logs/query;'
        'query=logName%3D%22projects%2Ftest-gcp-project%2Flogs%2FBMS_LOG_RECEIVER'
        f'%22%0AjsonPayload.deploymentid%3D%22{op_details.operation_id}%22%0A'
        f'jsonPayload.targethost%3D%22{bms.name}%22;'
        'timeRange=2022-01-11T11:10:10.000000Z'
        '%2F2022-01-11T12:12:30.000000Z?project=test-gcp-project'
    )


@patch('bms_app.services.utils.datetime')
def test_generate_logs_url_with_completed_at_none(dt_mock, client):
    dt_mock.now.return_value = datetime(2022, 1, 11, 15, 20, 20)

    bms = BMSServerFactory()
    op_details = OperationDetailsFactory(
        started_at=datetime(2022, 1, 11, 11, 10, 10),
        completed_at=None,
    )

    url = generate_target_gcp_logs_link(op_details, bms)

    assert url == (
        'https://console.cloud.google.com/logs/query;'
        'query=logName%3D%22projects%2Ftest-gcp-project%2Flogs%2FBMS_LOG_RECEIVER'
        f'%22%0AjsonPayload.deploymentid%3D%22{op_details.operation_id}%22%0A'
        f'jsonPayload.targethost%3D%22{bms.name}%22;'
        'timeRange=2022-01-11T11:10:10.000000Z'
        '%2F2022-01-12T15:20:20.000000Z?project=test-gcp-project'
    )
