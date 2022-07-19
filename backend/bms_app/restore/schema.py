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

from marshmallow import (
    Schema, ValidationError, fields, post_dump, validate, validates,
    validates_schema
)

from bms_app import ma
from bms_app.models import BackupType, RestoreConfig
from bms_app.pre_restore_validations import PRE_RESTORE_VALIDATIONS
from bms_app.services.gcs import create_file_link


VALIDATIONS_OPTIONS = [x['name'] for x in PRE_RESTORE_VALIDATIONS]


class RestoreConfigSchema(Schema):
    is_configured = fields.Boolean(required=True)
    backup_location = fields.Str(required=False, load_default='')
    rman_cmd = fields.Str(required=False, load_default='')
    pfile_content = fields.Str(required=False, load_default='')
    backup_type = fields.Str(required=False, load_default='')
    run_pre_restore = fields.Boolean(load_default=False)
    control_file = fields.Str(required=False, load_default='')
    validations = fields.List(fields.Str, load_default=list)

    @validates('validations')
    def validate_validations_options(self, value):
        if value:
            errors = [x for x in value if x not in VALIDATIONS_OPTIONS]
            if errors:
                raise ValidationError(f'incorrect values: {errors}')

    @validates_schema
    def validate_data_if_config_is_configured(self, data, **kwargs):
        """Validate that all data is set when 'is_configured'=True."""
        if data['is_configured']:
            required_fields = [
                'backup_location', 'rman_cmd', 'pfile_content',
                'backup_type', 'control_file'
            ]

            # validate pre-restore related fileds too
            if data['run_pre_restore']:
                required_fields.extend(['validations'])

            errors = [f for f in required_fields if not data.get(f)]

            if errors:
                raise ValidationError({f: 'is required' for f in errors})

            # validate backup_type
            validate.OneOf(BackupType.values())(data['backup_type'])


class RestoreConfigOutputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RestoreConfig
        fields = (
            'backup_location', 'rman_cmd', 'is_configured', 'backup_type',
            'control_file', 'pfile_file', 'pwd_file', 'tnsnames_file',
            'listener_file', 'run_pre_restore', 'validations'
        )

    backup_type = fields.Function(lambda obj: obj.backup_type.value)

    @post_dump(pass_original=True)
    def add_post_dump_data(self, data, obj, many):
        # add full gcs links
        data['pfile_file'] = create_file_link(obj.pfile_file) if obj.pfile_file else ''
        data['pwd_file'] = create_file_link(obj.pwd_file) if obj.pwd_file else ''
        data['tnsnames_file'] = create_file_link(obj.tnsnames_file) if obj.tnsnames_file else ''
        data['listener_file'] = create_file_link(obj.listener_file) if obj.listener_file else ''

        return data
