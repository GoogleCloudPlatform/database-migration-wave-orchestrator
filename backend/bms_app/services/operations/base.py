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
import os
from datetime import datetime

from marshmallow import ValidationError

from bms_app import settings
from bms_app.models import Operation, OperationDetails, OperationStatus, db


logger = logging.getLogger(__name__)


class BaseOperation:
    OPERATION_TYPE = None
    GCS_CONFIG_DIR_TMPL = None

    def _log(self, operation, db_mappings_objects):
        logger.debug(
            '%s operation: found %s dbs and %s targets ',
            operation.operation_type.value,
            len(db_mappings_objects),
            self._count_total_targets(db_mappings_objects)
        )

    def _create_operation_model(self, wave_id):
        operation = Operation(
            wave_id=wave_id,
            status=OperationStatus.STARTING,
            operation_type=self.OPERATION_TYPE,
        )
        db.session.add(operation)
        db.session.commit()

        return operation

    def _create_operation_details_models(self, operation, db_mappings_objects):
        operation_details_models = []
        all_mappings = [m for obj in db_mappings_objects for m in obj.mappings]

        for mapping in all_mappings:
            operation_details_models.append(
                OperationDetails(
                    mapping_id=mapping.id,
                    wave_id=operation.wave_id,
                    operation_id=operation.id,
                    status=OperationStatus.STARTING,
                    operation_type=self.OPERATION_TYPE,
                    step='PRE_DEPLOYMENT',
                )
            )

        db.session.add_all(operation_details_models)
        db.session.commit()

        return operation_details_models

    def _validate_db_mappings_objects(self, db_mappings_objects):
        if not db_mappings_objects \
                or not self._count_total_targets(db_mappings_objects):
            raise ValidationError(
                {'_schema': ['no db/mappings to run operation']}
            )

    @staticmethod
    def _count_total_targets(db_mappings_objects):
        return sum([len(obj.mappings)for obj in db_mappings_objects])

    @classmethod
    def _get_gcs_config_dir(cls, **kwargs):
        """Return full gcs prefix to specific operation configuration dir."""
        params = {'dt': datetime.now().strftime('%Y%m%d%H%M%S')}
        params.update(kwargs)

        config_dir = cls.GCS_CONFIG_DIR_TMPL.format(**params)

        return os.path.join(
            settings.GCS_DEPLOYMENT_CONFIG_PREFIX,
            config_dir
        )
