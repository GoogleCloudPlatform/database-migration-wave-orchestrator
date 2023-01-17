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

from marshmallow import EXCLUDE, Schema, fields, post_load

from bms_app import ma
from bms_app.models import (
    BMSServer, Config, Mapping, Operation, OperationDetails, SourceDB,
    SourceDBType, db
)
from bms_app.schema import (
    ASMConfigSchema, DataMountSchema, DbParamsSchema, InstallConfigSchema,
    MiscConfigSchema, RACConfigSchema, CloudDMSSchema
)
from bms_app.services.utils import generate_target_gcp_logs_link


class InSourceDBSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = SourceDB
        unknown = EXCLUDE

    @post_load
    def db_type(self, data, many, **kwargs):
        if data['rac_nodes']:
            data['db_type'] = SourceDBType.RAC
        else:
            data['db_type'] = SourceDBType.SI

        return data


class ASMConfigItem(Schema):
    class Meta:
        unknown = EXCLUDE

    diskgroup = fields.Str()
    au_size = fields.Str()
    redundancy = fields.Str()


class InMiscConfig(Schema):
    class Meta:
        unknown = EXCLUDE

    compatible_asm = fields.Str()
    compatible_rdbms = fields.Str()


class InASMConfig(Schema):
    class Meta:
        unknown = EXCLUDE

    asm = fields.List(fields.Nested(ASMConfigItem))


in_db_schema = InSourceDBSchema(
    only=['server', 'oracle_version', 'arch', 'cores', 'ram',
          'allocated_memory', 'db_name', 'db_size', 'oracle_release',
          'rac_nodes']
)


def update_db_config(source_db, raw_db_data):
    """Update Config."""
    asm_data = InASMConfig().load(raw_db_data)
    misc_data = InMiscConfig().load(raw_db_data)

    upd_data = {
        'db_id': source_db.id,
        'asm_config_values': asm_data['asm'],
        'misc_config_values': misc_data

    }
    if source_db.config:
        db.session.query(Config) \
            .filter(Config.db_id == source_db.id) \
            .update(upd_data)
    else:
        config = Config(**upd_data)
        db.session.add(config)

    db.session.commit()


def update_db(source_db, raw_db_data):
    """Update SourceDB."""
    source_db_data = in_db_schema.load(raw_db_data)

    db.session.query(SourceDB) \
        .filter(SourceDB.id == source_db.id) \
        .update(source_db_data)
    db.session.commit()

    update_db_config(source_db, raw_db_data)


def add_db(raw_db_data, project_id):
    """Add SourceDB using parsed data"""
    source_db_data = in_db_schema.load(raw_db_data)
    source_db_data['project_id'] = project_id

    source_db = SourceDB(**source_db_data)
    db.session.add(source_db)
    db.session.commit()

    update_db_config(source_db, raw_db_data)


def save_source_dbs(parsed_dbs_data, overwrite, project_id):
    added = updated = skipped = 0

    for raw_db_data in parsed_dbs_data:
        source_db = db.session.query(SourceDB) \
            .filter(
                SourceDB.server == raw_db_data['server'],
                SourceDB.db_name == raw_db_data['db_name'],
                SourceDB.project_id == project_id)\
            .first()

        if source_db:
            if overwrite:
                deployment_exists = db.session.query(OperationDetails) \
                    .filter(Mapping.db_id == source_db.id) \
                    .filter(Mapping.id == OperationDetails.mapping_id) \
                    .count()

                if not deployment_exists:
                    update_db(source_db, raw_db_data)
                    updated += 1
                else:
                    skipped += 1
            else:
                skipped += 1
        else:
            add_db(raw_db_data, project_id)
            added += 1

    return {
        'added': added,
        'updated': updated,
        'skipped': skipped
    }


class SaveSourceDBConfigService:
    """Save/Update Config data.

    Perform data validation if is_configured
    Or save without any validation in other case (draft).
    """

    ATTR_SCHEMA_MAP = {
        'install_config_values': InstallConfigSchema(),
        'db_params_values': DbParamsSchema(),
        'data_mounts_values': DataMountSchema(many=True),
        'asm_config_values': ASMConfigSchema(many=True),
        'misc_config_values': MiscConfigSchema(),
        'rac_config_values': RACConfigSchema(),
        'cloud_dms_values': CloudDMSSchema(),
    }
    CONFIG_ATTRS = (
        'install_config_values', 'db_params_values', 'data_mounts_values',
        'asm_config_values', 'misc_config_values', 'rac_config_values'
    )

    @classmethod
    def run(cls, db_id, data):
        config = cls._get_config_obj(db_id)

        cls._update_config_values(config, data)

        db.session.add(config)
        db.session.commit()

        return config

    @classmethod
    def _update_config_values(cls, config, data):
        is_configured = cls._get_is_configured(data)

        if is_configured:
            value_getter = cls._get_validated_value
        else:
            value_getter = cls._get_draft_value

        config.is_configured = is_configured

        for attr in cls.CONFIG_ATTRS:
            value = value_getter(data, attr)
            setattr(config, attr, value)

    @staticmethod
    def _get_is_configured(data):
        """Return is_configured value"""
        is_configured = data.get('is_configured', False)

        if not isinstance(is_configured, bool):
            is_configured = str(is_configured).lower() != 'false'

        return is_configured

    @staticmethod
    def _get_config_obj(db_id):
        config = db.session.query(Config).filter(Config.db_id == db_id).first()

        if not config:
            config = Config(db_id=db_id)

        return config

    @staticmethod
    def _get_draft_value(data, attr):
        """Return data without any validation."""
        return data.get(attr)

    @classmethod
    def _get_validated_value(cls, data, attr):
        """Validate and return data."""
        if attr in data:
            schema = cls.ATTR_SCHEMA_MAP[attr]
            return schema.load(data[attr])


class SourceDBOperationsHistoryService:
    @classmethod
    def run(cls, source_db):
        data = cls._get_source_db_data(source_db)
        data['operations'] = cls._get_operations(source_db)

        return data

    @staticmethod
    def _get_operations(source_db):
        """Return operations history data."""
        query = db.session.query(OperationDetails, Operation, BMSServer) \
            .join(Mapping, OperationDetails.mapping_id == Mapping.id) \
            .join(SourceDB, Mapping.db_id == SourceDB.id) \
            .join(BMSServer, Mapping.bms_id == BMSServer.id) \
            .join(Operation, OperationDetails.operation_id == Operation.id) \
            .filter(SourceDB.id == source_db.id) \
            .order_by(OperationDetails.id) \
            .all()

        operations_data = {}

        for op_details, operation, bms in query:
            op_id = op_details.operation_id

            if op_id not in operations_data:
                operations_data[op_id] = {
                    'wave_id': operation.wave_id,
                    'operation_type': operation.operation_type.value,
                    'started_at': operation.started_at,
                    'completed_at': operation.completed_at,
                    'bms': []

                }

            logs_url = generate_target_gcp_logs_link(op_details, bms)

            operations_data[op_id]['bms'].append({
                'id': bms.id,
                'name': bms.name,
                'logs_url': logs_url,
                'operation_status': op_details.status.value
            })

        return list(operations_data.values())

    @staticmethod
    def _get_source_db_data(source_db):
        return {
            'id': source_db.id,
            'source_hostname': source_db.server,
            'db_name': source_db.db_name,
            'oracle_version': source_db.oracle_version,
            'db_type': source_db.db_type.value,
            'operations': [],
        }
