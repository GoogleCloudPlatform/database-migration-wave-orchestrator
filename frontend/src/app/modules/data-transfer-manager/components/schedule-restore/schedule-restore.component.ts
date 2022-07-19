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

import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ChangeDateTime } from "@app-interfaces/date-time";
import { DialogData } from '@app-interfaces/dialog-data';
import { ScheduleRestoreService } from '@app-services/schedule-restore/schedule-restore.service';
import { ConfirmDialogComponent } from '@app-shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-schedule-restore',
  templateUrl: './schedule-restore.component.html',
  styleUrls: ['./schedule-restore.component.scss']
})

export class ScheduleRestoreComponent implements OnInit {
  isValidForm = false;
  isScheduled = false;
  dateTime: string = '';
  id!: number;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: { label: string, id_db: number },
    private dialog: MatDialog,
    private scheduleRestoreService: ScheduleRestoreService,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    this.scheduleRestoreService.getScheduleRestore(this.data.id_db).subscribe((val: any) => {
      if (val?.data[0]) {
        this.isScheduled = true;
        this.dateTime = val.data[0].schedule_time;
        this.id = val.data[0].id;
      }
    });
  }

  schedule(): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, { 
      panelClass: 'custom-dialog', 
      role: 'alertdialog', 
      id: 'dialog2', 
      width: '550px',
      data: <DialogData>{
        message: `By confirming this action, you start the restore process.
        Keep in mind that in order to maintain data consistency after switching over, the ability to update your current database should be turned off.
        Please, don't forget to switch over after the restore is completed.`,
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Start',
        cancelBtnText: 'Cancel',
        headerText: 'Schedule Restore?'
      },
    });

    dialogRef?.afterClosed().subscribe(result => {
      if (result === true) {
        const restoreBody = {
          db_id: this.data.id_db,
          schedule_time: this.dateTime
        }

        if (this.id) {
          this.scheduleRestoreService.updateScheduleRestore(this.id, restoreBody).subscribe(
            () => {
              this.openSnackBar('Restore schedule updated successfully', 'Close');
            },
            (error) => {
              this.openSnackBar(error[0], 'Close');
            }
          );
        } else {
          this.scheduleRestoreService.createScheduleRestore(restoreBody).subscribe(
            () => {
              this.openSnackBar('Restore scheduled successfully', 'Close');
            },
            (error) => {
              this.openSnackBar(error[0], 'Close');             
            }
          );
        }
      }
    });
  }

  cancelSchedule(): void {
    if(this.id) {
      this.scheduleRestoreService.deleteScheduleRestore(this.id).subscribe(
        () => {},
        (error) => {
          this.snackBar.open(error[0], 'Close' , {
            duration: 5000,
          });
        }
      );
    }
  }

  openSnackBar(message: string, action: string) {
    this.snackBar.open(message, action , {
      duration: 5000
    });
  }

  changeDateTime($event: ChangeDateTime): void {
    this.isValidForm = $event.isValidForm;
    this.dateTime = $event.dateTime;
  }
}
