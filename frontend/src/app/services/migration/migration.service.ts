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
import { BehaviorSubject, Observable } from "rxjs";
import { catchError, retry } from "rxjs/operators";

import { Migration } from "@app-interfaces/migration";
import { Metadata } from "@app-interfaces/metadata";

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class MigrationService extends HttpService {
  private readonly projectListSource = new BehaviorSubject(<Migration>{});

  projectList(): Observable<Migration> {
    return this.projectListSource.asObservable();
  }

  getMigrationsProjects(): Observable<Migration> {
    return this.http.get<Migration>(this.apiURL + '/projects', this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  getAndStoreMigrationsProjects(): void {
    this.http.get<Migration>(this.apiURL + '/projects', this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
      .subscribe((response) => {
        this.projectListSource.next(response);
      });
  }

  getMetaData(): Observable<Metadata> {
    return this.http.get<Metadata>(this.apiURL + '/metadata', this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  getMigrationProject(id: number): Observable<Migration> {
    return this.http.get<Migration>(this.apiURL + '/projects/' + id)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }

  createMigrationProject(migration: any): Observable<Migration> {
    return this.http.post<Migration>(this.apiURL + '/projects', JSON.stringify(migration), this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  updateMigrationProject(id: number, migration: any): Observable<Migration> {
    return this.http.put<Migration>(this.apiURL + '/projects/' + id, JSON.stringify(migration), this.httpOptions)
      .pipe(
        catchError(this.handleError)
      )
  }

  deleteMigrationProjectPromise(id: number | undefined): Promise<Migration> {
    return this.http.delete<Migration>(this.apiURL + '/projects/' + id, this.httpOptions).toPromise();
  }
}
