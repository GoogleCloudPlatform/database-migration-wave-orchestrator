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

import { Target } from "@app-interfaces/targets";

import { TargetsService } from "./targets.service";

export class MockTargetsService extends TargetsService {
  constructor() {
    super(jasmine.createSpyObj("HttpClient", { post: of({}), get: of({}) }));
  }

  getUnmappedTargetsProjects(_: number): Observable<Target> {
    const target: Target = {
      luns: [],
      data: [
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "test",
          created_at: "2022-02-09T08:52:44.158896",
          id: 111222,
          location: "europe-west-3",
          name: "test-bms",
          ram: "16",
          secret_name: "test secret name",
          socket: "test socket"
        },
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "test-2",
          created_at: "2022-02-09T08:52:44.158896",
          id: 1,
          location: "europe-west-3",
          name: "test-bms-2",
          ram: "16",
          secret_name: "test secret name 2",
          socket: "test socket 2"
        }
      ]
    };
    return of(target);
  }

  getAllTargetsProjects(): Observable<Target> {
    const target: Target = {
      luns: [],
      data: [
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "6",
          created_at: "2022-02-07T10:42:26.731344",
          id: 111333,
          location: "europe-west-2",
          name: "test-bms-2",
          ram: "20",
          secret_name: "projects/583108012640/secrets/gce-target-test-02",
          socket: "test socket 2"
        },
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "4",
          created_at: "2022-02-09T08:52:44.158896",
          id: 111222,
          location: "europe-west-3",
          name: "test-bms",
          ram: "16",
          secret_name: "projects/583108012640/secrets/gce-target-test-01",
          socket: "test socket"
        },
      ]
    };
    return of(target);
  }

  getTargetsProjects(): Observable<Target> {
    const target: Target = {
      luns: [],
      data: [
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "6",
          created_at: "2022-02-07T10:42:26.731344",
          id: 111333,
          location: "europe-west-2",
          name: "test-bms-2",
          ram: "20",
          secret_name: "projects/583108012640/secrets/gce-target-test-02.",
          socket: "test socket 2"
        },
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "4",
          created_at: "2022-02-09T08:52:44.158896",
          id: 111222,
          location: "europe-west-3",
          name: "test-bms",
          ram: "16",
          secret_name: "projects/583108012640/secrets/gce-target-test-01",
          socket: "test socket"
        },
      ]
    };
    return of(target);
  }

  getTargetsProject(): Observable<Target> {
    const target: Target = {
      luns: [],
      data: [
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "6",
          created_at: "2022-02-07T10:42:26.731344",
          id: 111333,
          location: "europe-west-2",
          name: "test-bms-2",
          ram: "20",
          secret_name: "projects/583108012640/secrets/gce-target-test-02.",
          socket: "test socket 2"
        },
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "4",
          created_at: "2022-02-09T08:52:44.158896",
          id: 111222,
          location: "europe-west-3",
          name: "test-bms",
          ram: "16",
          secret_name: "projects/583108012640/secrets/gce-target-test-01",
          socket: "test socket"
        },
      ]
    };
    return of(target);
  }

  startTargetsDiscovery(): Observable<Target> {
    const target: Target = {
      luns: [],
      data: [
        {
          luns: [],
          data: [],
          client_ip: "10.132.0.55",
          cpu: "4",
          created_at: "2022-02-07T10:42:26.731344",
          id: 111222,
          location: "europe-west-3",
          name: "test-bms",
          ram: "16",
          secret_name: "test secret name",
          socket: "test socket"
        }
      ]
    };
    return of(target);
  }
}

