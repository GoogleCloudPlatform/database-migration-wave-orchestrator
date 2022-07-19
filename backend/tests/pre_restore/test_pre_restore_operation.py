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

from bms_app import settings
from bms_app.models import (
    Operation, OperationDetails, OperationDetailsError, OperationStatus,
    SourceDB, SourceDBStatus, db
)
from bms_app.services.disk_space_validator import DiskSpaceError
from bms_app.services.operations.objects import DbMapping
from bms_app.services.operations.restore import PreRestoreOperation

from tests.factories import (
    BMSServerFactory, ConfigFactory, MappingFactory, ProjectFactory,
    RestoreConfigFactory, SourceDBFactory
)


@patch('bms_app.operation.views.PreRestoreOperation.run')
def test_pre_restore_operation_api(mock, client):
    db_1 = SourceDBFactory(status=SourceDBStatus.DEPLOYED)
    RestoreConfigFactory(
        source_db=db_1,
        is_configured=True,
        run_pre_restore=True
    )

    req = client.post('/api/operations/pre-restores', json={'db_id': db_1.id})

    assert req.status_code == 201

    mock.assert_called_with(db_id=db_1.id)


@patch('bms_app.services.operations.restore.DiskSpaceValidator')
@patch('bms_app.services.operations.restore.PreRestoreControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.run')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.__init__', return_value=None)
def test_run_rman_validations(ansible_init_mock, ansible_run_mock, gcs_mock,
                              node_mock, disk_space_val_mock, client):
    """Test run pre restore operation"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    RestoreConfigFactory(
        source_db=db_1,
        is_configured=True,
        run_pre_restore=True,
        validations=['RMAN> crosscheck backup']
    )
    map_1 = MappingFactory(source_db=db_1)

    PreRestoreOperation().run(db_1.id)

    source_db_1 = db.session.query(SourceDB).get(db_1.id)

    assert source_db_1
    assert source_db_1.status == SourceDBStatus.PRE_RESTORE

    operation = db.session.query(Operation).first()
    assert operation
    assert operation.status == OperationStatus.STARTING

    operation_details = db.session.query(OperationDetails) \
        .filter(OperationDetails.operation_id == operation.id) \
        .first()
    assert operation_details
    assert operation_details.status == OperationStatus.STARTING

    gcs_mock.assert_called_with(
        operation_id=operation.id
    )

    db_mappings_objects = DbMapping(db_1, [map_1])

    total_targets = sum([len(obj.mappings) for obj in [db_mappings_objects]])

    ansible_init_mock.assert_called_with(
        db_mappings_objects,
        gcs_mock.return_value
    )
    ansible_run_mock.assert_called_with()

    node_mock.assert_called_with(
        project=db_1.project,
        operation=operation,
        gcs_config_dir=gcs_mock.return_value,
        total_targets=total_targets,
        source_db=db_1,
    )

    assert not disk_space_val_mock.called


@patch('bms_app.services.operations.restore.DiskSpaceValidator')
@patch('bms_app.services.operations.restore.PreRestoreControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.run')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.__init__', return_value=None)
def test_run_rman_and_disk_space_validations(ansible_init_mock, ansible_run_mock, gcs_mock,
                              node_mock, disk_space_val_mock, client):
    """Test run pre restore operation"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    RestoreConfigFactory(
        source_db=db_1,
        is_configured=True,
        run_pre_restore=True,
        validations=['RMAN> crosscheck backup', 'disk space validation']
    )
    map_1 = MappingFactory(source_db=db_1)

    PreRestoreOperation().run(db_1.id)

    source_db_1 = db.session.query(SourceDB).get(db_1.id)

    assert source_db_1
    assert source_db_1.status == SourceDBStatus.PRE_RESTORE

    operation = db.session.query(Operation).first()
    assert operation
    assert operation.status == OperationStatus.STARTING

    operation_details = db.session.query(OperationDetails) \
        .filter(OperationDetails.operation_id == operation.id) \
        .first()
    assert operation_details
    assert operation_details.status == OperationStatus.STARTING

    gcs_mock.assert_called_with(
        operation_id=operation.id
    )

    db_mappings_objects = DbMapping(db_1, [map_1])

    total_targets = sum([len(obj.mappings) for obj in [db_mappings_objects]])

    ansible_init_mock.assert_called_with(
        db_mappings_objects,
        gcs_mock.return_value
    )
    ansible_run_mock.assert_called_with()

    node_mock.assert_called_with(
        project=db_1.project,
        operation=operation,
        gcs_config_dir=gcs_mock.return_value,
        total_targets=total_targets,
        source_db=db_1,
    )

    assert disk_space_val_mock.called


@patch('bms_app.services.status_handlers.operation_detail.RmanLogFileParser')
@patch('bms_app.services.operations.restore.DiskSpaceValidator')
@patch('bms_app.services.operations.restore.PreRestoreControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.run')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.__init__', return_value=None)
def test_run_disk_space_complete_validations(ansible_init_mock, ansible_run_mock, gcs_mock,
                                             node_mock, disk_space_val_mock, rman_parser_mock,
                                             client):
    """Test run pre restore operation"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    RestoreConfigFactory(
        source_db=db_1,
        is_configured=True,
        run_pre_restore=True,
        validations=['disk space validation']
    )
    MappingFactory(source_db=db_1)

    PreRestoreOperation().run(db_1.id)

    assert db_1.status == SourceDBStatus.PRE_RESTORE_COMPLETE

    operation = db.session.query(Operation).first()
    assert operation.status == OperationStatus.COMPLETE
    assert operation.completed_at

    operation_details = db.session.query(OperationDetails) \
        .filter(OperationDetails.operation_id == operation.id) \
        .first()
    assert operation_details.status == OperationStatus.COMPLETE
    assert operation_details.completed_at

    assert not db.session.query(OperationDetailsError) \
        .filter(OperationDetailsError.operation_details_id == operation_details.id) \
        .count()

    assert disk_space_val_mock.called

    assert not rman_parser_mock.called
    assert not gcs_mock.called
    assert not ansible_init_mock.called
    assert not ansible_run_mock.called
    assert not node_mock.called


@patch('bms_app.services.status_handlers.operation_detail.RmanLogFileParser')
@patch('bms_app.services.operations.restore.DiskSpaceValidator', side_effect=DiskSpaceError(10, 20))
@patch('bms_app.services.operations.restore.PreRestoreControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.run')
@patch('bms_app.services.operations.restore.AnsiblePreRestoreConfigService.__init__', return_value=None)
def test_run_disk_space_fail_validations(ansible_init_mock, ansible_run_mock, gcs_mock,
                                         node_mock, disk_space_val_mock, rman_parser_mock,
                                         client):
    """Test run pre restore operation"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    RestoreConfigFactory(
        source_db=db_1,
        is_configured=True,
        run_pre_restore=True,
        validations=['disk space validation']
    )
    MappingFactory(source_db=db_1)

    PreRestoreOperation().run(db_1.id)

    assert db_1.status == SourceDBStatus.PRE_RESTORE_FAILED

    operation = db.session.query(Operation).first()
    assert operation.status == OperationStatus.FAILED
    assert operation.completed_at

    operation_details = db.session.query(OperationDetails) \
        .filter(OperationDetails.operation_id == operation.id) \
        .first()
    assert operation_details.status == OperationStatus.FAILED
    assert operation_details.completed_at

    assert db.session.query(OperationDetailsError) \
        .filter(OperationDetailsError.operation_details_id == operation_details.id) \
        .count()

    assert disk_space_val_mock.called

    assert not rman_parser_mock.called
    assert not gcs_mock.called
    assert not ansible_init_mock.called
    assert not ansible_run_mock.called
    assert not node_mock.called


@patch('bms_app.services.operations.restore.PreRestoreControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.ansible.restore.copy_blob')
@patch('bms_app.services.ansible.restore.AnsiblePreRestoreConfigService._upload_yaml')
def test_uploading_files_for_pre_restore(upload_yaml_mock, copy_blob_mock, gcs_mock, node_mock, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')
    bms = BMSServerFactory()
    MappingFactory(source_db=db_1, bms=bms)
    ConfigFactory(source_db=db_1)
    res_conf_1 = RestoreConfigFactory(
        is_configured=True,
        run_pre_restore=True,
        source_db=db_1,
        backup_location='oracle-bms-go3-inv/backup',
        pfile_file='restore_configs/1/pfile.ora',
        control_file='test',
        validations=['RMAN> crosscheck backup', 'RMAN> report unrecoverable']
    )

    PreRestoreOperation().run(db_1.id)

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
                                 'swap_blk_device': '/dev/sda',
                                 'backup_bucket': res_conf_1.backup_location.split('/')[0],
                                 'pfile_file': 'pfile.ora',
                                 'fuse_direct': True,
                                 'control_file': res_conf_1.control_file,
                                 'gcs_backup_folder': res_conf_1.backup_location.split('/')[1],
                                 'rman_commands': [
                                    'crosscheck backup',
                                    'report unrecoverable',
                                 ]
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
