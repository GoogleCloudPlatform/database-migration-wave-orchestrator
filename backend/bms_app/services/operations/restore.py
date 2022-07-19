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

import logging
from datetime import datetime

from marshmallow import ValidationError

from bms_app.models import (
    FAILOVER_ALLOWED_STATUSES, PRE_RESTORE_ALLOWED_STATUSES,
    RESTORE_ALLOWED_STATUSES, ROLLBACK_RESTORE_ALLOWED_STATUSES,
    OperationDetailsError, OperationType, SourceDB, SourceDBStatus, db
)
from bms_app.services.ansible.restore import (
    AnsibleFailOverConfigService, AnsiblePreRestoreConfigService,
    AnsibleRestoreConfigService, AnsibleRollbackRestoreConfigService
)
from bms_app.services.control_node import (
    FailOverControlNodeService, PreRestoreControlNodeService,
    RestoreControlNodeService, RollbackRestoreControlNodeService
)
from bms_app.services.disk_space_validator import (
    DiskSpaceError, DiskSpaceValidator
)
from bms_app.services.restore_config import RestoreConfigValidationsService
from bms_app.services.status_handlers.operation import (
    FailOverOperationStatusHandler, PreRestoreOperationStatusHandler,
    RestoreOperationStatusHandler, RollbackRestoreOperationStatusHandler
)
from bms_app.services.status_handlers.operation_detail import (
    PreRestoreOperationDetailStatusHandler
)

from .base import BaseOperation
from .db_mappings import get_restore_db_mappings_objects
from .utils import is_pre_restore_allowed, is_restore_allowed


logger = logging.getLogger(__name__)


class BaseRestoreOperation(BaseOperation):
    OPERATION_TYPE = None
    IN_PROGRESS_STATUS = None
    ALLOWED_STATUSES = None
    CONTROL_NODE_CLS = None
    GCS_CONFIG_DIR_TMPL = None
    ANSIBLE_SERVICE = None
    OPERATION_STATUS_HANDLER = None

    def __init_subclass__(cls, **kwargs):
        """Check if all required variables are set in subclasses."""
        super().__init_subclass__(**kwargs)

        required_attrs = (
            'OPERATION_TYPE', 'IN_PROGRESS_STATUS', 'ALLOWED_STATUSES',
            'CONTROL_NODE_CLS', 'GCS_CONFIG_DIR_TMPL', 'ANSIBLE_SERVICE',
            'OPERATION_STATUS_HANDLER'
        )
        missing_attrs = [
            attr for attr in required_attrs if getattr(cls, attr) is None
        ]
        if missing_attrs:
            raise NotImplementedError(
                f'{cls.__name__} missing required class variables: {missing_attrs}'
            )

    def run(self, db_id):
        source_db = db.session.query(SourceDB).with_for_update().get(db_id)
        self._validate_source_db(source_db)
        self._set_source_db_status(source_db)

        db_mappings_objects = get_restore_db_mappings_objects(db_id=db_id)
        self._validate_db_mappings_objects(db_mappings_objects)

        operation = self._create_operation_model(wave_id=None)

        self._log(operation, db_mappings_objects)

        operation_details = self._create_operation_details_models(
            operation,
            db_mappings_objects
        )

        try:
            self._run_operation(
                source_db,
                operation,
                operation_details,
                db_mappings_objects
            )
        except Exception:
            logger.exception(
                'Error starting %s %s',
                operation.id,
                operation.operation_type.value
            )
            self._handle_pre_deployment_failure(operation)

        db.session.commit()

    def _handle_pre_deployment_failure(self, operation):
        self.OPERATION_STATUS_HANDLER(
            operation,
            completed_at=datetime.now()
        ).terminate()

    def _run_operation(self, source_db, operation,
                       operation_details, db_mappings_objects):
        return self._start_pre_deployment(
            source_db,
            operation,
            db_mappings_objects
        )

    def _start_pre_deployment(self, source_db, operation,
                              db_mappings_objects):
        """Generate ansible configs and start control node."""
        gcs_config_dir = self._get_gcs_config_dir(operation_id=operation.id)

        db_mappings_object = db_mappings_objects[0]
        # generate and upload ansible config files
        self.ANSIBLE_SERVICE(
            db_mappings_object,
            gcs_config_dir
        ).run()

        cn_context = self.get_control_node_context(
            source_db,
            operation,
            db_mappings_objects
        )

        # run control node
        self.CONTROL_NODE_CLS.run(
            project=source_db.project,
            operation=operation,
            gcs_config_dir=gcs_config_dir,
            **cn_context
        )

    @classmethod
    def _validate_source_db(cls, source_db):
        if not source_db:
            raise ValidationError(
                {'db_id': ['db not found']}
            )

        if source_db.is_rac:
            raise ValidationError(
                {'db_id': ['restore operations for RAC is not supported']}
            )

        cls._extra_validate_source_db(source_db)

    @classmethod
    def _extra_validate_source_db(cls, source_db):
        if source_db.status not in cls.ALLOWED_STATUSES:
            raise ValidationError(
                {'db_id': [f'wrong db status: {source_db.status}']}
            )

    @classmethod
    def _set_source_db_status(cls, source_db):
        source_db.status = cls.IN_PROGRESS_STATUS
        db.session.add(source_db)
        db.session.commit()

    def get_control_node_context(self, source_db,
                                 operation, db_mappings_objects):
        """Data to pass to startup script template for contorl node."""
        context = {
            'total_targets': self._count_total_targets(db_mappings_objects)
        }
        return context


class PreRestoreOperation(BaseRestoreOperation):
    OPERATION_TYPE = OperationType.PRE_RESTORE
    IN_PROGRESS_STATUS = SourceDBStatus.PRE_RESTORE
    ALLOWED_STATUSES = PRE_RESTORE_ALLOWED_STATUSES
    CONTROL_NODE_CLS = PreRestoreControlNodeService
    GCS_CONFIG_DIR_TMPL = 'pre_restore_{operation_id}_{dt}'
    ANSIBLE_SERVICE = AnsiblePreRestoreConfigService
    OPERATION_STATUS_HANDLER = PreRestoreOperationStatusHandler

    def _run_operation(self, source_db, operation,
                       operation_details, db_mappings_objects):
        """Run pre-restore operation.

        Depending on RestoreConfig.validations possible options to run are:
        - rman validations (requires starting control node)
        - disk space validation (does not require control node)
        - both: rman and disk space validation
        """
        rcv = RestoreConfigValidationsService(source_db)

        if rcv.needs_rman_validation() \
                and not rcv.needs_disk_space_validation():
            # start control node only
            # operation will be closed as usually by msg from pubsub
            self._start_pre_deployment(
                source_db,
                operation,
                db_mappings_objects,
            )
        elif not rcv.needs_rman_validation() \
                and rcv.needs_disk_space_validation():
            # run only disk space validation
            # and finish/close operation depending on the validation result
            now = datetime.now()
            opd_handler = PreRestoreOperationDetailStatusHandler(
                operation_details[0],
                now,
            )

            is_valid = self._run_disk_space_validation(
                source_db,
                operation_details[0]
            )

            if is_valid:
                opd_handler.set_complete()
            else:
                opd_handler.set_fail()

            self.OPERATION_STATUS_HANDLER(
                operation,
                completed_at=now,
            ).finish()

        elif rcv.needs_disk_space_validation() \
                and rcv.needs_disk_space_validation():
            # start contorl node and run disk space validation
            # operation will be closed as usually by msg from pubsub
            self._run_disk_space_validation(
                source_db,
                operation_details[0]
            )
            self._start_pre_deployment(
                source_db,
                operation,
                db_mappings_objects,
            )

    @staticmethod
    def _run_disk_space_validation(source_db, operation_detail):
        """Return whether validation was successfull or not."""
        is_valid = True

        try:
            DiskSpaceValidator(source_db).validate()
        except DiskSpaceError:
            is_valid = False

            err = OperationDetailsError(
                operation_details_id=operation_detail.id,
                message='disk space error'
            )
            db.session.add(err)
            db.session.flush()

        return is_valid

    @classmethod
    def _extra_validate_source_db(cls, source_db):
        if not is_pre_restore_allowed(source_db):
            raise ValidationError(
                {'db_id': ['operation is not allowed']}
            )

    def get_control_node_context(self, source_db,
                                 operation, db_mappings_objects):
        context = super().get_control_node_context(
            source_db,
            operation,
            db_mappings_objects
        )
        context['source_db'] = source_db
        return context


class RestoreOperation(BaseRestoreOperation):
    OPERATION_TYPE = OperationType.BACKUP_RESTORE
    IN_PROGRESS_STATUS = SourceDBStatus.DT
    ALLOWED_STATUSES = RESTORE_ALLOWED_STATUSES
    CONTROL_NODE_CLS = RestoreControlNodeService
    GCS_CONFIG_DIR_TMPL = 'restore_{operation_id}_{dt}'
    ANSIBLE_SERVICE = AnsibleRestoreConfigService
    OPERATION_STATUS_HANDLER = RestoreOperationStatusHandler

    def get_control_node_context(self, source_db,
                                 operation, db_mappings_objects):
        context = super().get_control_node_context(
            source_db,
            operation,
            db_mappings_objects
        )
        context['source_db'] = source_db
        return context

    @classmethod
    def _extra_validate_source_db(cls, source_db):
        if not is_restore_allowed(source_db):
            raise ValidationError(
                {'db_id': ['operation is not allowed']}
            )


class RollbackRestoreOperation(BaseRestoreOperation):
    OPERATION_TYPE = OperationType.ROLLBACK_RESTORE
    IN_PROGRESS_STATUS = SourceDBStatus.DT_ROLLBACK
    ALLOWED_STATUSES = ROLLBACK_RESTORE_ALLOWED_STATUSES
    CONTROL_NODE_CLS = RollbackRestoreControlNodeService
    GCS_CONFIG_DIR_TMPL = 'dt_rollback_{operation_id}_{dt}'
    ANSIBLE_SERVICE = AnsibleRollbackRestoreConfigService
    OPERATION_STATUS_HANDLER = RollbackRestoreOperationStatusHandler


class FailOverOperation(BaseRestoreOperation):
    OPERATION_TYPE = OperationType.DB_FAILOVER
    IN_PROGRESS_STATUS = SourceDBStatus.FAILOVER
    ALLOWED_STATUSES = FAILOVER_ALLOWED_STATUSES
    CONTROL_NODE_CLS = FailOverControlNodeService
    GCS_CONFIG_DIR_TMPL = 'dt_failover_{operation_id}_{dt}'
    ANSIBLE_SERVICE = AnsibleFailOverConfigService
    OPERATION_STATUS_HANDLER = FailOverOperationStatusHandler
