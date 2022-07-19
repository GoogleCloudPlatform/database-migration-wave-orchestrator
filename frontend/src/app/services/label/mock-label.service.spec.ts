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

import { Observable, of } from 'rxjs';

import { Label, LabelMeta } from '@app-interfaces/label';

import { LabelService } from './label.service';


export class MockLabelService extends LabelService {
  labels: LabelMeta = {
    data: [{
      name: 'label1',
      id: 1,
      project_id: 1 },
      {
      name: 'label2',
      id: 2,
      project_id: 1 },
      {
      name: 'label3',
      id: 3,
      project_id: 1
    }]
  }
  constructor() {
    super(jasmine.createSpyObj('HttpClient', { post: of({}), get: of({}) }));
  }

  getLabels(_: number): Observable<LabelMeta> {
    return of(this.labels);
  }

  addLabelSourceDb(_:number, label: Label): Observable<Label> {
    return of(label);
  }

  updateLabel(label: Label):  Observable<{}> {
    return of(label);
  }

  deleteLabelSourceDb(db_id: number, label_id: number): Observable<{}> {
    return of({});
  }

  getLabel(_: number): Observable<Label> {
    const label = {
      name: 'label1',
      id: 1,
      project_id: 1,
      db_count: 3
    }
    return of(label);
  }
}