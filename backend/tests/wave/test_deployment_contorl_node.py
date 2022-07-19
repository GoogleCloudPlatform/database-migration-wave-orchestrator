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

from bms_app.models import OperationType
from bms_app.services.operations.wave import DeployControlNodeService

from tests.factories import OperationFactory


@patch('bms_app.services.control_node.create_instance')
@patch('bms_app.services.control_node.get_zone', return_value='zone1')
def test_e2_standard_4_type(zmock, cr_inst_mock, client):
    operation = OperationFactory(operation_type=OperationType.ROLLBACK)

    DeployControlNodeService.run(
        project=operation.wave.project,
        operation=operation.wave.project,
        gcs_config_dir='config/dir',
        wave=operation.wave,
        total_targets=10,
    )

    assert zmock.called
    assert cr_inst_mock.called

    assert cr_inst_mock.call_args.kwargs['zone'] == 'zone1'
    assert cr_inst_mock.call_args.kwargs['machine_type'] == 'e2-standard-4'


@patch('bms_app.services.control_node.create_instance')
@patch('bms_app.services.control_node.get_zone', return_value='zone1')
def test_e2_standard_8_type(zmock, cr_inst_mock, client):
    operation = OperationFactory(operation_type=OperationType.ROLLBACK)

    DeployControlNodeService.run(
        project=operation.wave.project,
        operation=operation,
        gcs_config_dir='config/dir',
        wave=operation.wave,
        total_targets=50
    )

    assert zmock.called
    assert cr_inst_mock.called

    assert cr_inst_mock.call_args.kwargs['zone'] == 'zone1'
    assert cr_inst_mock.call_args.kwargs['machine_type'] == 'e2-standard-8'


@patch('bms_app.services.control_node.create_instance')
@patch('bms_app.services.control_node.get_zone', return_value='zone1')
def test_e2_standard_16_type(zmock, cr_inst_mock, client):
    operation = OperationFactory(operation_type=OperationType.ROLLBACK)

    DeployControlNodeService.run(
        project=operation.wave.project,
        operation=operation,
        gcs_config_dir='config/dir',
        wave=operation.wave,
        total_targets=80
    )

    assert zmock.called
    assert cr_inst_mock.called

    assert cr_inst_mock.call_args.kwargs['zone'] == 'zone1'
    assert cr_inst_mock.call_args.kwargs['machine_type'] == 'e2-standard-16'
