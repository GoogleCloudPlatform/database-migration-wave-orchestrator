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

from bms_app.models import OperationType, Wave, db
from bms_app.services.ansible import AnsibleConfigService
from bms_app.services.control_node import (
    DeployControlNodeService, RollbackConrolNodeService
)
from bms_app.services.status_handlers.operation import (
    DeploymentOperationStatusHandler
)

from .base import BaseOperation
from .db_mappings import get_wave_db_mappings_objects


logger = logging.getLogger(__name__)


class BaseWaveOperation(BaseOperation):
    """Base class to run wave operations."""
    OPERATION_TYPE = None
    CONTROL_NODE_CLS = None
    FILTER_DEPLOYABLE_DBS_ONLY = None
    GCS_CONFIG_DIR_TMPL = 'wave_{wave_id}_{operation_id}_{dt}'

    def __init_subclass__(cls, **kwargs):
        """Check if all required variables are set in subclasses."""
        super().__init_subclass__(**kwargs)

        required_attrs = (
            'OPERATION_TYPE', 'CONTROL_NODE_CLS', 'FILTER_DEPLOYABLE_DBS_ONLY',
        )
        missing_attrs = [
            attr for attr in required_attrs if getattr(cls, attr) is None
        ]
        if missing_attrs:
            raise NotImplementedError(
                f'{cls.__name__} missing required class variables: {missing_attrs}'
            )

    def run(self, wave_id, db_ids=None):
        wave = Wave.query.with_for_update().get(wave_id)
        self._validate_wave_status(wave)

        db_mappings_objects = get_wave_db_mappings_objects(
            wave_id=wave_id,
            db_ids=db_ids,
            filter_deployable=self.FILTER_DEPLOYABLE_DBS_ONLY
        )
        self._validate_db_mappings_objects(db_mappings_objects)

        self._set_wave_status_running(wave)

        operation = self._create_operation_model(wave_id)

        self._log(operation, db_mappings_objects)

        self._create_operation_details_models(operation, db_mappings_objects)

        try:
            self._start_pre_deployment(
                wave,
                operation,
                db_mappings_objects
            )
        except Exception:
            logger.exception(
                'error starting %s %s', operation.operation_type.value, wave_id
            )
            self._handle_pre_deployment_failure(operation)

        self._post_operation_action(db_mappings_objects)

        db.session.commit()

    def _start_pre_deployment(self, wave, operation, db_mappings_objects):
        """Generate ansible configs and start control node."""
        gcs_config_dir = self._get_gcs_config_dir(
            wave_id=operation.wave_id,
            operation_id=operation.id
        )

        # generate and upload ansible config files
        AnsibleConfigService(
            db_mappings_objects,
            gcs_config_dir
        ).run()

        # run control node
        self.CONTROL_NODE_CLS.run(
            project=wave.project,
            operation=operation,
            gcs_config_dir=gcs_config_dir,
            wave=wave,
            total_targets=self._count_total_targets(db_mappings_objects),
        )

    @staticmethod
    def _validate_wave_status(wave):
        if wave.is_running:
            raise ValidationError({'wave': ['is already running']})

    @staticmethod
    def _set_wave_status_running(wave):
        wave.is_running = True
        db.session.add(wave)
        db.session.commit()

    @staticmethod
    def _handle_pre_deployment_failure(operation):
        DeploymentOperationStatusHandler(
            operation,
            completed_at=datetime.now()
        ).terminate()

    @staticmethod
    def _post_operation_action(db_mappings_objects):
        pass


class DeploymentService(BaseWaveOperation):
    FILTER_DEPLOYABLE_DBS_ONLY = True
    OPERATION_TYPE = OperationType.DEPLOYMENT
    CONTROL_NODE_CLS = DeployControlNodeService


class RollbackService(BaseWaveOperation):
    FILTER_DEPLOYABLE_DBS_ONLY = False
    OPERATION_TYPE = OperationType.ROLLBACK
    CONTROL_NODE_CLS = RollbackConrolNodeService

    def run(self, wave_id, db_ids):
        if not db_ids:
            raise ValidationError(
                {'db_ids': ['is required for rollback']}
            )
        super().run(wave_id, db_ids)

    @staticmethod
    def _post_operation_action(db_mappings_objects):
        for obj in db_mappings_objects:
            if obj.db.restore_config:
                db.session.delete(obj.db.restore_config)
