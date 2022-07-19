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
import { Observable, Subject, BehaviorSubject } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { LabelMeta, Label } from '@app-interfaces/label';

import { HttpService } from '@app-services/http/http.service';


@Injectable({
  providedIn: 'root'
})
export class LabelService extends HttpService {
  changeLabel$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  changeDatabaseLabel$: Subject<Label> = new Subject<Label>();
  deleteDatabaseLabel$: Subject<Label> = new Subject<Label>();

  getLabels(projectId: number): Observable<LabelMeta> {
    return this.http.get<LabelMeta>(this.apiURL + '/labels?project_id=' + projectId, this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  getLabel(label_id: number): Observable<Label> {
    return this.http.get<Label>(this.apiURL + '/labels/' + label_id + '?db_count=True', this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  addLabelSourceDb(db_id: number, label: Label): Observable<Label> {
    return this.http.post<Label>(this.apiURL + '/source-dbs/' + db_id + '/labels',
    JSON.stringify(label), this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  updateLabel(label: Label):  Observable<{}> {
    const updateLabel: Label = {
      name: label.name
    }
    return this.http.put<Label>(this.apiURL + '/labels/' + label.id,
    JSON.stringify(updateLabel), this.httpOptions)
    .pipe(
      catchError(this.handleError)
    )
  }

  deleteLabel(label_id: number):  Observable<{}> {
    return this.http.delete(this.apiURL + '/labels/' + label_id, this.httpOptions);
  }

  deleteLabelSourceDb(db_id: number, label_id: number):  Observable<{}> {
    return this.http.delete(this.apiURL + '/source-dbs/' + db_id + '/labels/' + label_id, this.httpOptions);
  }
}
