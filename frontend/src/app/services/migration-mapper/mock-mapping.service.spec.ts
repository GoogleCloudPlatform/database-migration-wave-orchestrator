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

import { Observable, of } from "rxjs";

import { Mapping } from "@app-interfaces/mapping";
import { MappingTargets } from '@app-interfaces/mapping';

import { MappingService } from "./mapping.service";

export class MockMappingService extends MappingService {
    constructor() {
    super(jasmine.createSpyObj('HttpClient', { post: of({}), get: of({}) }));
  }

  getMigrationMappings(_:number): Observable<Mapping> {
    const mapping: Mapping = {
      bms: [
        {id: 1, name: 'test-cycle1'}
      ],
      db_id: 1,
      db_name: "test",
      id: 1,
      oracle_version: "12.1",
      source_hostname: "test",
      db_type: "RAC",
      oracle_release: "19.11.0.0.210412",
      fe_rac_nodes:1,
      wave_id:1
    }

    const mappings = {
      data: new Array(mapping),
      oracle_version: "12.1",
      bms:[],
      db_id:1
  }
    return of(mappings);
  }

  getMappingsByDbId(_:number): Observable<Mapping>{
    const mapping: Mapping = {
      bms: [
        {id: 1, name: 'test-cycle1'}
      ],
      db_id: 1,
      db_name: "test",
      id: 1,
      oracle_version: "18.1",
      source_hostname: "test",
      db_type: "RAC",
      oracle_release: "19.11.0.0.210412",
      fe_rac_nodes:1,
      wave_id:1
    }
    
    const mappingMeta = {
      data: new Array(mapping),
      bms: [
        {id: 1, name: 'test-cycle1'}
      ],
      db_id: 1,
      oracle_version: "12.1"
    }

    return of(mappingMeta);
  }

  editMigrationMapping(mapping: MappingTargets): Observable<any>{
    return of(mapping);
  }
}

