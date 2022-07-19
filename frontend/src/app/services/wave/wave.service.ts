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
import { Observable, BehaviorSubject } from "rxjs";
import { catchError, retry } from "rxjs/operators";

import { AddWave, AddWaveResp, Wave } from '@app-interfaces/wave';

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class WaveService extends HttpService {
  refreshWaveList$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

  getMigrationWaves(id:number): Observable<Wave> {
    return this.http.get<Wave>(this.apiURL + '/waves?project_id=' + id, this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  createMigrationWave(wave: AddWave): Observable<AddWaveResp> {
    return this.http.post<AddWaveResp>(this.apiURL + '/waves', JSON.stringify(wave), this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  editMigrationWave(wave: Wave, id: number): Observable<Wave> {
    return this.http.put<Wave>(this.apiURL + '/waves/'+ id, JSON.stringify(wave), this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  getMigrationWave(id: number): Observable<Wave> {
    return this.http.get<Wave>(this.apiURL + '/waves/'+ id, this.httpOptions)
    .pipe(
      retry(1),
      catchError(this.handleError)
    )
  }

  getMigrationWaveDetails(id: number): Observable<Wave> {
    return this.http.get<Wave>(this.apiURL + '/waves/'+ id +'?details=True', this.httpOptions)
    .pipe(
      retry(1),
      catchError(this.handleError)
    )
  }

  startDeployment(id: number, mappings: object): Observable<any> {
    return this.http.post(this.apiURL + '/waves/'+ id +'/deployment', JSON.stringify(mappings),this.httpOptions)
    .pipe(
      retry(1),
      catchError(this.handleError)
    )
  }

  startCleanUp(id: number, mappings: object): Observable<any> {
    return this.http.post(this.apiURL + '/waves/'+ id +'/rollback', JSON.stringify(mappings),this.httpOptions)
    .pipe(
      retry(1),
      catchError(this.handleError)
    )
  }

  deleteWave(id: number): Observable<any> {
    return this.http.delete(this.apiURL + '/waves/'+ id, this.httpOptions)
    .pipe(
      retry(1),
      catchError(this.handleError)
    )
  }
}
