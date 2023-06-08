/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

export interface ConfigEditor {
  is_configured?: boolean,
  asm_config_values?: {
    au_size: string,
    diskgroup: string,
    redundancy: string
    disks: {}[] ;
  }[],
  created_at?: string,
  data_mounts_values?: DataMountValues[],
  db_id?: number,
  db_params_values?: {
    db_name?: string,
  },
  install_config_values?: {
    grid_group?: string,
    grid_user?: string,
    home_name?: string,
    oracle_group?: string,
    oracle_root?: string,
    oracle_user?: string,
  },
  misc_config_values?: {
    asm_disk_management?: string,
    compatible_asm?: string,
    compatible_rdbms?: string,
    ntp_preferred?: string,
    oracle_root?: string,
    swap_blk_device?: string,
    role_separation: boolean
    is_swap_configured: boolean
  },
  rac_config_values?: {
    scan_name?: string,
    scan_port?: string,
    cluster_name?: string,
    cluster_domain?: string,
    public_net?: string,
    private_net?: string,
    scan_ip1?: string,
    scan_ip2?: string,
    scan_ip3?: string,
    dg_name?: string,
    rac_nodes: Node[]
  },
  dms_config_values?: {
    port?: number,
    username?: string,
    password?: string
  }
}

export interface Node {
  node_id: number;
  vip_name: string;
  vip_ip: string;
  node_ip: string;
}

export interface DataMountValues {
  blk_device: string;
  fstype: string;
  mount_opts: string;
  mount_point: string;
  name: string;
  purpose: string;
}
