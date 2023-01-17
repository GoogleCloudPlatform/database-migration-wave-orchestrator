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
import { Observable } from "rxjs";
import { catchError, retry } from "rxjs/operators";

import { ConfigEditorDms } from "@app-interfaces/configEditorDms";

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class ConfigEditorDmsService extends HttpService {
  getConfigEditor(dbId:number): Observable<ConfigEditorDms> {
    return this.http.get<ConfigEditorDms>(this.apiURL + `/source-dbs/${dbId}/config-dms`, this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  createConfigEditorsingleInstance(migration: any , projectId: number): Observable<ConfigEditorDms> {
    return this.http.post<ConfigEditorDms>(this.apiURL + `/source-dbs/${projectId}/config-dms`, JSON.stringify(migration), this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }
}
