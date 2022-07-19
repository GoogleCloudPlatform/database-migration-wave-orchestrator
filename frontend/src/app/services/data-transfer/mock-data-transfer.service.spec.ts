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

import { DataTransferMeta, DataTransferRestoreParameters, DataTransferRestoreInfo, UploadSourceDbFileResp, UploadFileResp } from '@app-interfaces/data-transfer';

import { DataTransferService } from './data-transfer.service';


export class MockDataTransferService extends DataTransferService{
  constructor() {
    super(jasmine.createSpyObj('HttpClient', { post: of({}), get: of({}) }));
  }

  getTransferMappings(): Observable<DataTransferMeta> {
    const transferedMappings: DataTransferMeta = {
      data: [
        {
          id: 1,
          server: 'srv-db-01',
          db_name: 'DB1',
          db_type: 'SI',
          is_configure: false,
          bms: [{
            id: 1,
            name: 'bms-target-01',
            logs_url: 'https://console.cloud.google.com/log'
          }],
          operation_type: 'PRE_RESTORE',
          operation_status: 'FAILED',
          errors: 1,
          operation_id: 111
        },
        {
          id: 2,
          server: 'srv-db-02',
          db_name: 'DB2',
          db_type: 'SI',
          is_configure: false,
          bms: [{
            id: 1,
            name: 'bms-target-02',
            logs_url: ''
          }],
          operation_type: 'BACKUP_RESTORE',
          operation_status: ''
        },
        {
          id: 3,
          server: 'srv-db-03',
          db_name: 'DB3',
          db_type: 'RAC',
          is_configure: false,
          bms: [{
            id: 1,
            name: 'bms-target-03',
            logs_url: 'https://console.cloud.google.com/log'},
            {
            id: 2,
            name: 'bms-target-04',
            logs_url: 'https://console.cloud.google.com/log'
          }],
          operation_type: 'ROLLBACK',
          operation_status: 'IN_PROGRESS'
        },
        {
          id: 4,
          server: 'srv-db-0n',
          db_name: 'DB4',
          db_type: 'SI',
          is_configure: false,
          bms: [{
            id: 1,
            name: 'bms-target-05',
            logs_url: 'https://console.cloud.google.com/log'}],
          operation_type: 'PRE_RESTORE',
          operation_status: 'COMPLETE'
        },
        {
          id:5,
          server: 'srv-db-05',
          db_name: 'DB5',
          db_type: 'SI',
          is_configure: true,
          bms: [{
            id: 1,
            name: 'bms-target-05',
            logs_url: 'https://console.cloud.google.com/log'}],
          operation_type: 'DEPLOYMENT',
          operation_status: '',
          status: 'DEPLOYED',
          next_operation: ['pre_restore']
        },
        {
          id:6,
          server: 'srv-db-06',
          db_name: 'DB6',
          db_type: 'SI',
          is_configure: true,
          bms: [{
            id: 1,
            name: 'bms-target-06',
            logs_url: 'https://console.cloud.google.com/log'
          }],
          operation_type: 'PRE_RESTORE',
          operation_status: 'STARTING'
        },
        {
          id:7,
          server: 'srv-db-07',
          db_name: 'DB7',
          db_type: 'SI',
          is_configure: true,
          bms: [{
            id: 1,
            name: 'bms-target-07',
            logs_url: 'https://console.cloud.google.com/log'}],
          operation_type: 'PRE_RESTORE',
          operation_status: 'COMPLETE',
          ready_to_restore: true,
          next_operation: ['restore']
        },
        {
          id:8,
          server: 'srv-db-08',
          db_name: 'DB8',
          db_type: 'SI',
          is_configure: true,
          bms: [{
            id: 1,
            name: 'bms-target-08',
            logs_url: 'https://console.cloud.google.com/log'
          }],
          operation_type: 'BACKUP_RESTORE',
          operation_status: 'STARTING',
          ready_to_restore: true,
          next_operation: []
        },
        {
          id:9,
          server: 'srv-db-09',
          db_name: 'DB9',
          db_type: 'SI',
          is_configure: true,
          bms: [{
            id: 1,
            name: 'bms-target-09',
            logs_url: 'https://console.cloud.google.com/log'
          }],
          operation_type: 'BACKUP_RESTORE',
          operation_status: 'STARTING',
          ready_to_restore: false,
          next_operation: ['rollback_restore']
        }
      ]
    };

    return of(transferedMappings);
  }

  createRestoreSettings(id: number, restoreParams: DataTransferRestoreParameters): Observable<{}> {
    return of({});
  }

  uploadSourceDbFile(formData: FormData, db_id: number): Observable<UploadSourceDbFileResp> {
    return of({
      content: 'A01.WORLD=\r\n  (DESCRIPTION =\r\n    (SDU = 32768)\r\n    (ADDRESS_LIST =\r\n',
      url: 'restore_configs/681/pfile.ora'
    });
  }

  deleteSourceDbFile(db_id: number): Observable<null> {
    return of(null);
  }

  uploadPasswordFile(formData: FormData, db_id: number): Observable<UploadFileResp> {
    return of({
      url: 'restore-configs/1/pwd_file.ora'
    });
  }

  deletePasswordFile(db_id: number): Observable<null> {
    return of(null);
  }

  uploadTsnamesFile(formData: FormData, db_id: number): Observable<UploadFileResp> {
    return of({
      url: 'restore-configs/1/tnsnames_file.ora'
    });
  }

  deleteTsnamesFile(db_id: number): Observable<null> {
    return of(null);
  }

  uploadListenerFile(formData: FormData, db_id: number): Observable<UploadFileResp> {
    return of({
      url: 'restore-configs/1/listener_file.ora'
    });
  }

  deleteListenerFile(db_id: number): Observable<null> {
    return of(null);
  }

  getRestoreSettings(_: number): Observable<DataTransferRestoreInfo> {
    const dataTransferInfo: DataTransferRestoreInfo = {
      db_name: 'db_1',
      backup_location: '',
      backup_type: '',
      is_configured: false,
      listener_file: null,
      pfile_content: '',
      pfile_file: '',
      pwd_file: null,
      rman_cmd: '',
      tnsnames_file: null,
      control_file: '',
      validations: [{
        description: '',
        enabled: false,
        name: ''
      }]
    }

    return of(dataTransferInfo);
  }
}
