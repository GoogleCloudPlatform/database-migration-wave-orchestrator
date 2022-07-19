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

export interface Wave {
  data?: Wave[];
  project_id: number,
  id: number,
  name: string,
  is_running: boolean,
  status_rate?: {
    deployed: number,
    failed: number,
    undeployed: number
  }
  mappings_count?: number,
  mappings? : {
    bms: {
      bms_id: number,
      bms_name: string,
      operation_status: string | null,
      operation_step: string | null,
      logs_url?:string,
    }[],
    has_secret_name?: boolean,
    db_id: number,
    db_name: string,
    db_type: string,
    operation_id: number | null,
    operation_status: string,
    operation_type: string | null,
    server: string,
    is_deployable?: boolean,
    is_configured?: boolean
  }[],
  curr_operation? : {
    completed_at: string,
    id: number
    operation_type: string,
    started_at: string
  },
  last_deployment?: {
    completed_at: string,
    id: number
    operation_type: string,
    started_at: string
  }
  showDetails?: boolean;
  step?: {
    curr_step: number,
    total_steps: number
  }
}

export interface AddWave {
  name: string;
  project_id: number;
  db_ids?: number[];
}

export interface AddWaveResp {
  assigned?: number;
  skipped?: number;
  unmapped?: number;
}