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

from marshmallow import Schema, ValidationError, fields, validates

from bms_app import ma
from bms_app.models import Config, Label, Operation, Project, Wave
from bms_app.validators import check_if_text, validate_project_id


# ORA_VERSIONS = ['19.3.0.0.0', '18.0.0.0.0', '12.2.0.1.0', '12.1.0.2.0', '11.2.0.4.0']
# ORA_EDITIONS = ['EE', 'SE', 'SE2']
# CLUSTER_TYPES = ['RAC', 'DG']
# DISK_GROUPS = ['DATA1', 'RECO1']


class WaveSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wave
        include_fk = True

    @validates('project_id')
    def validated_project_id_exists(self, value):
        validate_project_id(value)


class AddWaveSchema(Schema):
    name = fields.Str(required=True)
    project_id = fields.Int(required=True)
    db_ids = fields.List(fields.Int(), required=False)

    @validates('project_id')
    def validated_project_id_exists(self, value):
        validate_project_id(value)


class ProjectSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project


class OperationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Operation
        include_fk = True

    operation_type = fields.Function(lambda obj: obj.operation_type.value)
    status = fields.Function(lambda obj: obj.status.value)


class FileSchema(Schema):
    file = fields.Raw(required=True)


class TextFileSchema(Schema):
    file = fields.Raw(required=True)

    @validates('file')
    def validate_txt_file_format(self, file_object):
        file_object.seek(0)
        if not check_if_text(file_object):
            raise ValidationError(['file format has to be txt'])

    @validates('file')
    def validate_not_empty_file(self, file_object):
        file_object.seek(0)
        if not file_object.read():
            raise ValidationError(['file can not be empty'])


class BinaryFileSchema(Schema):
    file = fields.Raw(required=True)

    @validates('file')
    def validate_binary_file_format(self, file_object):
        if check_if_text(file_object):
            raise ValidationError(['file format has to be binary'])


class DbParamsSchema(Schema):
    # ora_version = fields.Str(validate=validate.OneOf(ORA_VERSIONS))
    # ora_edition = fields.Str(validate=validate.OneOf(ORA_EDITIONS), load_default='EE')
    db_name = fields.Str(load_default='ORCL')
    # ora_role_separation = fields.Boolean()
    # cluster_type = fields.Str(validate=validate.OneOf(CLUSTER_TYPES), missing=None)
    # scan_port = fields.Integer(load_default=1521)
    # oracle_user = fields.Str(load_default='oracle')
    # oracle_group = fields.Str(load_default='oinstall')
    # grid_user = fields.Str(load_default='grid')
    # grid_group = fields.Str(load_default='asmadmin')
    # oracle_root = fields.Str(load_default='/u01/app')
    # home_name = fields.Str(load_default='db_home1')
    #
    # @validates_schema
    # def validate_ora_edit_to_ora_ver(self, data, **kwargs):
    #     if data['ora_edition'] == 'SE' and data['ora_version'] != '11.2.0.4.0':
    #         raise ValidationError(
    #             'Not appropriate ora_version. '
    #             'For ora_edition SE only 11.2.0.4.0 ora_version is appropriate'
    #         )
    #     if data['ora_edition'] == 'SE2' and data['ora_version'] == '11.2.0.4.0':
    #         raise ValidationError(
    #             'Not appropriate ora_version. '
    #             'For ora_edition SE2 only 12.1.0.2.0 and above ora_versions are appropriate'
    #         )
    #     if data['ora_role_separation'] is False:
    #         data['grid_user'] = data['oracle_user']


class DataMountSchema(Schema):
    purpose = fields.Str(load_default='software')
    blk_device = fields.Str()
    name = fields.Str(load_default='u01')
    fstype = fields.Str(load_default='xfs')
    mount_point = fields.Str(load_default='/u01')
    mount_opts = fields.Str(load_default='nofail')


class DisksSchema(Schema):
    blk_device = fields.Str()
    name = fields.Str()
    size = fields.Str()


class ASMConfigSchema(Schema):
    diskgroup = fields.Str()
    disks = fields.List(fields.Nested(DisksSchema))
    au_size = fields.Str()
    redundancy = fields.Str()


class MiscConfigSchema(Schema):
    swap_blk_device = fields.Str()
    oracle_root = fields.Str(load_default='/u01/app')
    ntp_preferred = fields.Str(load_default='/etc/ntp.conf')
    role_separation = fields.Boolean()
    compatible_asm = fields.Str()
    compatible_rdbms = fields.Str()
    asm_disk_management = fields.Str()
    is_swap_configured = fields.Boolean()


class InstallConfigSchema(Schema):
    oracle_user = fields.Str(load_default='oracle')
    oracle_group = fields.Str(load_default='oinstall')
    home_name = fields.Str(load_default='db_home19c')
    grid_user = fields.Str(load_default='grid')
    grid_group = fields.Str(load_default='asmadmin')


class RACNodeSchema(Schema):
    node_name = fields.Str()
    node_id = fields.Int()
    node_ip = fields.Str()
    vip_name = fields.Str()
    vip_ip = fields.Str()


class RACConfigSchema(Schema):
    vip_name = fields.Str()
    vip_ip = fields.Str()
    scan_name = fields.Str(load_default='SCAN')
    scan_port = fields.Int(load_default=1521)
    cluster_name = fields.Str()
    cluster_domain = fields.Str()
    public_net = fields.Str(load_default='eth0')
    private_net = fields.Str(load_default='eth1')
    scan_ip1 = fields.Str()
    scan_ip2 = fields.Str(required=False)
    scan_ip3 = fields.Str(required=False)
    dg_name = fields.Str()
    rac_nodes = fields.List(fields.Nested(RACNodeSchema))

class DMSConfigSchema(Schema):
    port = fields.Int()
    username = fields.Str()
    password = fields.Str()
    password_secret_id = fields.Str()


class ConfigSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Config
        include_fk = True


class ProjectIdSchema(Schema):
    project_id = fields.Integer(required=True)


class LabelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Label
        include_fk = True
