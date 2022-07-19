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

from bms_app import settings
from bms_app.services.gcs import get_file_content


def get_pfile_content(restore_config):
    """Return pfile content."""
    pfile_content = get_file_content(
        settings.GCS_BUCKET,
        restore_config.pfile_file
    )
    return pfile_content


class RestoreConfigValidationsService:
    RMAN_CMD_PREFIX = 'RMAN>'
    DISK_SPACE_VALIDATION = 'disk space validation'

    def __init__(self, source_db):
        self.source_db = source_db
        self._rman_commands = None

    @property
    def restore_config(self):
        return self.source_db.restore_config

    def get_rman_commands(self):
        if self._rman_commands is None:
            self._rman_commands = []

            if self.restore_config:
                for cmd in self.restore_config.validations:
                    if cmd.startswith(self.RMAN_CMD_PREFIX):
                        self._rman_commands.append(
                            cmd[len(self.RMAN_CMD_PREFIX):].strip()
                        )

        return self._rman_commands

    def needs_rman_validation(self):
        return bool(self.get_rman_commands())

    def needs_disk_space_validation(self):
        if self.restore_config:
            return (
                self.DISK_SPACE_VALIDATION in self.restore_config.validations
            )
