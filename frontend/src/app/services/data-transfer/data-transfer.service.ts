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
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { DataTransferMeta, DataTransferRestoreParameters, UploadSourceDbFileResp,
DataTransferRestoreInfo, UploadFileResp, OperationError } from '@app-interfaces/data-transfer';

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class DataTransferService extends HttpService {
  getTransferMappings(databaseId: number): Observable<DataTransferMeta> {
    return this.http.get<DataTransferMeta>(this.apiURL + '/restore/source-dbs?project_id=' + databaseId, this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  getRestoreSettings(dbId: number): Observable<DataTransferRestoreInfo> {
    return this.http.get<DataTransferRestoreInfo>(this.apiURL + '/restore/source-dbs/' + dbId + '/config' , this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  createRestoreSettings(dbId: number, restoreParameters: DataTransferRestoreParameters): Observable<{}> {
    return this.http.post<DataTransferRestoreParameters>(this.apiURL + '/restore/source-dbs/' + dbId + '/config',
      JSON.stringify(restoreParameters), this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  uploadSourceDbFile(formData: FormData, db_id: number): Observable<UploadSourceDbFileResp> {
    return this.http.post<UploadSourceDbFileResp>(this.apiURL + `/restore/source-dbs/${db_id}/config/pfile`, formData, this.httpOptionsFD)
      .pipe(
        catchError(this.handleError)
      )
  }

  deleteSourceDbFile(db_id: number): Observable<null> {
    return this.http.delete<null>(this.apiURL + `/restore/source-dbs/${db_id}/config/pfile`, this.httpOptionsFD)
      .pipe(
        catchError(this.handleError)
      )
  }

  uploadPasswordFile(formData: FormData, db_id: number): Observable<UploadFileResp> {
    return this.http.post<UploadFileResp>(this.apiURL + `/restore/source-dbs/${db_id}/config/pwd_file`, formData, this.httpOptionsFD)
      .pipe(
        catchError(this.handleError)
      )
  }

  deletePasswordFile(db_id: number): Observable<null> {
    return this.http.delete<null>(this.apiURL + `/restore/source-dbs/${db_id}/config/pwd_file`, this.httpOptionsFD)
    .pipe(
      catchError(this.handleError)
    )
  }

  uploadTsnamesFile(formData: FormData, db_id: number): Observable<UploadFileResp> {
    return this.http.post<UploadFileResp>(this.apiURL + `/restore/source-dbs/${db_id}/config/tnsnames_file`, formData, this.httpOptionsFD)
      .pipe(
        catchError(this.handleError)
      )
  }

  deleteTsnamesFile(db_id: number): Observable<null> {
    return this.http.delete<null>(this.apiURL + `/restore/source-dbs/${db_id}/config/tnsnames_file`, this.httpOptionsFD)
    .pipe(
      catchError(this.handleError)
    )
  }

  uploadListenerFile(formData: FormData, db_id: number): Observable<UploadFileResp> {
    return this.http.post<UploadFileResp>(this.apiURL + `/restore/source-dbs/${db_id}/config/listener_file`, formData, this.httpOptionsFD)
      .pipe(
        catchError(this.handleError)
      )
  }

  deleteListenerFile(db_id: number): Observable<null> {
    return this.http.delete<null>(this.apiURL + `/restore/source-dbs/${db_id}/config/listener_file`, this.httpOptionsFD)
    .pipe(
      catchError(this.handleError)
    )
  }

  startPreRestore(db_id: number): Observable<any> {
    return this.http.post(this.apiURL + '/operations/pre-restores', JSON.stringify({"db_id" : db_id}),this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  startRestore(db_id: number): Observable<any> {
    return this.http.post(this.apiURL + '/operations/restores', JSON.stringify({"db_id" : db_id}),this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  startRollback(db_id: number): Observable<any> {
    return this.http.post(this.apiURL + '/operations/rollback-restores', JSON.stringify({"db_id" : db_id}),this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  startFailover(db_id: number): Observable<any> {
    return this.http.post(this.apiURL + '/operations/dt-failover', JSON.stringify({"db_id" : db_id}),this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  getOperationErrors(operation_id: number): Observable<OperationError[]> {
    return this.http.get<OperationError[]>(this.apiURL + '/operations/' + operation_id + '/errors', this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }
}
