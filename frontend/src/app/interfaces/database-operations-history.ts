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

export interface DatabaseOperationsHistoryResponse {
  db_name: string;
  db_type: string;
  id: number;
  operations: DatabaseOperationsHistoryDetails[];
  oracle_version: string;
  source_hostname: string;
}

export interface DatabaseOperationsHistoryDetails {
  bms: DatabaseOperationsHistoryBms[];
  completed_at: string;
  operation_type: string;
  started_at: string;
  wave_id: number;
}

export interface DatabaseOperationsHistoryBms {
  id: number;
  logs_url: string;
  name: string;
  operation_status: string;
}

