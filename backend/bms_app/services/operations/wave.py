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

from bms_app.models import SourceDB, Config, OperationType, Wave, db
from bms_app.schema import DMSConfigSchema
from bms_app.services.ansible import AnsibleConfigService
from bms_app.services.control_node import (
    DeployControlNodeService, RollbackConrolNodeService
)
from bms_app.services.status_handlers.operation import (
    DeploymentOperationStatusHandler
)
from bms_app.services.dms import DMS
from bms_app import settings
from google.cloud.workflows import executions

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
        except Exception as e:
            print(e)
            logger.exception(
                'error starting %s %s', operation.operation_type.value, wave_id
            )
            self._handle_pre_deployment_failure(operation)

        self._post_operation_action(db_mappings_objects)

        db.session.commit()
    
    def _get_dms_config(self, source_db: SourceDB) -> DMSConfigSchema:
        config: Config = db.session.query(Config).filter_by(db_id=source_db.id).one()
        schema = DMSConfigSchema()
        return schema.load(config.dms_config_values)

    def _start_dms_pre_deployment_local(self, wave, operation, dms_mappings):
        print('dms deployment started')
        dms = DMS(project_id=settings.GCP_PROJECT_NAME, region="us-central1")
        # TODO: do this async using operations callbacks
        for mapping in dms_mappings:
            config = self._get_dms_config(mapping.db)
            source_conn_name = f'waverunner-source-{mapping.db.db_name}'
            dest_conn_name = f'waverunner-target-for-{mapping.db.db_name}'
            job_name = f'waverunner-{mapping.db.db_name}'
            job_display_name = f'Waverunner job for {mapping.db.db_name}'
            print(f'Source DB config: {config}')

            def start_job(result):
                logger.info('starting job...')
                dms.start_migration_job(job_name)
            
            def create_job(result):
                logger.info('creating job...')
                dms.create_migration_job(
                    name=job_name,
                    display_name=job_display_name,
                    source_conn=source_conn_name,
                    destination_conn=dest_conn_name
                ).add_done_callback(start_job)
            
            def create_dest_connection(result):
                logger.info('creating destination connection...')
                dms.create_destination_connection_profile(
                    name=dest_conn_name,
                    source_conn_name=source_conn_name
                ).add_done_callback(create_job)
                
            logger.info('creating source connection...')
            dms.create_source_connection_profile(
                name=source_conn_name,
                host=mapping.db.server,
                port=config['port'],
                username=config['username'],
                password=config['password']
            ).add_done_callback(create_dest_connection)


    def _start_pre_deployment(self, wave, operation, db_mappings_objects):
        dms_mappings = list(filter(lambda mapping: mapping.is_dms, db_mappings_objects))
        bms_mappings = list(filter(lambda mapping: not mapping.is_dms, db_mappings_objects))

        print(f'dms: {dms_mappings}')
        print(f'bms: {bms_mappings}')

        self._start_dms_pre_deployment_local(wave, operation, dms_mappings)

        if not bms_mappings:
            return

        """Generate ansible configs and start control node."""
        gcs_config_dir = self._get_gcs_config_dir(
            wave_id=operation.wave_id,
            operation_id=operation.id
        )

        # generate and upload ansible config files
        AnsibleConfigService(
            bms_mappings,
            gcs_config_dir
        ).run()

        # run control node
        self.CONTROL_NODE_CLS.run(
            project=wave.project,
            operation=operation,
            gcs_config_dir=gcs_config_dir,
            wave=wave,
            total_targets=self._count_total_targets(bms_mappings),
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
