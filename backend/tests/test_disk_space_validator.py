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

from contextlib import contextmanager
from unittest.mock import patch

import pytest

from bms_app.services.disk_space_validator import (
    DiskSpaceError, DiskSpaceValidator
)

from tests.factories import (
    BMSServerFactory, ConfigFactory, MappingFactory, RestoreConfigFactory,
    SourceDBFactory
)


PFILE_CONTENT = """
*.db_cache_size=4496293888
*.db_create_file_dest='+DATA'
db_1.db_file_name_convert='+DATA/dir1/datafile','+DATA_1/dir1/datafile'
*.db_file_name_convert='+DATA/dir2/datafile','+DATA_2/dir2/datafile','+DATA/dir3/datafile','+DATA_3/dir3/datafile'
*.db_name='db_1'
"""


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    'db_size,expectation',
    [
        (10, does_not_raise()),
        (39, does_not_raise()),
        (41, pytest.raises(DiskSpaceError)),
    ]
)
def test_disk_space_err(db_size, expectation, client):
    sdb = SourceDBFactory(db_size=db_size)
    ConfigFactory(
        source_db=sdb,
        asm_config_values=[
            {
                'diskgroup': 'DATA',
                'disks': [
                    {
                        'blk_device': '/dev/sdb',
                        'name': 'VM1_DATA'
                    },
                ]
            },
            {
                'diskgroup': 'DATA_1',
                'disks': [
                    {
                        'blk_device': '/dev/sdc',
                        'name': 'VM1_DATA1'
                    },
                ]
            },
            {
                'diskgroup': 'DATA_2',
                'disks': [
                    {
                        'blk_device': '/dev/sdd',
                        'name': 'VM1_DATA2'
                    },
                ]
            },
            {
                'diskgroup': 'DATA_3',
                'disks': [
                    {
                        'blk_device': '/dev/sde',
                        'name': 'VM1_DATA3'
                    },
                ]
            },
        ]
    )
    RestoreConfigFactory(source_db=sdb, pfile_file='pfile.ora')
    bms = BMSServerFactory(
        luns=[
            {'lun_name': 'disk-1', 'size_gb': '10', 'storage_type': 'PERSISTENT', 'storage_volume': '/dev/sdb'},
            {'lun_name': 'disk-2', 'size_gb': '10', 'storage_type': 'PERSISTENT', 'storage_volume': '/dev/sdc'},
            {'lun_name': 'disk-3', 'size_gb': '10', 'storage_type': 'PERSISTENT', 'storage_volume': '/dev/sdd'},
            {'lun_name': 'disk-4', 'size_gb': '10', 'storage_type': 'PERSISTENT', 'storage_volume': '/dev/sde'},
        ]
    )
    MappingFactory(source_db=sdb, bms=bms)

    with patch('bms_app.services.disk_space_validator.get_pfile_content',
               return_value=PFILE_CONTENT) as mock:
        with expectation:
            dsv = DiskSpaceValidator(sdb)
            dsv.validate()

            assert mock.called
