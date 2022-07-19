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

import os
from unittest.mock import patch

import pytest
from marshmallow import ValidationError

from bms_app import settings
from bms_app.models import (
    Operation, OperationDetails, OperationStatus, SourceDB, SourceDBStatus,
    SourceDBType, db
)
from bms_app.services.operations.objects import DbMapping
from bms_app.services.operations.restore import RollbackRestoreOperation

from tests.factories import (
    BMSServerFactory, ConfigFactory, MappingFactory, ProjectFactory,
    RestoreConfigFactory, SourceDBFactory
)


@patch('bms_app.services.operations.restore.RollbackRestoreControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.operations.restore.AnsibleRollbackRestoreConfigService.run')
@patch('bms_app.services.operations.restore.AnsibleRollbackRestoreConfigService.__init__', return_value=None)
def test_run_rollback_restore_operation(ansible_init_mock, ansible_run_mock, gcs_mock, node_mock, client):
    """Test running restore operation"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DT_COMPLETE')
    ConfigFactory(source_db=db_1)
    RestoreConfigFactory(source_db=db_1)
    map_1 = MappingFactory(source_db=db_1)

    RollbackRestoreOperation().run(db_1.id)

    assert db_1.status == SourceDBStatus.DT_ROLLBACK

    operation = db.session.query(Operation) \
        .filter(Operation.status == 'STARTING') \
        .first()
    assert operation

    operation_details = db.session.query(OperationDetails) \
        .filter(OperationDetails.operation_id == operation.id) \
        .first()
    assert operation_details
    assert operation_details.status == OperationStatus.STARTING

    gcs_mock.assert_called_with(
        operation_id=operation.id
    )

    db_mappings_objects = DbMapping(db_1, [map_1])

    ansible_init_mock.assert_called_with(
        db_mappings_objects,
        gcs_mock.return_value
    )
    ansible_run_mock.assert_called_with()

    node_mock.assert_called_with(
        project=db_1.project,
        operation=operation,
        gcs_config_dir=gcs_mock.return_value,
        total_targets=1
    )


def test_validate_source_db_status_for_rollback_restore(client):
    """Test validate source db status"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DT')
    MappingFactory(source_db=db_1)

    with pytest.raises(ValidationError):
        RollbackRestoreOperation().run(db_1.id)


@patch('bms_app.services.operations.restore.BaseRestoreOperation._start_pre_deployment', side_effect=Exception())
def test_rollback_restore_operation_exception(pre_deploy_mock, client):
    """Test rollback restore operation failure"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DT_COMPLETE')
    MappingFactory(source_db=db_1)

    RollbackRestoreOperation().run(db_1.id)

    source_db = db.session.query(SourceDB).get(db_1.id)
    assert source_db.status == SourceDBStatus.DT_FAILED

    op = db.session.query(Operation).first()
    assert op.status == OperationStatus.FAILED

    op_det = db.session.query(OperationDetails) \
        .filter(OperationDetails.operation_id == op.id) \
        .first()
    assert op_det.status == OperationStatus.FAILED


@patch('bms_app.services.operations.restore.RollbackRestoreControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.ansible.restore.copy_blob')
@patch('bms_app.services.ansible.restore.AnsibleRollbackRestoreConfigService._upload_yaml')
def test_uploading_files_for_rollback_restore(upload_yaml_mock, copy_blob_mock, gcs_mock, node_mock, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DT_COMPLETE')
    bms = BMSServerFactory()
    MappingFactory(source_db=db_1, bms=bms)
    ConfigFactory(source_db=db_1)
    res_conf_1 = RestoreConfigFactory(
        source_db=db_1,
        pfile_file='restore_configs/1/pfile.ora'
    )

    RollbackRestoreOperation().run(db_1.id)

    upload_yaml_mock.assert_called_with(
        data={
            'all':
                {'children':
                    {'dbasm':
                        {'hosts':
                            {bms.name:
                                {'ansible_ssh_host': '172.25.9.8',
                                 'ansible_ssh_user': 'customeradmin',
                                 'ansible_ssh_private_key_file': '/root/.ssh/id_rsa_bms_toolkit',
                                 'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityAgent=no',
                                 'oracle_ver': db_1.oracle_version,
                                 'oracle_edition': db_1.oracle_edition,
                                 'db_name': 'ORCL',
                                 'compatible_rdbms': 'a',
                                 'oracle_user': 'oracle',
                                 'oracle_group': 'oinstall',
                                 'oracle_root': '/u01/app',
                                 'home_name': 'db_home19c',
                                 'sm_token': bms.secret_name,
                                 'swap_blk_device': '/dev/sda'
                                 }
                             }
                         }
                     }
                 }
        },
        file_name='inventory')

    copy_blob_mock.assert_called_with(
        settings.GCS_BUCKET,
        res_conf_1.pfile_file,
        settings.GCS_BUCKET,
        os.path.join(gcs_mock.return_value, 'pfile.ora')
    )


def test_error_if_rac(client):
    """Test validate source db type"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DT', db_type=SourceDBType.RAC)
    MappingFactory(source_db=db_1)

    with pytest.raises(ValidationError):
        RollbackRestoreOperation().run(db_1.id)
