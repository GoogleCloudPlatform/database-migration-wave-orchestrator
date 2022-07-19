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
    Operation, OperationDetails, OperationStatus, OperationType, SourceDBType
)
from bms_app.services.operations.wave import DeploymentService

from tests.factories import (
    BMSServerFactory, MappingFactory, ProjectFactory, SourceDBFactory,
    SourceDBStatus, WaveFactory
)


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.DeployControlNodeService.run')
def test_prevent_starting_running_wave(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test operation model."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr, is_running=True)

    assert wave.is_running

    with pytest.raises(ValidationError):
        DeploymentService().run(wave.id)

    assert wave.is_running


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.DeployControlNodeService.run')
def test_operation(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test operation model."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    MappingFactory(source_db=SourceDBFactory(wave=wave))

    assert not wave.is_running

    DeploymentService().run(wave.id)

    assert wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()

    assert operation
    assert operation.operation_type == OperationType.DEPLOYMENT
    assert operation.status == OperationStatus.STARTING
    assert operation.started_at
    assert not operation.completed_at
    assert operation.wave_id == wave.id


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.DeployControlNodeService.run')
def test_used_services(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test used services."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)
    MappingFactory(source_db=SourceDBFactory(wave=wave))

    assert not wave.is_running

    DeploymentService().run(wave.id)

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
@patch('bms_app.services.operations.wave.DeployControlNodeService.run')
def test_all_mappings_are_deployed(cn_mock, ans_run_mock, ans_init_mock , client):
    """Test that all wave mappings are deployed."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)

    db1 = SourceDBFactory(project=pr, wave=wave)
    db2 = SourceDBFactory(project=pr, wave=wave)

    bms1 = BMSServerFactory()
    bms2 = BMSServerFactory()

    m1 = MappingFactory(source_db=db1, bms=bms1)
    m2 = MappingFactory(source_db=db2, bms=bms2)

    assert not wave.is_running

    DeploymentService().run(wave.id)

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()
    assert operation

    op_details = OperationDetails.query.filter(
        OperationDetails.wave_id == wave.id,
        OperationDetails.operation_id == operation.id,
        OperationDetails.operation_type == OperationType.DEPLOYMENT,
        OperationDetails.status == OperationStatus.STARTING,
        OperationDetails.step == 'PRE_DEPLOYMENT',
    ).all()

    assert len(op_details) == 2
    assert set([op.mapping_id for op in op_details]) == {m1.id, m2.id}

    assert ans_init_mock.called
    assert ans_run_mock.called
    assert cn_mock.called


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.DeployControlNodeService.run')
def test_is_deployable_mappings(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test that only is_deployable mappings will be deployed."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)

    # create mapping that should be skipped by deployment
    db1 = SourceDBFactory(project=pr, wave=wave, status=SourceDBStatus.FAILED)
    db2 = SourceDBFactory(project=pr, wave=wave)
    db3 = SourceDBFactory(project=pr, wave=wave)

    bms1 = BMSServerFactory()
    bms2 = BMSServerFactory()
    bms3 = BMSServerFactory()


    MappingFactory(source_db=db1, bms=bms1)
    m2 = MappingFactory(source_db=db2, bms=bms2)
    m3 = MappingFactory(source_db=db3, bms=bms3)

    assert not wave.is_running

    DeploymentService().run(wave.id)

    assert wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()
    assert operation

    op_details = OperationDetails.query.filter(
        OperationDetails.wave_id == wave.id,
        OperationDetails.operation_id == operation.id,
        OperationDetails.operation_type == OperationType.DEPLOYMENT,
        OperationDetails.status == OperationStatus.STARTING,
        OperationDetails.step == 'PRE_DEPLOYMENT',
    ).all()

    assert len(op_details) == 2
    assert set([op.mapping_id for op in op_details]) == {m2.id, m3.id}

    assert ans_init_mock.called
    assert ans_run_mock.called
    assert cn_mock.called


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.DeployControlNodeService.run')
def test_bms_ids_param(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test deploymnet with provided list of databases to deploy."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)

    db1 = SourceDBFactory(project=pr, wave=wave)
    # db that should be deployed
    db2 = SourceDBFactory(project=pr, wave=wave)

    bms1 = BMSServerFactory()
    bms2 = BMSServerFactory()

    MappingFactory(source_db=db1, bms=bms1)
    # mapping for "db2"
    m2 = MappingFactory(source_db=db2, bms=bms2)

    assert not wave.is_running

    DeploymentService().run(wave.id, db_ids=[db2.id])

    assert wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()
    assert operation

    op_details = OperationDetails.query.filter(
        OperationDetails.wave_id == wave.id,
        OperationDetails.operation_id == operation.id,
        OperationDetails.operation_type == OperationType.DEPLOYMENT,
        OperationDetails.status == OperationStatus.STARTING,
        OperationDetails.step == 'PRE_DEPLOYMENT',
    ).all()

    assert len(op_details) == 1
    assert op_details[0].mapping_id == m2.id

    assert ans_init_mock.called
    assert ans_run_mock.called
    assert cn_mock.called


@patch('bms_app.services.operations.wave.BaseWaveOperation._start_pre_deployment', side_effect=Exception())
def test_pre_deployment_exception(mock, client):
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)

    db1 = SourceDBFactory(project=pr, wave=wave)
    db2 = SourceDBFactory(project=pr, wave=wave, db_type=SourceDBType.RAC)

    MappingFactory(source_db=db1)
    MappingFactory(source_db=db2)
    MappingFactory(source_db=db2)

    assert not wave.is_running

    DeploymentService().run(wave.id)

    assert not wave.is_running

    operation = Operation.query.filter(Operation.wave_id == wave.id).first()
    assert operation
    assert operation.status == OperationStatus.FAILED
    assert operation.completed_at

    assert db1.status is SourceDBStatus.FAILED
    assert db2.status is SourceDBStatus.FAILED

    op_details = OperationDetails.query.filter(
        OperationDetails.wave_id == wave.id,
        OperationDetails.operation_id == operation.id,
        OperationDetails.operation_type == OperationType.DEPLOYMENT,
        OperationDetails.status == OperationStatus.FAILED,
        OperationDetails.step == 'PRE_DEPLOYMENT',
    ).all()

    assert len(op_details) == 3
    assert all((op_d.completed_at for op_d in op_details))


@patch('bms_app.services.operations.wave.AnsibleConfigService.__init__', return_value=None)
@patch('bms_app.services.operations.wave.AnsibleConfigService.run')
@patch('bms_app.services.operations.wave.DeployControlNodeService.run')
def test_err_if_no_mappings(cn_mock, ans_run_mock, ans_init_mock, client):
    """Test operation model."""
    pr = ProjectFactory()
    wave = WaveFactory(project=pr)

    assert not wave.is_running

    with pytest.raises(ValidationError):
        DeploymentService().run(wave.id)

    assert not wave.is_running
    assert not Operation.query.count()
