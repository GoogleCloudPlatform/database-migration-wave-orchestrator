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

import { ScheduleRestore } from "@app-interfaces/schedule-restore";

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class ScheduleRestoreService extends HttpService {
  getScheduleRestore(dbId: number): Observable<ScheduleRestore> {
    return this.http.get<ScheduleRestore>(this.apiURL + '/scheduled-tasks?db_id=' + dbId, this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  createScheduleRestore(scheduleParameters: any): Observable<{}> {
    return this.http.post<{}>(this.apiURL + '/scheduled-tasks',
      JSON.stringify(scheduleParameters), this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  updateScheduleRestore(dbId: number, scheduleParameters: any): Observable<{}> {
    return this.http.put<{}>(this.apiURL + '/scheduled-tasks/' + dbId,
      JSON.stringify(scheduleParameters), this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  deleteScheduleRestore(dbId: number): Observable<any> {
    return this.http.delete(this.apiURL + '/scheduled-tasks/'+ dbId, this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }
}
