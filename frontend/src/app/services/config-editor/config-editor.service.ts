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

import { ConfigEditor } from "@app-interfaces/configEditor";

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class ConfigEditorService extends HttpService {
  getConfigEditor(dbId:number): Observable<ConfigEditor> {
    return this.http.get<ConfigEditor>(this.apiURL + `/source-dbs/${dbId}/config`, this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  createConfigEditorsingleInstance(migration: any , projectId: number): Observable<ConfigEditor> {
    return this.http.post<ConfigEditor>(this.apiURL + `/source-dbs/${projectId}/config`, JSON.stringify(migration), this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }
}
