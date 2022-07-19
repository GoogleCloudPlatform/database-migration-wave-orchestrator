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

import { Injectable } from '@angular/core';
import { Observable, Subject } from "rxjs";
import { catchError, tap } from "rxjs/operators";

import { DeploymentResponse, DeploymentDetailsResponseMeta } from "@app-interfaces/deployment";
import { Wave } from "@app-interfaces/wave";
import { DatabaseOperationsHistoryResponse } from "@app-interfaces/database-operations-history";

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class DeploymentHistoryService extends HttpService {
  public databaseOperationHistory$: Subject<DatabaseOperationsHistoryResponse> = new Subject();

  getDeploymentList(projectId: number): Observable<DeploymentResponse> {
    return this.http.get<DeploymentResponse>(this.apiURL + `/operations?project_id=${projectId}`, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  getDeploymentDetails(waveId: number|string, deploymentId: number|string): Observable<DeploymentDetailsResponseMeta> {
    const url = this.apiURL + `/waves/${waveId}/operations/${deploymentId}/details`;

    return this.http.get<DeploymentDetailsResponseMeta>(url, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  getWaveDetails(waveId: number|string): Observable<Wave> {
    const url = this.apiURL + `/waves/${waveId}?details=true`;

    return this.http.get<Wave>(url, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  getDatabaseMappingsHistory(databaseId: number|string): Observable<DatabaseOperationsHistoryResponse> {
    const url = this.apiURL + `/source-dbs/${databaseId}/operations_history`;

    return this.http.get<DatabaseOperationsHistoryResponse>(url, this.httpOptions)
      .pipe(
        tap(value => this.databaseOperationHistory$.next(value)),
        catchError(this.handleError),
      )
  }
}
