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

import { Observable, of, SubscriptionLike } from 'rxjs';

import { ConfigEditor } from '@app-interfaces/configEditor';

import { ConfigEditorService } from './config-editor.service';


export class MockConfigEditorService extends ConfigEditorService {
  constructor() {
    super(jasmine.createSpyObj('HttpClient', { post: of({}), get: of({}) }));
  }

  configEditor: ConfigEditor = {
    asm_config_values: [],
    created_at: 'test data',
    data_mounts_values: [{
      blk_device: '/dev/sdb',
      fstype: 'xfs',
      mount_opts: 'nofail',
      mount_point: ' /u01',
      name: ' u01',
      purpose: 'software'
    }],
    db_id: 1,
    db_params_values: { db_name: 'APPDB_3891' },
    install_config_values: {
      grid_group: 'oinstall',
      grid_user: 'grid',
      home_name: 'dbhome_1',
      oracle_group: 'oinstall'
    },
    misc_config_values: {
      asm_disk_management: 'Udev',
      compatible_asm: '12.2.0.1',
      compatible_rdbms: '11.2.0.4',
      ntp_preferred: 'data Original',
      oracle_root: ' /u01/app',
      role_separation: true,
      swap_blk_device: '/dev/sdf',
      is_swap_configured: false
    },
    rac_config_values: {
      cluster_domain: 'domain',
      cluster_name: 'name',
      dg_name: 'DATA',
      private_net: 'private',
      public_net: 'public',
      rac_nodes: [{
        node_id: 17,
        node_ip: '172.25.9.39',
        vip_ip: '192.168.1.1',
        vip_name: 'vip'
      }],
      scan_ip1: '192.168.1.1',
      scan_ip2: '192.168.1.2',
      scan_ip3: '192.168.1.3',
      scan_name: 'name',
      scan_port: '300'
    }
  }

  getConfigEditor(_: number): Observable<ConfigEditor> {
    return of(this.configEditor);
  }

  createConfigEditorsingleInstance(migration: any , _: number): Observable<ConfigEditor> {
    return of(this.configEditor);
  } 
}
