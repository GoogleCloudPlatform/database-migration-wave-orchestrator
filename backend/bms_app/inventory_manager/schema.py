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

from collections import defaultdict

from marshmallow import (
    EXCLUDE, Schema, ValidationError, fields, post_load, pre_load, validate
)

from bms_app import ma
from bms_app.models import BMSServer


BMS_PARAMS = {
    'o2-standard-16-metal': ('8', '2', '192GB'),
    'o2-standard-32-metal': ('16', '2', '384GB'),
    'o2-standard-48-metal': ('24', '2', '768GB'),
    'o2-standard-112-metal': ('56', '2', '1.5TB'),
    'o2-highmem-224-metal': ('112', '4', '3TB'),
    'o2-ultramem-672-metal': ('336', '12', '18TB'),
    'o2-ultramem-896-metal': ('448', '16', '24TB')
}


class BMSServerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BMSServer

    client_ip = fields.Function(
        lambda data: next(
            (x for x in data.networks if x.get('type') == 'CLIENT'), {}).get('ipAddress')
        )


class APIBMSLunSchema(Schema):
    name = fields.Str(required=True)
    size_gb = fields.Str(data_key='sizeGb', required=True)
    storage_type = fields.Str(data_key='storageType', required=True)
    storage_volume = fields.Str(data_key='wwid', required=True)

    class Meta:
        unknown = EXCLUDE

    @post_load
    def post_load_process(self, data, **kwargs):
        data['name'] = data['name'].split('/')[-1]
        data['storage_volume'] = f'/dev/mapper/3{data["storage_volume"]}'

        return data


class UploadBMSLunSchema(Schema):
    name = fields.Str(required=True)
    size_gb = fields.Str(required=True)
    storage_type = fields.Str(required=True)
    storage_volume = fields.Str(required=True)


class BMSNetworkSchema(Schema):
    name = fields.Str(required=True)
    ipAddress = fields.IP(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(['CLIENT', 'PRIVATE']))

    class Meta:
        unknown = EXCLUDE

    @post_load
    def post_load_process(self, data, **kwargs):
        data['name'] = data['name'].split('/')[-1]
        data['ipAddress'] = str(data['ipAddress'])

        return data


class UploadBMSServerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BMSServer
        unknown = EXCLUDE

    def __init__(self, *args, **kwargs):
        # Exclude id from uploaded file
        self.opts.exclude += ('id',)
        super().__init__(*args, **kwargs)

    name = fields.Str(required=True)
    location = fields.Str(required=True)
    luns = fields.List(fields.Nested(UploadBMSLunSchema))
    networks = fields.List(fields.Nested(BMSNetworkSchema))
    machine_type = fields.Str(data_key='machineType')

    @staticmethod
    def handle_error(exc, data, **kwargs):
        """Log and raise our custom exception when (de)serialization fails."""
        reversed_err = defaultdict(list)

        def reverse_errors(data, parent=''):
            for key, value in data.items():
                err = f'{parent}.{key}' if parent else key

                if isinstance(value, dict):
                    # skip 1-st level and list index
                    if parent and not isinstance(key, int):
                        sub_parent = f'{parent}.{key}'
                    else:
                        sub_parent = parent or key

                    reverse_errors(value, sub_parent)

                elif isinstance(value, list):
                    for val in value:  # in case of multiple errors
                        if err not in reversed_err[val]:
                            reversed_err[val].append(err)
                else:  # str
                    reversed_err[value].append(err)

        reverse_errors(exc.messages)

        raise ValidationError(reversed_err)

    @post_load
    def post_load_process(self, data, **kwargs):
        if not data.get('machine_type'):
            if not all((x in data for x in ('cpu', 'socket', 'ram'))):
                raise ValidationError(
                    {'cpu/socket/ram': ['Please specify all fields or fill in machineType field.']}
                )

        if not any(network['type'] == 'CLIENT' for network in data['networks']):
            raise ValidationError(
                {'networks': ["Please specify at least one type network as 'CLIENT'."]}
            )

        all_volumes = [lun['storage_volume'] for lun in data['luns']]
        if len(all_volumes) != len(set(all_volumes)):
            raise ValidationError(
                {'storage_volume': ["Please specify unique storage_volume value"]}
            )

        return data


class APIBMSServerSchema(ma.SQLAlchemyAutoSchema):
    """schema to load data from BMS API."""
    class Meta:
        model = BMSServer
        unknown = EXCLUDE

    def __init__(self, *args, **kwargs):
        self.opts.exclude += ('id',)
        super().__init__(*args, **kwargs)

    name = fields.Str(data_key='id')
    location = fields.Str(data_key='name')
    machine_type = fields.Str(data_key='machineType')
    luns = fields.List(fields.Nested(APIBMSLunSchema))
    networks = fields.List(fields.Nested(BMSNetworkSchema))

    @pre_load(pass_many=True)
    def filter_data(self, data, **kwargs):
        data['luns'] = [x for x in data['luns'] if not x.get('bootLun')]
        return data

    @post_load
    def post_load_process(self, data, **kwargs):
        data['location'] = data['location'].split('/')[3]

        machine_type = data['machine_type']
        cpu, socket, ram = BMS_PARAMS.get(machine_type, ('', '', ''))
        data['cpu'] = cpu
        data['socket'] = socket
        data['ram'] = ram

        return data
