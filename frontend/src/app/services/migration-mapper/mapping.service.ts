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

import { Mapping } from '@app-interfaces/mapping';
import { MappingTargets } from '@app-interfaces/mapping';

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class MappingService extends HttpService {
  getMigrationMappings(id:number): Observable<Mapping> {
    return this.http.get<Mapping>(this.apiURL + '/mappings?project_id=' + id , this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  getMappingsByDbId(id:number|string): Observable<Mapping> {
    return this.http.get<Mapping>(this.apiURL + '/mappings?db_id=' + id , this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  createMigrationMapping(mapping: MappingTargets): Observable<any> {
    return this.http.post<any>(this.apiURL + '/mappings', JSON.stringify(mapping), this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  editMigrationMapping(mapping: MappingTargets): Observable<any> {
    return this.http.put<any>(this.apiURL + '/mappings', JSON.stringify(mapping), this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }
}
