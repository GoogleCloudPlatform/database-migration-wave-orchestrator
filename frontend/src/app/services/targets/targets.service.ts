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
import { HttpErrorResponse, HttpParams } from "@angular/common/http";
import { Observable, throwError } from "rxjs";
import { catchError, retry } from "rxjs/operators";

import { Target } from "@app-interfaces/targets";

import { HttpService } from '@app-services/http/http.service';


@Injectable({
  providedIn: 'root'
})
export class TargetsService extends HttpService {
  getAllTargetsProjects(): Observable<Target> {
    return this.http.get<Target>(this.apiURL + '/targets', this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  getUnmappedTargetsProjects(id: number): Observable<Target> {
    const params = new HttpParams()
      .set('project_id', id + '')
      .set('unmapped', 'true');

    return this.http.get<Target>(this.apiURL + '/targets', { headers: this.httpOptions.headers, params })
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  getTargetsProject(id: number): Observable<Target> {
    return this.http.get<Target>(this.apiURL + '/targets/' + id)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  getTargetsProjects(id: number): Observable<Target> {
    return this.http.get<Target>(this.apiURL + '/targets?project_id=' + id + '&unmapped=True')
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  createTargetsProject(migration: any): Observable<Target> {
    return this.http.post<Target>(this.apiURL + '/targets', JSON.stringify(migration), this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  updateTargetsProject(id: number, migration: any): Observable<Target> {
    return this.http.put<Target>(this.apiURL + '/targets/' + id, JSON.stringify(migration), this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  deleteTargetsProject(id: number | undefined){
    if (id === undefined)
      return;
    return this.http.delete<Target>(this.apiURL + '/targets/' + id, this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  uploadTargetFile(formData: FormData) {
    return this.http.post<any>(this.apiURL + '/targets/upload', formData, this.httpOptionsFD)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  startTargetsDiscovery() {
    return this.http.post(this.apiURL + '/targets/discovery', null)
     .pipe(
       retry(1),
       catchError(this.handleError)
     )
  }

  handleError(error: HttpErrorResponse) {   
    const errors = error.error.errors;    
    let errorMsgs: string = '';
    for (const [key, value] of Object.entries(errors)) {
      if(Array.isArray(value)) {
        errorMsgs += key.slice(0, -1) + ': ' + value.join(', ') + '. ';
      }
    }    
    return throwError(errorMsgs);   
  }
}
