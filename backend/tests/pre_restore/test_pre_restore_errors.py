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

from tests.factories import (
    OperationDetailsErrorFactory, OperationDetailsFactory
)


@patch('bms_app.operation.views.RmanLogFileParser.get_cmd_output', return_value='text')
def test_pre_restore_errors(parser_mock, client):
    op_d = OperationDetailsFactory()
    err_1 = OperationDetailsErrorFactory(
        operation_details=op_d,
        message='error_1'
    )
    err_2 = OperationDetailsErrorFactory(
        operation_details=op_d,
        message='rman error'
    )

    req = client.get(f'api/operations/{op_d.operation_id}/errors')

    assert req.status_code == 200

    assert req.json == [
        {
            'name': err_1.message,
            'details': '',
        },
        {
            'name': err_2.message,
            'details': parser_mock.return_value,
        },
    ]
