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

export interface SourceDb {
  data?: SourceDb[];
  allocated_memory?: number;
  arch?: string;
  cores?: number;
  db_type?: string;
  db_name?: string;
  db_size?: number;
  id?: number;
  rac_nodes?: number;
  project_id?: number;
  ram?: number;
  server?: string;
  status?: any;
  oracle_release?: string;
  oracle_version?: string;
  oracle_edition?: string;
  fe_rac_nodes?: number;
  wave_id?: number;
  labels?: SourceDbLabel[],
  db_engine?: string;
}

interface SourceDbLabel {
  name: string;
  id: number;
}
