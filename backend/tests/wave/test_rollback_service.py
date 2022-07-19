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

import pytest
from marshmallow import ValidationError

from bms_app.models import (
    Operation, OperationDetails, OperationStatus, OperationType, RestoreConfig,
    db
)
from bms_app.services.operations.wave import RollbackService

from tests.factories import (
    BMSServerFactory, MappingFactory, ProjectFactory, RestoreConfigFactory,
    SourceDBFactory, WaveFactory
)


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.RollbackConrolNodeService.run')
def test_prevent_starting_running_wave(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test used services."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr, is_running=True)

    assert wave.is_running

    with pytest.raises(ValidationError):
        RollbackService().run(wave.id, db_ids=[])

    assert wave.is_running



@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.RollbackConrolNodeService.run')
def test_used_services(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test used services."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    source_db = SourceDBFactory(wave=wave)
    MappingFactory(source_db=source_db)

    assert not wave.is_running

    RollbackService().run(wave.id, db_ids=[source_db.id])

    assert wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()

    assert ans_init_mock.called
    assert ans_run_mock.called

    assert ans_init_mock.call_args.args[1].startswith(f'wave_{wave.id}_{operation.id}_')

    assert cn_mock.call_args.kwargs['project'] == pr
    assert cn_mock.call_args.kwargs['operation'] == operation
    assert cn_mock.call_args.kwargs['gcs_config_dir'].startswith(f'wave_{wave.id}_{operation.id}_')
    assert cn_mock.call_args.kwargs['total_targets'] == 1
    assert cn_mock.call_args.kwargs['wave'] == wave
    assert cn_mock.called


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.RollbackConrolNodeService.run')
def test_bms_ids_param(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test deploymnet with provided list of databases to deploy."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)

    db1 = SourceDBFactory(project=pr, wave=wave)
    db2 = SourceDBFactory(project=pr, wave=wave)
    db3 = SourceDBFactory(project=pr, wave=wave)

    MappingFactory(source_db=db1)
    m2 = MappingFactory(source_db=db2)
    m3 = MappingFactory(source_db=db3)

    assert not wave.is_running

    RollbackService().run(wave.id, db_ids=[db2.id, db3.id])

    assert wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()

    assert operation
    assert operation.operation_type == OperationType.ROLLBACK
    assert operation.status == OperationStatus.STARTING
    assert operation.started_at
    assert not operation.completed_at
    assert operation.wave_id == wave.id

    op_details = OperationDetails.query.filter(
        OperationDetails.wave_id == wave.id,
        OperationDetails.operation_id == operation.id,
        OperationDetails.operation_type == OperationType.ROLLBACK,
        OperationDetails.status == OperationStatus.STARTING,
        OperationDetails.step == 'PRE_DEPLOYMENT',
    ).all()

    assert len(op_details) == 2
    assert {op.mapping_id for op in op_details} == set([m2.id, m3.id])

    assert ans_init_mock.called
    assert ans_run_mock.called
    assert cn_mock.called


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run', side_effect=Exception())
@patch('bms_app.services.operations.wave.RollbackConrolNodeService.run')
def test_ansible_service_exception(cn_mock, ans_run_mock, ans_init_mock, client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db1 = SourceDBFactory(project=pr, wave=wave)
    MappingFactory(source_db=db1, bms=BMSServerFactory())

    assert not wave.is_running

    RollbackService().run(wave.id, db_ids=[db1.id])

    assert not wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()
    assert operation
    assert operation.status == OperationStatus.FAILED
    assert operation.completed_at

    op_details = OperationDetails.query.filter(
        OperationDetails.wave_id == wave.id,
        OperationDetails.operation_id == operation.id,
        OperationDetails.operation_type == OperationType.ROLLBACK,
        OperationDetails.status == OperationStatus.FAILED,
        OperationDetails.step == 'PRE_DEPLOYMENT',
    ).all()

    assert len(op_details) == 1
    assert op_details[0].completed_at

    assert ans_init_mock.called
    assert ans_run_mock.called
    assert not cn_mock.called


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.RollbackConrolNodeService.run', side_effect=Exception())
def test_control_node_service_exception(cn_mock, ans_run_mock, ans_init_mock, client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db1 = SourceDBFactory(project=pr, wave=wave)
    MappingFactory(source_db=db1)

    assert not wave.is_running

    RollbackService().run(wave.id, db_ids=[db1.id])

    assert not wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()
    assert operation
    assert operation.status == OperationStatus.FAILED
    assert operation.completed_at

    op_details = OperationDetails.query.filter(
        OperationDetails.wave_id == wave.id,
        OperationDetails.operation_id == operation.id,
        OperationDetails.operation_type == OperationType.ROLLBACK,
        OperationDetails.status == OperationStatus.FAILED,
        OperationDetails.step == 'PRE_DEPLOYMENT',
    ).all()

    assert len(op_details) == 1
    assert op_details[0].completed_at

    assert ans_init_mock.called
    assert ans_run_mock.called
    assert cn_mock.called


@patch('bms_app.services.operations.wave.RollbackService._start_pre_deployment')
def test_restore_config_deletion_during_deployment_rollback(pre_deploy_mock, client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    db1 = SourceDBFactory(project=pr, wave=wave, status='DEPLOYED')
    MappingFactory(source_db=db1)
    RestoreConfigFactory(
        source_db=db1,
    )

    assert db.session.query(RestoreConfig).all()

    RollbackService().run(wave.id, db_ids=[db1.id])

    assert not db.session.query(RestoreConfig).all()
