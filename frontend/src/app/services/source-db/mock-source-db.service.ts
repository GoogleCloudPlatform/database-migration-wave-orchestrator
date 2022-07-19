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

import { Observable, of } from 'rxjs';

import { SourceDb } from '@app-interfaces/sourceDb';

import { SourceDbService } from './source-db.service';

export class MockSourceDbService extends SourceDbService {
  constructor() {
    super(jasmine.createSpyObj('HttpClient', { post: of({}), get: of({}) }));
  }

  getSourceDbsProjects(_: number): Observable<SourceDb> {
    const projects: SourceDb = {
      data: [
        {
          allocated_memory: 41,
          arch: 'Solaris[tm] OE (64-bit)',
          cores: 24,
          db_name: 'APPDB_3891',
          db_size: 16544.855,
          db_type: 'RAC',
          fe_rac_nodes: 2,
          id: 528,
          oracle_edition: 'EE',
          oracle_release: 'base',
          oracle_version: '11.2',
          project_id: 23,
          rac_nodes: 2,
          ram: 134,
          server: 'serverapp_3891',
          status: 'EMPTY',
          wave_id: 1,
          labels: [
            {
              name: 'label1',
              id: 1
            },
            {
              name: 'label2',
              id: 2
            }
          ]
        },
        {
          allocated_memory: 1,
          arch: 'Linux x86 64-bit',
          cores: 2,
          db_name: 'REPORT_DB',
          db_size: 1.247,
          db_type: 'SI',
          fe_rac_nodes: 0,
          id: 25,
          oracle_edition: 'EE',
          oracle_release: 'base',
          oracle_version: '19.3.0.0.0',
          project_id: 6,
          rac_nodes: 0,
          ram: 2,
          server: 'lxoradbprod2',
          status: 'FAILED',
          labels: []
        }
      ],
      allocated_memory: 41,
      rac_nodes: 2
    }
    return of(projects);
  }
}

