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

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { DataTransferService } from '@app-services/data-transfer/data-transfer.service';
import { UtilService } from '@app-services/util/util.service';

import { ScheduleRestoreComponent } from '@app-modules/data-transfer-manager/components/schedule-restore/schedule-restore.component';
import { BaseMaterialTableComponent } from '@app-shared/components/base-material-table/base-material-table.component';

import { getDBType }  from "@app-shared/helpers/functions";

import { DataTransfer, DataTransferMeta, Operations, OperationStatus } from '@app-interfaces/data-transfer';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DialogData } from '@app-interfaces/dialog-data';
import { ConfirmDialogComponent } from '@app-shared/components/confirm-dialog/confirm-dialog.component';
import { ErrorsDialogComponent } from '../errors-dialog/errors-dialog.component';

@Component({
  selector: 'app-data-transfer-manager',
  templateUrl: './data-transfer-manager.component.html',
  styleUrls: ['./data-transfer-manager.component.scss']
})
export class DataTransferManagerComponent extends BaseMaterialTableComponent<DataTransfer> implements OnInit {
  displayedColumns = ['server', 'db_name', 'target_hostname', 'db_type', 'configuration', 'operation_type',
    'operation_status', 'action', 'logs_url'];
  showDataTable: boolean = false;
  operations = Operations;
  operationStatus = OperationStatus;
  private currentProjectId!: number;

  constructor(
    private dialog: MatDialog,
    private dataTransferService: DataTransferService,
    private utilService: UtilService,
    private snackBar: MatSnackBar,
  ) {
    super();
  }

  ngOnInit(): void {
    if (this.utilService.getCurrentProjectId() != null) {
      this.currentProjectId = this.utilService.getCurrentProjectId();
      this.getTransferMappings();

    }
  }

  getTransferMappings() {
    this.dataTransferService.getTransferMappings(this.currentProjectId).subscribe((response: DataTransferMeta) => {
      if (!response.data || !response.data[0]) return;

      this.showDataTable = true;
      this.initTable(response.data);
    })
  }

  scheduleRestore(row: any): void {
    this.dialog.open(ScheduleRestoreComponent, {
      panelClass: 'custom-dialog',
      role: 'dialog',
      data: { label: row?.db_name, id_db: row.id  },
      id: 'schedule-restore'
    });
  }

  run(id: number): void {
    this.startRestore(id);
  }

  private initTable(data: Array<DataTransfer>) {
    const dataTransferMigrations: Array<DataTransfer> = [];

    data.forEach((item) => {
      const data: DataTransfer = Object.create(item);

      data.server = item.server;
      data.db_name = item.db_name;
      data.bms = item.bms;
      data.db_type = getDBType(data.db_type);
      data.operation_type = item.operation_type;
      data.operation_status = item.operation_status;
      data.ready_to_restore = item.ready_to_restore;
      dataTransferMigrations.push(data);
    });

    this.initDataSource(dataTransferMigrations);
    this.setSorting();
  }

  private setSorting() {
    this.dataSource.sortingDataAccessor = (item, property) => {
      if (property === 'target_hostname') {
        return item.bms[0].name
      } else {
        let key = item[property as keyof DataTransfer]?.toLocaleString()
        return  key ? key : '';
      }
    };
  }

  startPreRestore(db_id: number) {
    this.dataTransferService.startPreRestore(db_id).subscribe(() => {
      this.getTransferMappings();
    },
    (error) => {
      this.openSnackBar(error);
    });
  }

  startRestore(db_id: number) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: <DialogData>{
        message: `By confirming this action, you start the restore process.
        Keep in mind that in order to maintain data consistency after switching over, the ability to update your current database should be turned off.
        Please, don't forget to switch over after the restore is completed.`,
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Start',
        cancelBtnText: 'Cancel',
        headerText: 'Start Restore?'
      },
      width: '550px',
      role: 'alertdialog',
      panelClass: 'custom-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if(result === true) {
        this.dataTransferService.startRestore(db_id).subscribe(() => {
          this.getTransferMappings();
        },
        (error) => {
          this.openSnackBar(error);
        });
      }
    });
  }

  startFailOver(db_id: number): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: <DialogData>{
        message: 'By this action, you going to switch the application to the new DB. This action can not be undone (restore will not be possible). Are you sure?',
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Start',
        cancelBtnText: 'Cancel',
        headerText: 'Start Failover?'
      },
      width: '550px',
      role: 'alertdialog',
      panelClass: 'custom-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if(result === true) {
        this.dataTransferService.startFailover(db_id).subscribe(() => {
          this.getTransferMappings();
        },
        (error) => {
          this.openSnackBar(error);
        });
      }
    });
  }

  startRollback(db_id: number) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: <DialogData>{
        message: 'With this action, you are going to rollback this restore operation. Are you sure you want to proceed?',
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Start',
        cancelBtnText: 'Cancel',
        headerText: 'Start Rollback?'
      },
      width: '550px',
      role: 'alertdialog',
      panelClass: 'custom-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if(result === true) {
        this.dataTransferService.startRollback(db_id).subscribe(() => {
          this.getTransferMappings();
        },
        (error) => {
          this.openSnackBar(error);
        });
      }
    });
  }

  showErrors(operation_id: number) {
    this.dialog.open(ErrorsDialogComponent, {
      data: <{operation_id: number}>{
        operation_id: operation_id
      },
      width: '80vw',
      height: '80vh',
      role: 'alertdialog',
      panelClass: 'custom-dialog'
    });

  }

  private openSnackBar(message: string): void {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }

  canRollback(row: DataTransfer): boolean {
    return !!(row.is_configure === true && row.next_operation?.some(e => e === this.operations.rollback_restore));
  }

  canRestore(row: DataTransfer): boolean {
    return !!(row.is_configure === true && row.next_operation?.some(e => e === this.operations.restore));
  }

  canPreRestore(row: DataTransfer): boolean {
    return !!(row.is_configure === true && row.next_operation?.some(e => e === this.operations.pre_restore));
  }

  canFailOver(row: DataTransfer): boolean {
    return !!(row.is_configure === true && row.next_operation?.some(e => e === this.operations.failover));
  }
}
