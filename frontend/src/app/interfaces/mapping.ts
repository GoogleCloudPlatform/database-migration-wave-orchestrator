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

export interface Mapping {
  data?: Mapping[];
  bms: Bms[],
  db_id: number,
  db_name?: string,
  id?: number,
  oracle_version: string,
  source_hostname?: string,
  target_hostname?: string,
  wave_id?: number,
  nodes_amount?: number;
  nodes?: Node[];
  db_type?: string;
  fe_rac_nodes?: number;
  oracle_release?: string;
  db_type_text?: string;
  is_deployed?: boolean;
  editable?: boolean;
  target_db_tool_id?: number;
}

export interface Node {
  label: string;
  value: number | null | string;
}

export interface Bms {
  id: number,
  name: string
}

export enum DB_Types{
  "RAC" = "Real Application Cluster",
  "SI" = "Single Instance",
  "DG" = "DG"
}

export interface MappingTargets{
  db_id: number;
  bms_id: number[];
  fe_rac_nodes: number;
  wave_id?: number;
}
