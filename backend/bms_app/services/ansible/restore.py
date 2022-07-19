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

import os

import yaml

from bms_app import settings
from bms_app.inventory_manager.services import get_client_ip
from bms_app.services.gcs import copy_blob, upload_blob_from_string
from bms_app.services.restore_config import RestoreConfigValidationsService

from .mixins import FileUploadMixin


class AnsibleBaseDataTransferConfigService(FileUploadMixin):
    """Generate ansible inventory and config files and upload them to GCS.

    Files:
    - inventory - used by all other playbooks
    - pfile.ora - db parameters file
    """

    INVENTORY_FILE = 'inventory'

    def __init__(self, db_mappings_object, gcs_config_dir):
        self.db_mappings_object = db_mappings_object
        self.gcs_config_dir = gcs_config_dir or ''

    def run(self):
        inventory_data = self._generate_inventory_data()

        self._save_inventory(inventory_data)
        self._save_config_files()

    def _save_inventory(self, inventory_data):
        self._upload_yaml(
            data=inventory_data,
            file_name=self.INVENTORY_FILE
        )

    def _save_config_files(self):
        self._copy_file(
            self.db_mappings_object.db.restore_config.pfile_file,
            'pfile.ora'
        )

    def _copy_file(self, gcs_key, destination_file_name):
        """Copy file to ansible config dir."""
        copy_blob(
            settings.GCS_BUCKET,
            gcs_key,
            settings.GCS_BUCKET,
            os.path.join(self.gcs_config_dir, destination_file_name)
        )

    def _upload_yaml(self, data, file_name):
        """Upload file in yaml format to GCS."""
        file_content = yaml.safe_dump(data)
        gcs_key = os.path.join(self.gcs_config_dir, file_name)
        upload_blob_from_string(settings.GCS_BUCKET, gcs_key, file_content)

    def _generate_inventory_data(self):
        """Generate ansible file inventory data."""
        inventory_host = self._generate_main_inventory_hosts()
        inventory_data = self._generate_inventory_file_data(inventory_host)
        return inventory_data

    def _generate_main_inventory_hosts(self):
        if self.db_mappings_object.db.is_rac:
            raise NotImplementedError('rac db is not supported yet')
            # return cls._generate_rac_install_inventory_host(db_map_obj)
        return self._generate_si_install_inventory_host()

    def _generate_si_install_inventory_host(self):
        """Single Instance config."""
        source_db = self.db_mappings_object.db
        config = source_db.config
        bms = self.db_mappings_object.mappings[0].bms

        config_data = {
            'ansible_ssh_host': get_client_ip(bms),
            'ansible_ssh_user': 'customeradmin',
            'ansible_ssh_private_key_file': '/root/.ssh/id_rsa_bms_toolkit',
            'ansible_ssh_extra_args': '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentityAgent=no',
            'oracle_ver': source_db.oracle_version,
            'oracle_edition': source_db.oracle_edition,
            'db_name': config.db_params_values['db_name'],
            'compatible_rdbms': config.misc_config_values['compatible_rdbms'],
            'oracle_user': config.install_config_values['oracle_user'],
            'oracle_group': config.install_config_values['oracle_group'],
            'oracle_root': config.misc_config_values['oracle_root'],
            'home_name': config.install_config_values['home_name'],
            'sm_token': bms.secret_name,
        }

        if 'swap_blk_device' in config.misc_config_values:
            config_data['swap_blk_device'] = config.misc_config_values['swap_blk_device']

        self._add_extra_config_data(source_db, bms, config_data)

        return {
            bms.name: config_data
        }

    @staticmethod
    def _add_extra_config_data(source_db, bms, config_data):
        pass

    @staticmethod
    def _generate_inventory_file_data(hosts):
        """Generate complete inventory data structure."""
        return {
            'all': {
                'children': {
                    'dbasm': {
                        'hosts': hosts
                    }
                }
            }
        }


class AnsiblePreRestoreConfigService(AnsibleBaseDataTransferConfigService):
    """Generate ansible inventory for PreRestore"""

    def _add_extra_config_data(self, source_db, bms, config_data):
        restore_config = source_db.restore_config
        rcv = RestoreConfigValidationsService(source_db)

        splitted = [x for x in restore_config.backup_location.split('/') if x]

        config_data.update(
            {
                'backup_bucket': splitted[0],
                'pfile_file': 'pfile.ora',
                'fuse_direct': True,
                'control_file': restore_config.control_file,
                'rman_commands': rcv.get_rman_commands(),
            }
        )

        if len(splitted) > 1:
            config_data['gcs_backup_folder'] = '/'.join(splitted[1:])

        return config_data


class AnsibleRestoreConfigService(AnsibleBaseDataTransferConfigService):
    """Generate ansible inventory for Restore"""

    def _save_config_files(self):
        super()._save_config_files()
        if self.db_mappings_object.db.restore_config.pwd_file:
            self._copy_file(
                self.db_mappings_object.db.restore_config.pwd_file,
                'orapw.file'
            )

        self._save_rman_command()

    def _add_extra_config_data(self, source_db, bms, config_data):
        restore_config = self.db_mappings_object.db.restore_config

        splitted = [x for x in restore_config.backup_location.split('/') if x]

        config_data.update(
            {
                'backup_bucket': splitted[0],
                'pfile_file': 'pfile.ora',
                'fuse_direct': True,
                'restore_type': restore_config.backup_type.value.lower(),
                'control_file': restore_config.control_file,
            }
        )

        if len(splitted) > 1:
            config_data['gcs_backup_folder'] = '/'.join(splitted[1:])

        if restore_config.pwd_file:
            config_data['psw_file'] = restore_config.pwd_file

        return config_data

    def _save_rman_command(self):
        restore_config = self.db_mappings_object.db.restore_config

        if restore_config.is_full_backup_type:
            template_name = 'rman_restore_db.cmd.j2'
        else:
            template_name = 'rman_restore_inc.cmd.j2'

        upload_blob_from_string(
            settings.GCS_BUCKET,
            os.path.join(self.gcs_config_dir, template_name),
            restore_config.rman_cmd
        )


class AnsibleRollbackRestoreConfigService(AnsibleBaseDataTransferConfigService):
    """Generate ansible inventory for RollbackRestore"""

    pass


class AnsibleFailOverConfigService(AnsibleBaseDataTransferConfigService):
    """Generate ansible inventory for FailOver"""

    pass
