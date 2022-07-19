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
from abc import ABC, abstractmethod

from flask import render_template

from bms_app import settings
from bms_app.services.gce import create_instance, get_zone


logger = logging.getLogger(__name__)


CREATE_INSTANCE_LOG = 'Starting GCE name: %s, zone: %s, project: %s, ' \
    'vpc: %s, subnet: %s, service_account: %s'


class BaseCNService(ABC):
    """Base class for launching Control Node."""

    OPERATION_TYPE = None

    @classmethod
    def run(cls, project, operation, gcs_config_dir, **context):
        """Start GCE control node."""
        zone = get_zone(settings.GCP_PROJECT_NAME, project.subnet)

        name = cls._generate_name(operation, context)

        raw_startup_script = cls._generate_startup_script(
            operation,
            gcs_config_dir,
            context
        )

        logger.debug(
            CREATE_INSTANCE_LOG,
            name, zone, settings.GCP_PROJECT_NAME,
            project.vpc, project.subnet, settings.GCP_SERVICE_ACCOUNT
        )

        machine_type = cls._get_machine_type(context)

        create_instance(
            project=settings.GCP_PROJECT_NAME,
            zone=zone,
            vpc=project.vpc,
            subnet=project.subnet,
            name=name,
            startup_script=raw_startup_script,
            service_account=settings.GCP_SERVICE_ACCOUNT,
            machine_type=machine_type,
        )

    @staticmethod
    @abstractmethod
    def _generate_name(operation, context):
        """Return GCE control node's name."""
        pass

    @classmethod
    def _generate_startup_script(cls, operation, gcs_config_dir, context):
        """Return GCE control node's startup script."""
        script_context = {
            'operation_id': operation.id,
            'bucket_name': settings.GCS_BUCKET,
            'gcs_config_dir': gcs_config_dir,
            'operation_type': cls.OPERATION_TYPE,
            'gcp_project_name': settings.GCP_PROJECT_NAME,
            'pubsub_topic': settings.GCP_PUBSUB_TOPIC,
        }
        extra_script_context = cls._get_extra_startup_script_context(
            operation,
            gcs_config_dir,
            context
        )
        script_context.update(extra_script_context)

        raw_startup_script = render_template(
            'runner.sh.j2',
            **script_context
        )

        return raw_startup_script

    @staticmethod
    @abstractmethod
    def _get_extra_startup_script_context(operation, gcs_config_dir, context):
        """Return additional data to render startup srcipt."""
        return {}

    @staticmethod
    def _get_machine_type(context):
        return 'e2-medium'


class WaveBaseCNService(BaseCNService):
    """Base class for Deployment and Rollback operations."""

    OPERATION_TYPE = None

    @staticmethod
    def _generate_name(operation, context):
        wave = context['wave']
        return f'bms-app-control-node-{wave.id}-{operation.id}'

    @staticmethod
    def _get_extra_startup_script_context(operation, gcs_config_dir, context):
        return {'wave_id': context['wave'].id}


class DeployControlNodeService(WaveBaseCNService):
    OPERATION_TYPE = 'DEPLOYMENT'

    @staticmethod
    def _get_machine_type(context):
        """Return machine type based on number of targets.

        Up to 25 tagrets - e2-standard-4
        25-75 targets - e2-standard-8
        75-100 targets - e2-standard-16

        """
        total_targets = context['total_targets']
        if total_targets < 25:
            machine_type = 'e2-standard-4'
        elif total_targets < 75:
            machine_type = 'e2-standard-8'
        else:
            machine_type = 'e2-standard-16'

        return machine_type


class RollbackConrolNodeService(WaveBaseCNService):
    OPERATION_TYPE = 'ROLLBACK'


class PreRestoreControlNodeService(BaseCNService):
    OPERATION_TYPE = 'PRE_RESTORE'

    @staticmethod
    def _generate_name(operation, context):
        return f'bms-app-control-node-pre-{operation.id}'

    @staticmethod
    def _get_extra_startup_script_context(operation, gcs_config_dir, context):
        source_db = context['source_db']
        return {
            'wave_id': 0,  # there is no 'wave' for restore operations
            'backup_type': source_db.restore_config.backup_type.value
        }


class RestoreControlNodeService(BaseCNService):
    OPERATION_TYPE = 'RESTORE'

    @staticmethod
    def _generate_name(operation, context):
        return f'bms-app-control-node-dt-{operation.id}'

    @staticmethod
    def _get_extra_startup_script_context(operation, gcs_config_dir, context):
        source_db = context['source_db']
        return {
            'wave_id': 0,  # there is no 'wave' for restore operations
            'backup_type': source_db.restore_config.backup_type.value
        }


class RollbackRestoreControlNodeService(BaseCNService):
    OPERATION_TYPE = 'ROLLBACK_RESTORE'

    @staticmethod
    def _generate_name(operation, context):
        return f'bms-app-control-node-dt-rollback-{operation.id}'

    @staticmethod
    def _get_extra_startup_script_context(operation, gcs_config_dir, context):
        return {
            'wave_id': 0,  # there is no 'wave' for restore operations
        }


class FailOverControlNodeService(BaseCNService):
    OPERATION_TYPE = 'DB_FAILOVER'

    @staticmethod
    def _generate_name(operation, context):
        return f'bms-app-control-node-dt-failover-{operation.id}'

    @staticmethod
    def _get_extra_startup_script_context(operation, gcs_config_dir, context):
        return {
            'wave_id': 0,  # there is no 'wave' for restore operations
        }
