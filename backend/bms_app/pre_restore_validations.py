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

PRE_RESTORE_VALIDATIONS = [
    {
        'name': 'RMAN> crosscheck backup',
        'description': (
            'Use the CROSSCHECK command to synchronize the physical reality of backups and copies with their logical records in the RMAN repository.\n'
            'CROSSCHECK validates all specified backups and copies, even if they were created in previous database incarnations.\n'
            'If a backup is on disk, then CROSSCHECK determines whether the header of the file is valid. '
            'If a backup is on tape, then RMAN queries the RMAN repository for the names and locations of the backup pieces to be checked. '
            'RMAN sends this metadata to the target database server, which queries the media management software about the backups. '
            'The media management software then checks its media catalog and reports back to the server with the status of the backups.'
        )
    },
    {
        'name': 'RMAN> delete noprompt expired backup',
        'description': (
            'Delete any expired backups detected by the CROSSCHECK. When the CROSSCHECK command is used to determine whether backups recorded in the repository still exist on disk or tape, '
            'if RMAN cannot locate the backups, then it updates their records in the RMAN repository to EXPIRED status. '
            'You can then use the DELETE EXPIRED command to remove records of expired backups from the RMAN repository. '
            'If the expired files still exist, then the DELETE EXPIRED command terminates with an error.'
        )
    },
    {
        'name': 'RMAN> list backup',
        'description': 'The LIST command uses the information in the RMAN repository to provide lists of backups and other objects relating to backup and recovery.'
    },
    {
        'name': 'RMAN> restore database preview',
        'description': 'Reports (but does not restore) the backups and archived redo log files that RMAN could use to restore and recover the database to the specified time.'
    },
    {
        'name': 'RMAN> report need backup',
        'description': 'Reports which database files must be backed up to meet a configured or specified retention policy.'
    },
    {
        'name': 'RMAN> report unrecoverable',
        'description': 'Reports which database files require backup because they have been affected by some NOLOGGING operation such as a direct-path INSERT.'
    },
    {
        'name': 'RMAN> restore database validate',
        'description': (
                'The restore validate command can be performed for any database objects including the whole database to verify the files are valid.'
                'This command can be used to restore as of the current time (default), but you can also specify a previous point-in-time.\n'
                'The validate verifies that the files are available and also checks for corruption.'
        )
    },
    {
        'name': 'RMAN> restore database validate check logical',
        'description': 'The validate verifies that the files are available and also checks for logical corruption.'
    },
    {
        'name': 'disk space validation',
        'description': 'Validate disk space'
    }
]
