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

from bms_app.models import (
    FINISHED_OPERATION_STATUSES, Mapping, OperationDetails,
    OperationDetailsError, OperationStatus, SourceDB, SourceDBStatus, db
)
from bms_app.services.rman import RmanLogFileError, RmanLogFileParser


BMS_TOOLKIT_ERROR = 'bms toolkit error'


class BaseOperationDetailStatusHandler:
    """Base class to process OperationDetails status/step changes."""
    FAILED_STATUS = None
    COMPLETE_STATUS = None
    PARTIALLY_COMPLETE_STATUS = None

    def __init__(self, op_detail, completed_at):
        self.op_detail = op_detail
        self.completed_at = completed_at

    def set_step(self, step, timestamp):
        """Handle OperationDetails's step change."""
        self.op_detail.step = step
        self.op_detail.step_upd_at = datetime.fromtimestamp(timestamp)
        db.session.add(self.op_detail)

    def set_fail(self):
        """Set OperationDetails status to FAILED."""
        self.set_status(OperationStatus.FAILED, set_completed_at=True)

        # set source_db.status to FAILED
        source_db = self.op_detail.mapping.source_db
        if source_db.is_rac:
            self._handle_rac_node_failure(source_db)
        else:
            source_db.status = self.FAILED_STATUS

        db.session.add(source_db)

    def fail(self):
        """Handle pubsub's FAIL msg."""
        self.set_fail()

    def set_status(self, status, set_completed_at=False):
        """Set status only."""
        self.op_detail.status = status
        if set_completed_at:
            self.op_detail.completed_at = self.completed_at

        db.session.add(self.op_detail)

    def set_complete(self):
        """Set OperationDetails status as completed successfully."""
        self.set_status(OperationStatus.COMPLETE, set_completed_at=True)

        source_db = self.op_detail.mapping.source_db

        self._update_source_db_status_value(source_db)

    def complete(self):
        """Handle pubsub's COMPLETE msg."""
        return self.set_complete()

    def _handle_rac_node_failure(self, source_db):
        """Set the status only when all rac nodes have already finished."""
        all_nodes_statuses = self._get_all_rac_nodes_statuses(source_db)
        if self._all_rac_nodes_have_finished(all_nodes_statuses):
            source_db.status = self.FAILED_STATUS

    def _update_source_db_status_value(self, source_db):
        """Update SourceDb.status.

        Set it to "success_status" if:
            - Single instance
            - all RAC nodes are completed successfully too
        set it to SourceDBStatus.FAILED in other case.
        """
        if source_db.is_rac:
            all_nodes_statuses = self._get_all_rac_nodes_statuses(source_db)
            if self._all_rac_nodes_have_finished(all_nodes_statuses):
                if self._all_rac_nodes_complete(all_nodes_statuses):
                    source_db.status = self.COMPLETE_STATUS
                else:
                    source_db.status = self.FAILED_STATUS
        else:
            source_db.status = self.COMPLETE_STATUS

        db.session.add(source_db)

    def _get_all_rac_nodes_statuses(self, source_db):
        oph_statuses = db.session.query(OperationDetails.status) \
            .outerjoin(Mapping) \
            .filter(
                Mapping.db_id == source_db.id,
                OperationDetails.operation_id == self.op_detail.operation_id) \
            .all()
        return [x[0] for x in oph_statuses]

    @staticmethod
    def _all_rac_nodes_have_finished(all_nodes_statuses):
        """Return True/False if all rac nodes finished their operations."""
        return all(
            (x in FINISHED_OPERATION_STATUSES for x in all_nodes_statuses)
        )

    @staticmethod
    def _all_rac_nodes_complete(all_nodes_statuses):
        """Return True/False if all rac nodes finished successfully."""
        return all(x == OperationStatus.COMPLETE for x in all_nodes_statuses)


class DeploymentOperationDetailStatusHandler(BaseOperationDetailStatusHandler):
    """Handler to process Wave OperationDetails status/step changes."""
    FAILED_STATUS = SourceDBStatus.FAILED
    COMPLETE_STATUS = SourceDBStatus.DEPLOYED


class PreRestoreOperationDetailStatusHandler(BaseOperationDetailStatusHandler):
    """Handler to process Pre_restore OperationDetails status/step changes."""
    FAILED_STATUS = SourceDBStatus.PRE_RESTORE_FAILED
    COMPLETE_STATUS = SourceDBStatus.PRE_RESTORE_COMPLETE

    def run_extra_validation(self):
        """Check pre-restore rman log file."""
        rmp = RmanLogFileParser(self.op_detail.operation_id)

        if rmp.log_file_exists():
            try:
                RmanLogFileParser(self.op_detail.operation_id).validate()
            except RmanLogFileError as exc:
                self._save_validation_errors(exc.errors)

    def _save_validation_errors(self, errors):
        models = []

        for err in errors:
            models.append(
                OperationDetailsError(
                    operation_details_id=self.op_detail.id,
                    message=err
                )
            )

        db.session.add_all(models)
        db.session.flush()

    def complete(self):
        """Handle complete msg from pubsub.

        PreRestore operation requires parsing rman log file.
        If any error (ansible, rman, disp space valdiation) is found
        operation status is changed to FAILED
        """

        self.run_extra_validation()

        # set operation as FAILED it any error is found
        if self.is_error_found():
            self.set_fail()

        else:
            self.set_complete()

    def fail(self):
        # save bms toolkit error
        self._save_validation_errors([BMS_TOOLKIT_ERROR])

        self.run_extra_validation()

        self.set_fail()

    def is_error_found(self):
        """Check if any (bms toolkit, rman, disk space validation) is found"""
        return bool(
            db.session.query(OperationDetailsError)
            .filter(OperationDetailsError.operation_details_id == self.op_detail.id)
            .count()
        )

class RestoreOperationDetailStatusHandler(BaseOperationDetailStatusHandler):
    """Handler to process Restore OperationDetails status/step changes."""
    FAILED_STATUS = SourceDBStatus.DT_FAILED
    COMPLETE_STATUS = SourceDBStatus.DT_COMPLETE
    PARTIALLY_COMPLETE_STATUS = SourceDBStatus.DT_PARTIALLY

    def _update_source_db_status_value(self, source_db):
        if source_db.is_rac:
            all_nodes_statuses = self._get_all_rac_nodes_statuses(source_db)
            if self._all_rac_nodes_have_finished(all_nodes_statuses):
                if self._all_rac_nodes_complete(all_nodes_statuses):
                    source_db.status = self.COMPLETE_STATUS
                else:
                    self._set_restore_db_status(source_db)
        else:
            source_db.status = self.COMPLETE_STATUS

        db.session.add(source_db)

    def _handle_rac_node_failure(self, source_db):
        """Set the status only when all rac nodes have already finished."""

        all_nodes_statuses = self._get_all_rac_nodes_statuses(source_db)
        if self._all_rac_nodes_have_finished(all_nodes_statuses):
            self._set_restore_db_status(source_db)

    def _set_restore_db_status(self, source_db):
        first_node = db.session.query(OperationDetails) \
            .join(Mapping, OperationDetails.mapping_id == Mapping.id) \
            .join(SourceDB, Mapping.db_id == SourceDB.id) \
            .filter(SourceDB.id == self.op_detail.mapping.source_db.id) \
            .filter(Mapping.rac_node == 0).first()
        if first_node.status == OperationStatus.FAILED:
            source_db.status = self.FAILED_STATUS
        else:
            source_db.status = self.PARTIALLY_COMPLETE_STATUS


class RollbackOperationDetailStatusHandler(BaseOperationDetailStatusHandler):
    """Handler to process Rollback OperationDetails status/step changes."""
    FAILED_STATUS = SourceDBStatus.FAILED
    COMPLETE_STATUS = SourceDBStatus.ROLLBACKED


class RollbackRestoreOperationDetailStatusHandler(BaseOperationDetailStatusHandler):
    """Handler to process Rollback Restore OperationDetails status/step changes."""
    FAILED_STATUS = SourceDBStatus.DT_FAILED
    COMPLETE_STATUS = SourceDBStatus.DEPLOYED

    def _handle_rac_node_failure(self, source_db):
        raise NotImplementedError

    def _get_all_rac_nodes_statuses(self, source_db):
        raise NotImplementedError


class FailOverOperationDetailStatusHandler(BaseOperationDetailStatusHandler):
    """Handler to process Failover OperationDetails status/step changes."""
    FAILED_STATUS = SourceDBStatus.FAILOVER_FAILED
    COMPLETE_STATUS = SourceDBStatus.FAILOVER_COMPLETE

    def _handle_rac_node_failure(self, source_db):
        raise NotImplementedError

    def _get_all_rac_nodes_statuses(self, source_db):
        raise NotImplementedError
