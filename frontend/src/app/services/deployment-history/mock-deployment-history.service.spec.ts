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

import { BehaviorSubject, Observable, of, Subject } from 'rxjs';

import { DatabaseOperationsHistoryResponse } from '@app-interfaces/database-operations-history';
import { DeploymentDetailsResponseMeta } from '@app-interfaces/deployment';

import { DeploymentHistoryService } from './deployment-history.service';


export class MockDeploymentHistoryService extends DeploymentHistoryService {
  constructor() {
    super(jasmine.createSpyObj('HttpClient', { post: of({}), get: of({}) }));
  }

  databaseHistory: DatabaseOperationsHistoryResponse = {
    db_name: 'DB49',
    db_type: 'SI',
    id: 1,
    operations: [{
      bms: [{
        id: 1,
        logs_url: 'https://console.cloud.google.com',
        name: 'tests-cycle3-49',
        operation_status: 'FAILED'
      }],
      completed_at: 'Thu, 28 Apr 2022 08:40:49 GMT',
      operation_type: 'DEPLOYMENT',
      started_at: 'Thu, 28 Apr 2022 08:40:48 GMT',
      wave_id: 1
    }],
    oracle_version: '19.3.0.0.0',
    source_hostname: 'new-stress-test-db-server49'
  };


  databaseOperationHistory$: Subject<DatabaseOperationsHistoryResponse> = new BehaviorSubject(this.databaseHistory);

  getDatabaseMappingsHistory(_: number | string): Observable<DatabaseOperationsHistoryResponse> {
    return of(this.databaseHistory);
  }

  getDeploymentDetails(waveId: number|string, deploymentId: number|string): Observable<DeploymentDetailsResponseMeta>  {
    const deploymentDetails: DeploymentDetailsResponseMeta = {
      data: [
        {
          operation_id: 1,
          operation_type: 'DEPLOYMENT',
          status: 'COMPLETE',
          wave_id: 1,
          source_db : {
            db_name: 'DB1',
            db_type: 'SI',
            oracle_version: '19.3.0.0.0',
            source_hostname: 'test-server-1'
          },
          bms: [{
            completed_at: 'Fri, 21 Jan 2022 21:01:23 GMT',
            id: 1,
            logs_url: 'https://console.cloud.google.com',
            mapping_id: 1,
            name: 'tests-cycle-1',
            started_at: 'Fri, 21 Jan 2022 19:29:08 GMT',
            step: 'SW_INSTALL'
          }]
        }
      ]
    }

    return of(deploymentDetails);
  }
}
