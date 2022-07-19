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

from bms_app.inventory_manager.services import get_client_ip

from .mixins import FileUploadMixin


class AnsibleConfigService(FileUploadMixin):
    """Generate ansible inventory and config files and upload them to GCS.

    Files:
    - inventory_temp - used by host-provision playbook
    - inventory - used by all other playbooks
    - asm_config/asm_disk_config_{hostname} - ask disk config
    - data_mounts_config/data_mounts_config_{hostname} - data mounts config

    """

    INVENTORY_FILE = 'inventory'
    INVENTORY_TMP_FILE = 'inventory_temp'  # used for host-provision playbook
    ASM_CONFIG_DIR = 'asm_config'
    DATA_MOUNTS_CONFIG_DIR = 'data_mounts_config'

    def __init__(self, db_mappings_objects, gcs_config_dir):
        self.db_mappings_objects = db_mappings_objects
        self.gcs_config_dir = gcs_config_dir or ''

    def run(self):
        (main_inventory_data, provision_inventory_data,
         asm_configs, data_mounts_configs) = self._generate_configs_data()

        self._save_inventories(
            main_inventory_data, provision_inventory_data
        )
        self._save_asm_configs(asm_configs)
        self._save_data_mounts_configs(data_mounts_configs)

    def _save_inventories(self, main_inventory_data, provision_inventory_data):
        self._upload_yaml(
            data=main_inventory_data,
            file_name=self.INVENTORY_FILE
        )
        self._upload_yaml(
            data=provision_inventory_data,
            file_name=self.INVENTORY_TMP_FILE
        )

    def _save_asm_configs(self, asm_configs):
        for host_name, config_content in asm_configs.items():
            file_name = f'asm_disk_config_{host_name}.json'
            self._upload_json(
                data=config_content,
                dir_name=self.ASM_CONFIG_DIR,
                file_name=file_name
            )

    def _save_data_mounts_configs(self, data_mounts_configs):
        for host_name, config_content in data_mounts_configs.items():
            file_name = f'data_mounts_config_{host_name}.json'
            self._upload_json(
                data=config_content,
                dir_name=self.DATA_MOUNTS_CONFIG_DIR,
                file_name=file_name
            )

    def _generate_configs_data(self):
        """Generate all needed ansible configuration data."""
        provision_inventory_hosts = {}  # hosts by host-provision inventory
        main_inventory_hosts = {}  # hosts used by all other playbooks
        asm_js_configs = {}  # asm json config per host
        data_js_mounts_configs = {}  # data_mounts json config per host

        for db_map_dto in self.db_mappings_objects:
            config = db_map_dto.db.config
            mappings = db_map_dto.mappings

            # generate main inventory hosts
            main_inventory_hosts.update(
                self._generate_main_inventory_hosts(db_map_dto)
            )

            # generate other configs and provision inventory hosts
            for mapping in mappings:
                bms = mapping.bms

                provision_inventory_hosts.update(
                    self._generate_single_inventory_host(bms)
                )

                asm_js_configs[bms.name] = config.asm_config_values
                data_js_mounts_configs[bms.name] = config.data_mounts_values

        main_inventory_data = self._generate_inventory_file_data(
            main_inventory_hosts
        )
        provision_inventory_data = self._generate_inventory_file_data(
            provision_inventory_hosts
        )

        return (
            main_inventory_data,
            provision_inventory_data,
            asm_js_configs,
            data_js_mounts_configs
        )

    @classmethod
    def _generate_main_inventory_hosts(cls, db_map_dto):
        if db_map_dto.db.is_rac:
            return cls._generate_rac_install_inventory_host(db_map_dto)

        return cls._generate_si_install_inventory_host(db_map_dto)

    @staticmethod
    def _generate_common_inventory_data(source_db, bms):
        config = source_db.config

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

        for param in ('compatible_rdbms', 'swap_blk_device'):
            if param in config.misc_config_values:
                config_data[param] = config.misc_config_values[param]

        return config_data

    @classmethod
    def _generate_si_install_inventory_host(cls, db_map_dto):
        """Sinlge Instance config."""
        source_db = db_map_dto.db

        data = {}
        for mapping in db_map_dto.mappings:
            bms = mapping.bms

            config_data = cls._generate_common_inventory_data(source_db, bms)

            data[bms.name] = config_data

        return data

    @classmethod
    def _generate_rac_install_inventory_host(cls, db_map_dto):
        """Generate inventory for RAC."""
        source_db = db_map_dto.db
        config = source_db.config

        data = {}
        for mapping in db_map_dto.mappings:
            bms = mapping.bms

            rac_config_values = config.rac_config_values
            rc_data = next(
                (rc for rc in rac_config_values['rac_nodes']
                 if rc['node_id'] == bms.id)
            )

            config_data = cls._generate_common_inventory_data(source_db, bms)

            config_data.update({
                # rac data
                'cluster_type': 'RAC',
                'rac_node': mapping.rac_node,
                'scan_name': rac_config_values['scan_name'],
                'scan_port': rac_config_values['scan_port'],
                'cluster_name': rac_config_values['cluster_name'],
                'cluster_domain': rac_config_values['cluster_domain'],
                'public_net': rac_config_values['public_net'],
                'private_net': rac_config_values['private_net'],
                'scan_ip1': rac_config_values['scan_ip1'],
                'dg_name': rac_config_values['dg_name'],
                'vip_name': rc_data['vip_name'],
                'vip_ip': rc_data['vip_ip'],

            })

            for param in ('scan_ip2', 'scan_ip3'):
                if param in rac_config_values:
                    config_data[param] = rac_config_values[param]

            data[bms.name] = config_data

        return data

    @staticmethod
    def _generate_single_inventory_host(bms):
        """Generate one host section for host-provision inventory."""
        return {
            bms.name: {
                'ansible_ssh_host': get_client_ip(bms),
                'ansible_ssh_user': 'customeradmin',
                'sm_token': bms.secret_name or '',
            }
        }

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
