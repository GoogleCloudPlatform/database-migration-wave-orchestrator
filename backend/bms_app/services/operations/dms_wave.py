import logging

from google.cloud import secretmanager

from marshmallow import ValidationError
from typing import Sequence

from bms_app.models import OperationType, OperationDetails, OperationStatus, Config, Wave, SourceDB, db
from bms_app.schema import DMSConfigSchema
from bms_app.services.dms import DMS
from bms_app import settings
from .base import BaseOperation


logger = logging.getLogger(__name__)
secrets_client = secretmanager.SecretManagerServiceClient()

class DMSDeploymentService(BaseOperation):
    OPERATION_TYPE = OperationType.DMS_DEPLOYMENT

    def run(self, wave_id, db_ids=None):
        wave = Wave.query.with_for_update().get(wave_id)
        
        self._validate_wave_status(wave)

        # retrive source databases to be deployed
        # TODO: add db_ids filter
        source_dbs = db.session.query(SourceDB).filter(SourceDB.wave_id == wave_id).all()

        self._validate_source_databases(source_dbs)

        self._set_wave_status_running(wave)

        operation = self._create_operation_model(wave_id)

        self._log(operation, source_dbs)

        self._create_operation_details_models(operation)

        self._start_pre_deployment(source_dbs)

        db.session.commit()
    
    def _start_pre_deployment(self, source_dbs):
        for db in source_dbs:
            config = self._get_dms_config(db)
            logger.info(f'starting workflow for: {db.host}, with the following config: {config}')
    
    def _get_dms_config(self, source_db: SourceDB) -> DMSConfigSchema:
        config: Config = db.session.query(Config).filter_by(db_id=source_db.id).one()
        schema = DMSConfigSchema()
        dms_config: DMSConfigSchema = schema.load(config.dms_config_values)
        if dms_config['password_secret_id']:
            req = secretmanager.AccessSecretVersionRequest(
                name=secrets_client.secret_version_path(settings.GCP_PROJECT_NAME, dms_config['password_secret_id'], "latest")
            )
            res = secrets_client.access_secret_version(request=req)
            dms_config['password'] = res.payload.data.decode('UTF-8')
        return dms_config

    def _log(self, operation, source_dbs):
        logger.debug(
            '%s operation: found %s dbs',
            operation.operation_type.value,
            len(source_dbs),
        )
    
    def _create_operation_details_models(self, operation):
        operation_details = OperationDetails(
            wave_id=operation.wave_id,
            operation_id=operation.id,
            status=OperationStatus.STARTING,
            operation_type=self.OPERATION_TYPE,
            step='PRE_DEPLOYMENT',
        )
        db.session.add(operation_details)
        db.session.commit()

        return operation_details

    @staticmethod
    def _validate_wave_status(wave):
        if wave.is_running:
            raise ValidationError({'wave': ['is already running']})

    @staticmethod
    def _validate_source_databases(source_dbs: Sequence[SourceDB]):
        invalid_sources = []
        for db in source_dbs:
            if not db.is_dms_deployable:
                invalid_sources.append(db)
        
        if len(invalid_sources) > 0:
            invalid_sources_errors = [f'{db.server}: invalid source' for db in invalid_sources]
            raise ValidationError({'source_db': invalid_sources_errors})

    @staticmethod
    def _set_wave_status_running(wave):
        wave.is_running = True
        db.session.add(wave)
        db.session.commit()