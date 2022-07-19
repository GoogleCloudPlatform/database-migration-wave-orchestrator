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

import re
from configparser import ConfigParser

from bms_app.models import BMSServer, Mapping, SourceDB, db
from bms_app.services.restore_config import get_pfile_content


# "'+DATA_1/DB_NAME/datafile'" -> regex to parse disk group name: DATA_1
DISK_GROUP_RE = re.compile(r'\+([^/]+)/')


class DiskSpaceError(Exception):
    def __init__(self, db_size, capacity):
        super().__init__(
            f'disk space error: db_size={db_size}, capacity={capacity}'
        )


class DiskSpaceValidator:
    """Validate if db size is less or equal than target's disks size.

    Parse pfile config and retrieve all used disk groups.
    Calculate total size of disks mapped to these disk groups.
    Compare db size and calulated disk size.
    """

    def __init__(self, source_db):
        self.source_db = source_db

    def validate(self):
        pfile_disk_groups = self._parse_prifle_disk_groups()
        asm_blk_devices = self._get_asm_blk_devices(pfile_disk_groups)
        total_disks_capacity = self._get_total_disks_capacity(asm_blk_devices)

        if self.source_db.db_size > total_disks_capacity:
            raise DiskSpaceError(
                str(self.source_db.db_size),
                total_disks_capacity
            )

    def _parse_prifle_disk_groups(self):
        """Parse pfile and return list of used disk groups.

        Pfile format is similar to "INI" (key=value) format
        but it does not contain section ([section name])
        """
        pfile_txt = get_pfile_content(self.source_db.restore_config)
        parser = ConfigParser()
        parser.read_string('[cfg]\n' + pfile_txt)

        disk_groups_1 = self._parse_file_name_convert_param(parser)
        disk_groups_2 = self._parse_create_file_dest_param(parser)

        return disk_groups_1.union(disk_groups_2)

    @staticmethod
    def _parse_file_name_convert_param(parser):
        """Parse 'db_file_name_convert' parameters.

        There might be multiple lines:
        - *.db_file_name_convert ans
        - <db_name>.db_file_name_convert
        Example: *.db_file_name_convert='+DATA/uaab2stanbynew_ifobs/datafile','+DATA2/uaab2prodsrv_IFOBS/datafile','+DATA/uaab2stanbynew_ifobs/datafile','+DATA4/IFOBS/datafile'
        The algorithm is:
        - get the value
        - split it by comma (they are source and destination) and get every second item (+DATA2/..., +DATA4/..)
        - parse the value between "+" and "/" (e.g. DATA2, DATA4)
        """
        keys = [k for k in parser['cfg'].keys()
                if k.endswith('.db_file_name_convert')]

        disk_groups = set()

        for k in keys:
            for destination in parser['cfg'][k].split(',')[1::2]:
                disk_group = DISK_GROUP_RE.search(destination).groups()[0]
                disk_groups.add(disk_group)

        return disk_groups

    @staticmethod
    def _parse_create_file_dest_param(parser):
        """Parse 'db_create_file_dest' parameter.

        Example: *.db_create_file_dest='+DATA'
        """
        keys = [k for k in parser['cfg'].keys()
                if k.endswith('.db_create_file_dest')]
        return {parser['cfg'][k].strip("'").lstrip('+') for k in keys}

    def _get_asm_blk_devices(self, disk_groups):
        """Return list of block devices/disks mapped to ASM disk groups."""
        asm_blk_devices = set()

        for asm_data in self.source_db.config.asm_config_values:
            if asm_data['diskgroup'] in disk_groups:
                for disk in asm_data['disks']:
                    asm_blk_devices.add(disk['blk_device'])

        return asm_blk_devices

    def _get_total_disks_capacity(self, asm_blk_devices):
        """Calculate total size of block devices."""
        capacity = 0

        query = db.session.query(BMSServer) \
            .join(Mapping) \
            .join(SourceDB) \
            .filter(SourceDB.id == self.source_db.id) \
            .all()

        for bms in query:
            for lun in bms.luns:
                if lun['storage_volume'] in asm_blk_devices:
                    capacity += int(lun['size_gb'])

        return capacity
