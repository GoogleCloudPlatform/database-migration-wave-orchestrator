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
    Operation, OperationDetails, OperationStatus, SourceDBStatus, db
)
from bms_app.services.operations.objects import DbMapping
from bms_app.services.operations.restore import FailOverOperation

from tests.factories import (
    BMSServerFactory, ConfigFactory, MappingFactory, ProjectFactory,
    RestoreConfigFactory, SourceDBFactory
)


@patch('bms_app.services.operations.restore.FailOverControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.operations.restore.AnsibleFailOverConfigService.run')
@patch('bms_app.services.operations.restore.AnsibleFailOverConfigService.__init__', return_value=None)
def test_run_failover_operation(ansible_init_mock, ansible_run_mock, gcs_mock, node_mock, client):
    """Test running failover operation"""
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DT_COMPLETE')
    ConfigFactory(source_db=db_1)
    RestoreConfigFactory(source_db=db_1)
    map_1 = MappingFactory(source_db=db_1)

    FailOverOperation().run(db_1.id)

    assert db_1.status == SourceDBStatus.FAILOVER

    operation = db.session.query(Operation) \
        .filter(Operation.status == 'STARTING') \
        .first()
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
        total_targets=total_targets
    )


@patch('bms_app.services.operations.restore.FailOverControlNodeService.run')
@patch('bms_app.services.operations.base.BaseOperation._get_gcs_config_dir')
@patch('bms_app.services.ansible.restore.upload_blob_from_string')
@patch('bms_app.services.ansible.restore.copy_blob')
@patch('bms_app.services.ansible.restore.AnsibleFailOverConfigService._upload_yaml')
def test_uploading_files_for_failover(upload_yaml_mock, copy_blob_mock, blob_from_string, gcs_mock, node_mock, client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DT_COMPLETE')
    bms = BMSServerFactory()
    MappingFactory(source_db=db_1, bms=bms)
    config = ConfigFactory(source_db=db_1)
    res_conf_1 = RestoreConfigFactory(
        source_db=db_1,
        pfile_file='restore_configs/1/pfile.ora'
    )

    FailOverOperation().run(db_1.id)

    upload_yaml_mock.assert_called_with(
        data={
            'all':
                {'children':
                    {'dbasm':
                        {'hosts':
                            {bms.name:
                                {
                                    'ansible_ssh_host': '172.25.9.8',
                                    'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityAgent=no',
                                    'ansible_ssh_private_key_file': '/root/.ssh/id_rsa_bms_toolkit',
                                    'ansible_ssh_user': 'customeradmin',
                                    'compatible_rdbms': config.misc_config_values['compatible_rdbms'],
                                    'db_name': config.db_params_values['db_name'],
                                    'home_name': config.install_config_values['home_name'],
                                    'oracle_edition': db_1.oracle_edition,
                                    'oracle_group': config.install_config_values['oracle_group'],
                                    'oracle_root': config.misc_config_values['oracle_root'],
                                    'oracle_user': config.install_config_values['oracle_user'],
                                    'oracle_ver': db_1.oracle_version,
                                    'sm_token': bms.secret_name,
                                    'swap_blk_device': config.misc_config_values['swap_blk_device']
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
