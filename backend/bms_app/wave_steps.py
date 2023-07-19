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

BASE_STEPS = [
    {
        'id': 'PRE_DEPLOYMENT',
        'name': 'Pre-deployment',
        'description': (
            'Pre-deployment\n'
            'internal steps:\n'
            '- Control nodes provision\n'
            '- Setup environment\n'
            '- Setup logging\n'
            '- Generate configuration files'
        )
    },
    {
        'id': 'SETUP_SSH_CONNECTION',
        'name': 'Setup SSH connection',
        'description': (
            'Setup SSH connection\n'
            '- Setup SSH connection between control node and target hosts'
        )
    },
]

DEPLOYMENT_STEPS = BASE_STEPS + [
    {
        'id': 'CHECK_INSTANCE',
        'name': 'Check instance',
        'description': (
            'Check instance\n'
            '- Platform verification\n'
            '- Test privilege escalation on target\n'
            '- Test connectivity to target instance'
        )
    },
    {
        'id': 'HOST_PREPARATION',
        'name': 'Host preparation',
        'description': (
            'Host preparation\n'
            '- Install required base OS packages\n'
            '- Configure services\n'
            '- Disable firewall, selinux\n'
            '- Install Oracle required packages\n'
            '- Create users and groups\n'
            '- Configure ASM disks and Swap\n'
            '- Configure kernel parameters\n'
            '- Configure Hugepages\n'
            '- Copy installation files from GCS Bucket'
        )
    },
    {
        'id': 'SW_INSTALL',
        'name': 'Software installation',
        'description': (
            'Software intallation\n'
            'Oracle software is divided into two general categories:\n'
            '- base software that you download from the Oracle Software Delivery Cloud site (also known as Oracle \'eDelivery\'):\n'
            '-- Grid binaries\n'
            '-- RDBMS binaries\n'
            '- patches that you download from Oracle\'s My Oracle Support (MOS) site.'
        )
    }
]

DMS_DEPLOYMENT_STEPS = [
    {
        'id': 'PRE_DEPLOYMENT',
        'name': 'Pre-deployment',
        'description': (
            'Starts the Workflow to run the following steps.'
        )
    },
    {
        'id': 'CREATE_SRC_CONNECTION_PROFILE',
        'name': 'Create Source Connection Profile',
        'description': (
            'Creates the connection profile based on source database connection details.\n'
            'Connection profile contains information such as:\n'
            '- Host\n'
            '- Port\n'
            '- Username\n'
            '- Password\n'
        )
    },
    {
        'id': 'CREATE_DST_CONNECTION_PROFILE',
        'name': 'Create Destination Connection Profile',
        'description': (
            'Creates the connection profile to the target CloudSQL instance.\n'
            'Creating the connection profile also triggers the creation of the target instance\n'
        )
    },
    {
        'id': 'RUN_MIGRATION_JOB',
        'name': 'Run DMS Migration Job',
        'description': (
            'Starts the DMS migration job with the source and target connection profiles\n'
            'created in previous steps.\n',
            'Data is mirrored from the source to the target. CloudSQL continues operating as\n'
            'slave. A manual promotion must be made to start using the target instance as primary\n'
            'database.'
        )
    }
]

ROLLBACK_STEPS = BASE_STEPS + [
    {
        'id': 'CLEANUP',
        'name': 'Cleanup',
        'description': (
            '- Kills all running Oracle services\n'
            '- Deconfigures the Oracle Restart software\n'
            '- Removes Oracle related directories and files\n'
            '- Removes Oracle software owner users and groups\n'
            '- Re-initializes ASM storage devices and uninstalls ASMlib if installed\n'
            'Important: a destructive cleanup permanently deletes the databases and any data they ontain. Any backups that are stored local to the server are also deleted'
        )
    }
]
