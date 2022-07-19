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

import { AddWave, AddWaveResp, Wave } from "@app-interfaces/wave";

import { WaveService } from "./wave.service";

export const WAVE_DETAILED = {
    project_id: 1,
    id: 1,
    name: "wave1",
    is_running: false,
    mappings: []
}

export const WAVE_OPERATION = {
    completed_at: "Tue, 04 Jan 2022 15:55:48 GMT",
    id: 21,
    operation_type: "DEPLOYMENT",
    started_at: "Tue, 04 Jan 2022 15:55:47 GMT",
}

export const WAVE_MAPPING = {
    bms: [{
        bms_id: 1,
        bms_name: "test",
        operation_status: "FAILED",
        operation_step: "PRE_DEPLOYMENT",
    }],
    db_id: 1,
    db_name: "test",
    db_type: "SI",
    operation_id: 16,
    operation_status: "FAILED",
    operation_type: "DEPLOYMENT",
    server: "test",
    is_deployable: false,
    is_configured: true,
    has_secret_name: true
}

export const UNDEPLOYED_WAVE_MAPPING = {
    bms: [{
        bms_id: 1,
        bms_name: "test",
        operation_status: null,
        operation_step: null,
    }],
    db_id: 2,
    db_name: "test2",
    db_type: "SI",
    operation_id: null,
    operation_status: "",
    operation_type: null,
    server: "test2",
    is_deployable: true,
    is_configured: false,
    has_secret_name: false
}

export class MockWaveService extends WaveService {
    constructor() {
		super(jasmine.createSpyObj('HttpClient', { post: of({}), get: of({}) }));
	}

    getMigrationWaves(_: number): Observable<any> {
        const wave: Wave = {
            project_id: 1,
            id: 1,
            name: "wave1",
            is_running: false,
        }

        const waves = {
            data: new Array(wave)
        }

        return of(waves);
    }

    getMigrationWaveDetails(_: number): Observable<Wave> {
        const wave: Wave ={
            project_id: 1,
            id: 1,
            name: "wave1",
            is_running: false,
            mappings: []
        };
        return of(wave);
    }

    createMigrationWave(wave: AddWave):Observable<AddWaveResp> {
      return of({});
    }
}

