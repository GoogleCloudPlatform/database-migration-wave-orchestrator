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
from collections import defaultdict

from marshmallow import ValidationError
from sqlalchemy import func

from bms_app import settings
from bms_app.models import (
    DATA_TRANSFER_DB_STATUSES, FAILOVER_ALLOWED_STATUSES,
    RESTORE_ALLOWED_STATUSES, ROLLBACK_RESTORE_ALLOWED_STATUSES, BMSServer,
    Mapping, Operation, OperationDetails, RestoreConfig, SourceDB, db
)
from bms_app.pre_restore_validations import PRE_RESTORE_VALIDATIONS
from bms_app.services.gcs import (
    delete_blob, upload_blob, upload_blob_from_string
)
from bms_app.services.operations.utils import (
    is_pre_restore_allowed, is_restore_allowed
)
from bms_app.services.scheduled_tasks import get_planned_task
from bms_app.services.utils import generate_target_gcp_logs_link
from bms_app.upload.views import StreamWrapper


def get_or_create_restore_config(source_db):
    restore_config = db.session.query(RestoreConfig) \
        .filter(RestoreConfig.db_id == source_db.id) \
        .first()

    if not restore_config:
        restore_config = RestoreConfig(db_id=source_db.id)

    return restore_config


def merge_validations(config_validations=None):
    """Merge RestoreConfig.validations with PRE_RESTORE_VALIDATIONS.

    Return list of all possible validations with flag
    which means whether it is enabled for the current restore config or not.
    """
    config_validations = config_validations or []
    merged_validations = []

    for item in PRE_RESTORE_VALIDATIONS:
        merged_validations.append({
            'name': item['name'],
            'description': item['description'],
            'enabled': item['name'] in config_validations
        })

    return merged_validations


class GetSourceDBAPIService:
    """Return list of dbs ready for or involved in Data Transfer."""
    @classmethod
    def run(cls, project_id):
        data = {}
        qs = db.session.query(SourceDB, RestoreConfig, BMSServer) \
            .outerjoin(RestoreConfig, SourceDB.id == RestoreConfig.db_id) \
            .join(Mapping, SourceDB.id == Mapping.db_id) \
            .join(BMSServer, Mapping.bms_id == BMSServer.id) \
            .filter(SourceDB.status.in_(DATA_TRANSFER_DB_STATUSES))

        if project_id:
            qs = qs.filter(SourceDB.project_id == project_id)

        unique_db_ids = set()

        for source_db, restore_config, bms in qs:
            db_id = source_db.id
            unique_db_ids.add(db_id)

            # add source db data only once
            if db_id not in data:
                item = cls._generate_item(source_db, restore_config)
                data[db_id] = item

                cls._add_scheduled_task(item, db_id)

            # there might be many bms targets
            # add all of them
            cls._add_bms_data(data[db_id], bms)

        # extend source db data with operations data
        cls._add_operation_data(data, unique_db_ids)

        return list(data.values())

    @classmethod
    def _generate_item(cls, source_db, restore_config):
        return {
            'server': source_db.server,
            'id': source_db.id,
            'db_name': source_db.db_name,
            'db_type': source_db.db_type.value,
            'status': source_db.status.value,
            'ready_to_restore': source_db.status in RESTORE_ALLOWED_STATUSES,
            'is_configure': restore_config.is_configured if restore_config else False,
            'bms': [],
            'errors': 0,
            'scheduled_task': {},
            'next_operation': cls._calculate_next_possible_operations(source_db)
        }

    @staticmethod
    def _calculate_next_possible_operations(source_db):
        next_operation = []
        if is_pre_restore_allowed(source_db):
            next_operation.append('pre_restore')
        if is_restore_allowed(source_db):
            next_operation.append('restore')
        if source_db.status in ROLLBACK_RESTORE_ALLOWED_STATUSES:
            next_operation.append('rollback_restore')
        if source_db.status in FAILOVER_ALLOWED_STATUSES:
            next_operation.append('failover')
        return next_operation

    @staticmethod
    def _add_bms_data(item, bms):
        item['bms'].append({
            'id': bms.id,
            'name': bms.name,
        })

    @staticmethod
    def _add_scheduled_task(item, db_id):
        task = get_planned_task(db_id)
        if task:
            item['scheduled_task'].update({
                'id': task.id,
                'schedule_time': task.schedule_time,
                'completed': task.completed
            })

    @classmethod
    def _add_operation_data(cls, data, unique_db_ids):
        """Add data about last operation.

        Get map of 'last operation' -> ['source db',...]
        Retrieve data about all 'last operation'
        Assign operation data to all source dbs involved in the operation
        """
        # get list of last operation id and corresponding db_id
        db_operation_data = db.session.query(Mapping, OperationDetails) \
            .with_entities(func.max(OperationDetails.operation_id),
                           Mapping.db_id) \
            .join(OperationDetails,
                  Mapping.id == OperationDetails.mapping_id) \
            .filter(Mapping.db_id.in_(unique_db_ids)) \
            .group_by(Mapping.db_id) \
            .all()

        # create a map operation_id -> [db_id] map
        # in order to track which db was involved in the specific operation
        operation_id_db_id_map = defaultdict(list)
        for op_id, db_id in db_operation_data:
            operation_id_db_id_map[op_id].append(db_id)

        # retrieve data about all last operations
        all_operation_ids = operation_id_db_id_map.keys()
        operations_data_qs = db.session.query(
            Operation, OperationDetails, BMSServer
        ) \
            .join(OperationDetails) \
            .join(Mapping) \
            .join(BMSServer, Mapping.bms_id == BMSServer.id) \
            .filter(Operation.id.in_(all_operation_ids))

        # extend 'data' with required info
        errors = defaultdict(set)  # collect unique errors per db

        for operation, op_details, bms_server in operations_data_qs:
            # add operation type/status to databases involved in the operation
            for db_id in operation_id_db_id_map[operation.id]:
                item = next((x for x in data.values() if x['id'] == db_id))

                cls._add_operation_info(item, operation)
                cls._add_logs_url(item, operation, op_details, bms_server)

                errors[db_id].update({x.message for x in op_details.errors})

        cls._add_errors(data, errors)

    @staticmethod
    def _add_operation_info(item, operation):
        """Add operation type/status/started_at/completed_at."""
        # 'operation' is multiplied because of join to 'op_details'
        # add it only once
        if 'operation_type' not in item:
            item.update({
                'operation_type': operation.operation_type.value,
                'operation_status': operation.status.value,
                'operation_id': operation.id,
                'started_at': operation.started_at,
                'completed_at': operation.completed_at
            })

    @staticmethod
    def _add_logs_url(item, operation, op_details, bms_server):
        """Add 'logs_url'."""
        bms_data = next(
            (x for x in item['bms'] if x['id'] == bms_server.id),
            None
        )
        if bms_data:
            bms_data.update({
                'logs_url': generate_target_gcp_logs_link(
                    op_details,
                    bms_server
                )
            })

    @staticmethod
    def _add_errors(data, errors):
        """Add errors count."""
        for item in data.values():
            if item['id'] in errors:
                item['errors'] = len(errors.get(item['id']))


class SaveConfigFileService:
    """Save file to GCS bucket and to RestoreConfig model"""
    @classmethod
    def run(cls, db_id, file_obj, file_name, config_field_name):
        source_db = SourceDB.query.get_or_404(db_id)

        if config_field_name == 'pfile_file':
            cls._validate_pfile_db_name(source_db, file_obj)

        gcs_key = cls._upload(db_id, file_name, file_obj)
        cls._update_restore_config(source_db, config_field_name, gcs_key)

        return gcs_key

    @staticmethod
    def _update_restore_config(source_db, config_field_name, gcs_key):
        restore_config = get_or_create_restore_config(source_db)

        setattr(restore_config, config_field_name, gcs_key)

        db.session.add(restore_config)
        db.session.commit()

    @staticmethod
    def _upload(db_id, file_name, file_obj):
        gcs_key = os.path.join(
            settings.GCP_RESTORE_CONFIGS_PREFIX,
            str(db_id),
            file_name
        )

        upload_blob(
            settings.GCS_BUCKET,
            gcs_key,
            StreamWrapper(file_obj)
        )

        return gcs_key

    @staticmethod
    def _validate_pfile_db_name(source_db, file_obj):
        """Compare db_name parameter in pfile with SourceDB.db_name """
        for data in file_obj.readlines():
            if data.decode().rstrip() == f'*.db_name=\'{source_db.db_name}\'':
                file_obj.seek(0)
                return

        raise ValidationError(
            ['please upload pfile corresponding to this database']
        )


class DeleteConfigFileService:
    """Delete file from GCS bucket and link to it from RestoreConfig model"""
    @classmethod
    def run(cls, restore_config, file_name, config_field_name):
        cls._delete_gcs_file(restore_config.db_id, file_name)

        setattr(restore_config, config_field_name, '')

        db.session.add(restore_config)
        db.session.commit()

    @staticmethod
    def _delete_gcs_file(db_id, file_name):
        """Delete gcs blob."""
        gcs_key = os.path.join(
            settings.GCP_RESTORE_CONFIGS_PREFIX,
            str(db_id),
            file_name
        )

        delete_blob(
            settings.GCS_BUCKET,
            gcs_key
        )


class CreateOrUpdateRestoreConfig:
    @classmethod
    def run(cls, source_db, data):
        restore_config = get_or_create_restore_config(source_db)

        cls._update_restore_config(restore_config, data)

        if data['pfile_content']:
            restore_config.pfile_file = cls._save_pfile_content(
                source_db.id,
                data['pfile_content']
            )
        elif restore_config.pfile_file and not data['pfile_content']:
            # pfile should be deleted if pfile_content is empty
            cls._delete_pfile(restore_config)

        db.session.add(restore_config)
        db.session.commit()

    @staticmethod
    def _update_restore_config(restore_config, data):
        restore_config.backup_location = data['backup_location']
        restore_config.rman_cmd = data['rman_cmd']
        restore_config.is_configured = data['is_configured']
        restore_config.backup_type = data['backup_type']
        restore_config.run_pre_restore = data['run_pre_restore']
        restore_config.control_file = data['control_file']
        restore_config.validations = data['validations']

    @staticmethod
    def _save_pfile_content(db_id, pfile_content):
        pfile_gcs_key = os.path.join(
            settings.GCP_RESTORE_CONFIGS_PREFIX,
            str(db_id),
            'pfile.ora'
        )
        upload_blob_from_string(
            settings.GCS_BUCKET,
            pfile_gcs_key,
            pfile_content
        )
        return pfile_gcs_key

    @staticmethod
    def _delete_pfile(restore_config):
        DeleteConfigFileService.run(
            restore_config,
            file_name='pfile.ora',
            config_field_name='pfile_file'
        )
