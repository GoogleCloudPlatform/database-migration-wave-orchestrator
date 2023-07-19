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

from bms_app.models import (
    FINISHED_OPERATION_STATUSES, OperationDetails, OperationStatus, Wave, db
)

from .operation_detail import (
    DeploymentOperationDetailStatusHandler,
    DMSDeploymentOperationDetailStatusHandler,
    FailOverOperationDetailStatusHandler,
    PreRestoreOperationDetailStatusHandler,
    RestoreOperationDetailStatusHandler, RollbackOperationDetailStatusHandler,
    RollbackRestoreOperationDetailStatusHandler
)


class BaseOperationStatusHandler:
    """Base class to process operation status changes."""
    OP_DETAILS_STATUS_HANDLER = None

    def __init__(self, operation, completed_at):
        self.operation = operation
        self.completed_at = completed_at

    def set_status(self, status):
        self.operation.status = status
        db.session.add(self.operation)

    def terminate(self):
        # check if operation status has been processed in the expected way
        # if operation if not in one of expected status
        # it means that something went wrong
        # and it make sense to mark operation as failed
        if self.operation.status not in FINISHED_OPERATION_STATUSES:
            self._fail_all_operation_details()
            self.finish()

    def finish(self):
        """Make all necessary actions to finish operation."""
        agg_status = self._calc_aggregated_operation_status()

        self.operation.status = agg_status
        self.operation.completed_at = self.completed_at

        self._post_finish()

        db.session.add(self.operation)

    def _post_finish(self):
        pass

    def _fail_all_operation_details(self):
        """Set all OperationDetails.status to FAILED."""
        qs = db.session.query(OperationDetails) \
            .filter(OperationDetails.operation_id == self.operation.id) \
            .all()

        # use OperationDetailStatusHandler to set source_db status correctly
        for op_detail in qs:
            self.OP_DETAILS_STATUS_HANDLER(
                op_detail,
                self.completed_at
            ).set_fail()

    def _calc_aggregated_operation_status(self):
        """Return aggregated operation status: 'COMPLETE/FAILED'

        FAILED - if at least one target/mapping is failed
        COMPLETE - if all are complete/successful
        """
        failed = OperationDetails.query.filter(
            OperationDetails.operation_id == self.operation.id,
            OperationDetails.status != OperationStatus.COMPLETE
        ).count()

        return OperationStatus.FAILED if failed else OperationStatus.COMPLETE


class DeploymentOperationStatusHandler(BaseOperationStatusHandler):
    """Handler to process Wave Operation status/step changes."""
    OP_DETAILS_STATUS_HANDLER = DeploymentOperationDetailStatusHandler

    def _post_finish(self):
        self._handle_wave()

    def _handle_wave(self):
        """Set wave.is_running = False."""
        Wave.query.filter(Wave.id == self.operation.wave_id) \
            .update({'is_running': False})

class DMSDeploymentOperationStatusHandler(DeploymentOperationStatusHandler):
    OP_DETAILS_STATUS_HANDLER = DMSDeploymentOperationDetailStatusHandler


class PreRestoreOperationStatusHandler(BaseOperationStatusHandler):
    """Handler to process Pre_restore Operation status/step changes."""
    OP_DETAILS_STATUS_HANDLER = PreRestoreOperationDetailStatusHandler


class RestoreOperationStatusHandler(BaseOperationStatusHandler):
    """Handler to process Restore Operation status/step changes."""
    OP_DETAILS_STATUS_HANDLER = RestoreOperationDetailStatusHandler


class RollbackOperationStatusHandler(DeploymentOperationStatusHandler):
    """Handler to process Rollback Operation status/step changes."""
    OP_DETAILS_STATUS_HANDLER = RollbackOperationDetailStatusHandler


class RollbackRestoreOperationStatusHandler(BaseOperationStatusHandler):
    """Handler to process Rollback Operation status/step changes."""
    OP_DETAILS_STATUS_HANDLER = RollbackRestoreOperationDetailStatusHandler


class FailOverOperationStatusHandler(BaseOperationStatusHandler):
    """Handler to process FailOver Operation status/step changes."""
    OP_DETAILS_STATUS_HANDLER = FailOverOperationDetailStatusHandler
