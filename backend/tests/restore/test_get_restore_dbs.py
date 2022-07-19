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
from bms_app.restore.services import GetSourceDBAPIService

from tests.factories import (
    BMSServerFactory, MappingFactory, OperationDetailsErrorFactory,
    OperationDetailsFactory, OperationFactory, ProjectFactory,
    RestoreConfigFactory, ScheduledTaskFactory, SourceDBFactory
)


@patch('bms_app.restore.services.generate_target_gcp_logs_link', return_value='http')
def test_get_list_dbs_ready_to_restore(log_mock, client):
    pr_1 = ProjectFactory()
    db_1 = SourceDBFactory(project=pr_1, status='DT', db_type='RAC')
    db_2 = SourceDBFactory(project=pr_1, status='DT', db_type='RAC')
    db_3 = SourceDBFactory(project=pr_1, status='DT', db_type='SI')
    db_4 = SourceDBFactory(project=pr_1, status='DEPLOYED')
    db_5 = SourceDBFactory(project=pr_1, status='EMPTY')

    conf_1 = RestoreConfigFactory(source_db=db_1, is_configured=True)
    RestoreConfigFactory(source_db=db_2)
    RestoreConfigFactory(source_db=db_3)
    RestoreConfigFactory(source_db=db_4, is_configured=True)

    bms_1 = BMSServerFactory()

    m11 = MappingFactory(source_db=db_1)
    m12 = MappingFactory(source_db=db_1)
    m13 = MappingFactory(source_db=db_1)

    m21 = MappingFactory(source_db=db_2)
    m22 = MappingFactory(source_db=db_2)
    m23 = MappingFactory(source_db=db_2)

    m31 = MappingFactory(source_db=db_3)

    m41 = MappingFactory(source_db=db_4, bms=bms_1)

    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    op_2 = OperationFactory(wave=None, operation_type='IMPORT_EXPORT')
    op_3 = OperationFactory(wave=None, operation_type='DATA_GUARD')
    op_4 = OperationFactory(wave=None, operation_type='DEPLOYMENT', status='COMPLETE')

    OperationDetailsFactory(operation=op_1, mapping=m11)
    OperationDetailsFactory(operation=op_1, mapping=m12)
    OperationDetailsFactory(operation=op_1, mapping=m13)

    OperationDetailsFactory(operation=op_1, mapping=m21)
    OperationDetailsFactory(operation=op_1, mapping=m22)
    OperationDetailsFactory(operation=op_1, mapping=m23)

    OperationDetailsFactory(operation=op_3, mapping=m11)
    OperationDetailsFactory(operation=op_3, mapping=m13)

    OperationDetailsFactory(operation=op_2, mapping=m31)

    opd_4 = OperationDetailsFactory(operation=op_4, mapping=m41)
    err_1 = OperationDetailsErrorFactory(operation_details=opd_4)
    err_2 = OperationDetailsErrorFactory(operation_details=opd_4)

    req = client.get(f'/api/restore/source-dbs')
    data = req.json

    assert data

    assert len(data['data']) == 4

    assert data['data'][0]['is_configure']
    assert not data['data'][1]['is_configure']

    assert len(data['data'][0]['bms']) == 3
    assert len(data['data'][2]['bms']) == 1

    assert data['data'][0]['operation_type'] == OperationType.DATA_GUARD.value

    assert data['data'][3] == {
        'server': db_4.server,
        'id': db_4.id,
        'db_name': db_4.db_name,
        'db_type': db_4.db_type.value,
        'status': db_4.status.value,
        'ready_to_restore': False,
        'is_configure': True,
        'bms': [
            {
                'id': bms_1.id,
                'name': bms_1.name,
                'logs_url': log_mock.return_value,
            }
        ],
        'scheduled_task': {},
        'operation_type': op_4.operation_type.value,
        'operation_status': op_4.status.value,
        'operation_id': op_4.id,
        'started_at': op_4.started_at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'completed_at': op_4.completed_at,
        'errors': 2,
        'next_operation': ['restore']
    }


@patch('bms_app.restore.services.generate_target_gcp_logs_link', return_value='http')
def test_get_info_about_scheduled_db(log_mock, client):
    pr_1 = ProjectFactory()
    db_1 = SourceDBFactory(project=pr_1, status='DT', db_type='SI')
    scheduled_task_1 = ScheduledTaskFactory(source_db=db_1)
    RestoreConfigFactory(source_db=db_1, is_configured=True)
    bms_1 = BMSServerFactory()
    m1 = MappingFactory(source_db=db_1, bms=bms_1)
    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    opd_1 = OperationDetailsFactory(operation=op_1, mapping=m1)

    req = client.get(f'/api/restore/source-dbs')
    data = req.json

    assert data['data'][0] == {
        'server': db_1.server,
        'id': db_1.id,
        'db_name': db_1.db_name,
        'db_type': db_1.db_type.value,
        'status': db_1.status.value,
        'ready_to_restore': False,
        'is_configure': True,
        'bms': [
            {
                'id': bms_1.id,
                'name': bms_1.name,
                'logs_url': log_mock.return_value,
            }
        ],
        'scheduled_task': {
            'completed': False,
            'id': scheduled_task_1.id,
            'schedule_time': scheduled_task_1.schedule_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
        },
        'operation_type': op_1.operation_type.value,
        'operation_status': op_1.status.value,
        'started_at': op_1.started_at.strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'completed_at': op_1.completed_at,
        'operation_id': op_1.id,
        'errors': 0,
        'next_operation': []
    }


def test_filter_db_by_project(client):
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()

    db_1 = SourceDBFactory(project=pr_1, status='DT', db_type='RAC')
    db_2 = SourceDBFactory(project=pr_1, status='DT', db_type='SI')
    db_3 = SourceDBFactory(project=pr_1, status='DT', db_type='SI')
    db_4 = SourceDBFactory(project=pr_2, status='DEPLOYED')

    RestoreConfigFactory(source_db=db_1)
    RestoreConfigFactory(source_db=db_2)
    RestoreConfigFactory(source_db=db_3)
    RestoreConfigFactory(source_db=db_4)

    m11 = MappingFactory(source_db=db_1)
    m12 = MappingFactory(source_db=db_1)

    m21 = MappingFactory(source_db=db_2)

    m31 = MappingFactory(source_db=db_3)

    m41 = MappingFactory(source_db=db_4)

    op_1 = OperationFactory(wave=None, operation_type='BACKUP_RESTORE')
    op_2 = OperationFactory(wave=None, operation_type='DEPLOYMENT', status='COMPLETE')

    OperationDetailsFactory(operation=op_1, mapping=m11)
    OperationDetailsFactory(operation=op_1, mapping=m12)

    OperationDetailsFactory(operation=op_1, mapping=m21)

    OperationDetailsFactory(operation=op_1, mapping=m31)

    OperationDetailsFactory(operation=op_2, mapping=m41)

    sbd_project_1 = GetSourceDBAPIService.run(project_id=1)
    assert len(sbd_project_1) == 3

    sbd_project_2 = GetSourceDBAPIService.run(project_id=2)
    assert len(sbd_project_2) == 1


def test_next_operation_field_calculation(client):
    pr = ProjectFactory()
    db_1 = SourceDBFactory(project=pr, status='DEPLOYED')  # run_pre_restore=False =============> ['restore']
    db_2 = SourceDBFactory(project=pr, status='DEPLOYED')  # run_pre_restore=True ==============> ['pre-restore']
    db_3 = SourceDBFactory(project=pr, status='DEPLOYED')  # without RestoreConfig =============> []
    db_4 = SourceDBFactory(project=pr, status='PRE_RESTORE')  # run_pre_restore=False ==========> []
    db_5 = SourceDBFactory(project=pr, status='PRE_RESTORE')  # run_pre_restore=True ===========> []
    db_6 = SourceDBFactory(project=pr, status='PRE_RESTORE')  # without RestoreConfig ==========> []
    db_7 = SourceDBFactory(project=pr, status='PRE_RESTORE_COMPLETE')  # run_pre_restore=False => ['restore']
    db_8 = SourceDBFactory(project=pr, status='PRE_RESTORE_COMPLETE')  # run_pre_restore=True ==> ['pre_restore', 'restore']
    db_9 = SourceDBFactory(project=pr, status='PRE_RESTORE_COMPLETE')  # without RestoreConfig => ['pre_restore']
    db_10 = SourceDBFactory(project=pr, status='PRE_RESTORE_FAILED')  # run_pre_restore=False ===> ['restore']
    db_11 = SourceDBFactory(project=pr, status='PRE_RESTORE_FAILED')  # run_pre_restore=True ====> ['pre_restore']
    db_12 = SourceDBFactory(project=pr, status='PRE_RESTORE_FAILED')  # without RestoreConfig ===> []
    db_13 = SourceDBFactory(project=pr, status='DT')  # run_pre_restore=False ===================> []
    db_14 = SourceDBFactory(project=pr, status='DT')  # run_pre_restore=True ====================> []
    db_15 = SourceDBFactory(project=pr, status='DT')  # without RestoreConfig ===================> []
    db_16 = SourceDBFactory(project=pr, status='DT_COMPLETE')  # run_pre_restore=False ==========> ['restore', 'rollback_restore', 'failover']
    db_17 = SourceDBFactory(project=pr, status='DT_COMPLETE')  # run_pre_restore=True ===========> ['restore', 'rollback_restore', 'failover']
    db_18 = SourceDBFactory(project=pr, status='DT_COMPLETE')  # without RestoreConfig ==========> ['rollback_restore', 'failover']
    db_19 = SourceDBFactory(project=pr, status='DT_FAILED')  # run_pre_restore=False ============> ['rollback_restore']
    db_20 = SourceDBFactory(project=pr, status='DT_FAILED')  # run_pre_restore=True =============> ['rollback_restore']
    db_21 = SourceDBFactory(project=pr, status='DT_FAILED')  # without RestoreConfig ============> ['rollback_restore']
    db_22 = SourceDBFactory(project=pr, status='DT_PARTIALLY')  # run_pre_restore=False =========> ['restore', 'rollback_restore']
    db_23 = SourceDBFactory(project=pr, status='DT_PARTIALLY')  # run_pre_restore=True ==========> ['restore', 'rollback_restore']
    db_24 = SourceDBFactory(project=pr, status='DT_PARTIALLY')  # without RestoreConfig =========> ['rollback_restore']
    db_25 = SourceDBFactory(project=pr, status='DT_ROLLBACK')  # run_pre_restore=False ==========> []
    db_26 = SourceDBFactory(project=pr, status='DT_ROLLBACK')  # run_pre_restore=True ===========> []
    db_27 = SourceDBFactory(project=pr, status='DT_ROLLBACK')  # without RestoreConfig ==========> []
    db_28 = SourceDBFactory(project=pr, status='FAILOVER')  # run_pre_restore=False =============> []
    db_29 = SourceDBFactory(project=pr, status='FAILOVER')  # run_pre_restore=True ==============> []
    db_30 = SourceDBFactory(project=pr, status='FAILOVER')  # without RestoreConfig =============> []
    db_31 = SourceDBFactory(project=pr, status='FAILOVER_COMPLETE')  # run_pre_restore=False ====> ['rollback_restore']
    db_32 = SourceDBFactory(project=pr, status='FAILOVER_COMPLETE')  # run_pre_restore=True =====> ['rollback_restore']
    db_33 = SourceDBFactory(project=pr, status='FAILOVER_COMPLETE')  # without RestoreConfig ====> ['rollback_restore']
    db_34 = SourceDBFactory(project=pr, status='FAILOVER_FAILED')  # run_pre_restore=False ======> ['restore', 'rollback_restore']
    db_35 = SourceDBFactory(project=pr, status='FAILOVER_FAILED')  # run_pre_restore=True =======> ['restore', 'rollback_restore']
    db_36 = SourceDBFactory(project=pr, status='FAILOVER_FAILED')  # without RestoreConfig ======> ['rollback_restore']

    RestoreConfigFactory(source_db=db_1, is_configured=True)
    RestoreConfigFactory(source_db=db_2, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_4)
    RestoreConfigFactory(source_db=db_5, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_7, is_configured=True)
    RestoreConfigFactory(source_db=db_8, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_10, is_configured=True)
    RestoreConfigFactory(source_db=db_11, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_13)
    RestoreConfigFactory(source_db=db_14, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_16, is_configured=True)
    RestoreConfigFactory(source_db=db_17, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_19)
    RestoreConfigFactory(source_db=db_20, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_22, is_configured=True)
    RestoreConfigFactory(source_db=db_23, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_25)
    RestoreConfigFactory(source_db=db_26, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_28)
    RestoreConfigFactory(source_db=db_29, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_31)
    RestoreConfigFactory(source_db=db_32, is_configured=True, run_pre_restore=True)
    RestoreConfigFactory(source_db=db_34, is_configured=True)
    RestoreConfigFactory(source_db=db_35, is_configured=True, run_pre_restore=True)

    MappingFactory(source_db=db_1)
    MappingFactory(source_db=db_2)
    MappingFactory(source_db=db_3)
    MappingFactory(source_db=db_4)
    MappingFactory(source_db=db_5)
    MappingFactory(source_db=db_6)
    MappingFactory(source_db=db_7)
    MappingFactory(source_db=db_8)
    MappingFactory(source_db=db_9)
    MappingFactory(source_db=db_10)
    MappingFactory(source_db=db_11)
    MappingFactory(source_db=db_12)
    MappingFactory(source_db=db_13)
    MappingFactory(source_db=db_14)
    MappingFactory(source_db=db_15)
    MappingFactory(source_db=db_16)
    MappingFactory(source_db=db_17)
    MappingFactory(source_db=db_18)
    MappingFactory(source_db=db_19)
    MappingFactory(source_db=db_20)
    MappingFactory(source_db=db_21)
    MappingFactory(source_db=db_22)
    MappingFactory(source_db=db_23)
    MappingFactory(source_db=db_24)
    MappingFactory(source_db=db_25)
    MappingFactory(source_db=db_26)
    MappingFactory(source_db=db_27)
    MappingFactory(source_db=db_28)
    MappingFactory(source_db=db_29)
    MappingFactory(source_db=db_30)
    MappingFactory(source_db=db_31)
    MappingFactory(source_db=db_32)
    MappingFactory(source_db=db_33)
    MappingFactory(source_db=db_34)
    MappingFactory(source_db=db_35)
    MappingFactory(source_db=db_36)

    req = client.get(f'/api/restore/source-dbs')
    data = req.json

    assert data['data'][0]['next_operation'] == ['restore']
    assert data['data'][1]['next_operation'] == ['pre_restore']
    assert data['data'][2]['next_operation'] == []
    assert data['data'][3]['next_operation'] == []
    assert data['data'][4]['next_operation'] == []
    assert data['data'][5]['next_operation'] == []
    assert data['data'][6]['next_operation'] == ['restore']
    assert data['data'][7]['next_operation'] == ['pre_restore', 'restore']
    assert data['data'][8]['next_operation'] == []
    assert data['data'][9]['next_operation'] == ['restore']
    assert data['data'][10]['next_operation'] == ['pre_restore']
    assert data['data'][11]['next_operation'] == []
    assert data['data'][12]['next_operation'] == []
    assert data['data'][13]['next_operation'] == []
    assert data['data'][14]['next_operation'] == []
    assert data['data'][15]['next_operation'] == ['restore', 'rollback_restore', 'failover']
    assert data['data'][16]['next_operation'] == ['restore', 'rollback_restore', 'failover']
    assert data['data'][17]['next_operation'] == ['rollback_restore', 'failover']
    assert data['data'][18]['next_operation'] == ['rollback_restore']
    assert data['data'][19]['next_operation'] == ['rollback_restore']
    assert data['data'][20]['next_operation'] == ['rollback_restore']
    assert data['data'][21]['next_operation'] == ['restore', 'rollback_restore']
    assert data['data'][22]['next_operation'] == ['restore', 'rollback_restore']
    assert data['data'][23]['next_operation'] == ['rollback_restore']
    assert data['data'][24]['next_operation'] == []
    assert data['data'][25]['next_operation'] == []
    assert data['data'][26]['next_operation'] == []
    assert data['data'][27]['next_operation'] == []
    assert data['data'][28]['next_operation'] == []
    assert data['data'][29]['next_operation'] == []
    assert data['data'][30]['next_operation'] == ['rollback_restore']
    assert data['data'][31]['next_operation'] == ['rollback_restore']
    assert data['data'][32]['next_operation'] == ['rollback_restore']
    assert data['data'][33]['next_operation'] == ['restore', 'rollback_restore']
    assert data['data'][34]['next_operation'] == ['restore', 'rollback_restore']
    assert data['data'][35]['next_operation'] == ['rollback_restore']
