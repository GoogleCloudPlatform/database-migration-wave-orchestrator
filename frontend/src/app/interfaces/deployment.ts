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

export interface DeploymentResponse {
  data?: DeploymentResponse[];
  completed_at: string,
  id: number
  mappings_count: number,
  started_at: string,
  status: string,
  wave_id: number,
  wave_name: string,
}

export interface DeploymentData extends DeploymentResponse {
  details?: string,
  duration?: string,
}


export interface DeploymentDetailsResponseMeta {
  data: DeploymentDetailsResponse[];
}

export interface DeploymentDetailsResponse {
  bms: DeploymentDetailsBms[];
  operation_id: number;
  operation_type: string;
    source_db: {
    db_name: string,
    db_type: string,
    oracle_version: string,
    source_hostname: string,
  },
  status: string;
  wave_id: number;
}

export interface DeploymentDetailsBms {
  completed_at: string;
  id: number,
  logs_url: string,
  mapping_id: number,
  name: string;
  started_at: string;
  step: string;
}

export interface DeploymentDetailsData extends DeploymentDetailsResponse {
  database: string,
  log: string,
  source_hostname: string,
  target_hostname: string,
  type: string,
  version: string,
}
