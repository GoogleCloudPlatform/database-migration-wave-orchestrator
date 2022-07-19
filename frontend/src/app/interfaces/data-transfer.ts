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

export interface DataTransferMeta {
  data: DataTransfer[];
}

export interface DataTransfer {
  id: number;
  server: string;
  db_name: string;
  db_type: string;
  is_configure: boolean;
  bms: DataTransferBMS[];
  operation_type: string;
  operation_status: string;
  status?: string;
  target_hostname?: string;
  ready_to_restore?: boolean;
  errors?: number;
  operation_id?: number,
  next_operation?: string[];
}

export interface DataTransferBMS {
  id: number;
  name: string;
  logs_url: string;
}

export interface DataTransferRestoreParameters {
  backup_location: string;
  rman_cmd: string;
  is_configured: boolean;
  pfile_content: string;
  backup_type: string;
  control_file: string;
  validations: Validations[];
}

export interface DataTransferRestoreInfo extends DataTransferRestoreParameters {
  db_name: string;
  listener_file: string|null;
  pfile_file: string;
  pwd_file: string|null;
  tnsnames_file: string|null;
}

export interface Validations {
  description: string;
  enabled: boolean;
  name: string;
}

export interface UploadSourceDbFileResp {
  content: string;
  url: string;
}

export interface UploadFileResp {
  url: string;
}

export enum OperationStatus {
  starting = 'STARTING',
  inProgress = 'IN_PROGRESS',
  complete = 'COMPLETE',
  failed = 'FAILED',
  completePartially ='COMPLETE_PARTIALLY',
}

export enum Operations {
  pre_restore = 'pre_restore',
  restore = 'restore',
  rollback_restore = 'rollback_restore',
  failover = 'failover'
}

export interface OperationError {
  name: string,
  details: string
}
