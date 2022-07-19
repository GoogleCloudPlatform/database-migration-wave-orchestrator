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
from bms_app.services.gcs import blob_exists, get_file_content


class RmanLogFileError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__()


class RmanCommandLogParser:
    """Parser for one rman command output.

    Exmaple:
        RMAN> restore database preview;
        Starting restore at 12-MAY-22
        using channel ORA_DISK_1


        List of Backup Sets
        ===================
        ....
    """

    ERROR_WORDS = ['EXPIRED', 'RMAN-', 'ORA-', 'ERROR']
    # list of commands with specific error output
    CMD_WITH_TABLE_STYLE_ERRORS = (
        'report need backup',
        'report unrecoverable'
    )

    def __init__(self, text):
        self.text = text.strip()
        self.lines = text.split('\n')
        self.cmd = self.lines[0].strip(' ;')

    def has_error(self):
        if self.cmd in self.CMD_WITH_TABLE_STYLE_ERRORS:
            has_error = self._has_table_style_err()
        else:
            has_error = self._has_error_word()

        return has_error

    def _has_error_word(self):
        """Check if contains any of words that means error."""
        return any(word in self.text for word in self.ERROR_WORDS)

    def _has_table_style_err(self):
        """Check "table" style error.

        Error example:
            RMAN> report need backup;
            RMAN retention policy will be applied to the command
            RMAN retention policy is set to redundancy 1
            Report of files with less than 1 redundant backups
            File #bkps Name
            ---- ----- -------------------------------------------------------------------------------
            1    0     +DATA/FINDB/DATAFILE/system.256.1095521433
            7    0     +DATA/FINDB/DATAFILE/users.259.1095521503

        No error example:
            RMAN> report need backup;
            RMAN retention policy will be applied to the command
            RMAN retention policy is set to redundancy 1
            Report of files with less than 1 redundant backups
            File #bkps Name
            ---- ----- ---------------------------------------------------------------------------------
        """
        # check if the last line has any data except separator (space and dash)
        return bool(self.lines[-1].strip(' -'))


class RmanLogFileParser:
    RMAN_FILE_LOCATION = 'control_node_logs/bms_logs_{operation_id}/rman_pre_restore.log'
    COMMANDS_TO_SKIP = ('delete noprompt expired backup')
    RMAN_CMD_PREFIX = 'RMAN>'

    def __init__(self, operation_id):
        self.operation_id = operation_id
        self._rman_file_content = None

    def validate(self):
        failed_commands = []

        for chunk in self._split_file():
            cmd_parser = RmanCommandLogParser(chunk)
            # skip logs not related to specific rman command
            if cmd_parser.cmd and cmd_parser.cmd not in self.COMMANDS_TO_SKIP:
                if cmd_parser.has_error():
                    failed_commands.append(
                        f'{self.RMAN_CMD_PREFIX} {cmd_parser.cmd}'
                    )

        if failed_commands:
            raise RmanLogFileError(failed_commands)

    @property
    def rman_file_content(self):
        if self._rman_file_content is None:
            gcs_key = self.RMAN_FILE_LOCATION.format(
                operation_id=self.operation_id
            )
            self._rman_file_content = get_file_content(
                settings.GCS_BUCKET,
                gcs_key
            )
        return self._rman_file_content

    def get_cmd_output(self, cmd):
        """Return output of the specific rman command."""
        if cmd.startswith(self.RMAN_CMD_PREFIX):
            cmd = cmd[5:].strip()  # to remove spaces around

        for chunk in self._split_file():
            cmd_parser = RmanCommandLogParser(chunk)
            if cmd_parser.cmd == cmd:
                return chunk

    def _split_file(self):
        splitted = [x.strip() for x in self.rman_file_content.split(self.RMAN_CMD_PREFIX)]
        # skip 1-st section that contains some general information
        return splitted[1:]

    def log_file_exists(self):
        gcs_key = self.RMAN_FILE_LOCATION.format(
            operation_id=self.operation_id
        )
        return blob_exists(settings.GCS_BUCKET, gcs_key)
