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

import { Component, OnDestroy, OnInit } from '@angular/core';
import { SubscriptionLike } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Label, LabelMeta } from '@app-interfaces/label';
import { LabelService } from '@app-services/label/label.service';
import { UtilService } from '@app-services/util/util.service';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../confirm-dialog/confirm-dialog.component';
import { DialogData } from '@app-interfaces/dialog-data';
import { NgModel } from '@angular/forms';
import { SlidingPanelService } from '@app-services/sliding-panel/sliding-panel.service';


@Component({
  selector: 'app-manage-labels',
  templateUrl: './manage-labels.component.html',
  styleUrls: ['./manage-labels.component.scss']
})

export class ManageLabelsComponent implements OnInit, OnDestroy {
  project_id!: number;
  labels: Label[] = [];
  labelSubscriptions: SubscriptionLike[] = [];
  patternForLabel = '^[A-Za-z][A-Za-z0-9-_]*(?:_[A-Za-z0-9]+)*$';
  initialLabelValue!: string;

  constructor(
    private util:UtilService,
    private labelService: LabelService,
    private slidingPanelService: SlidingPanelService,
    public dialog: MatDialog,
    private snackBar: MatSnackBar,
  ) {}

  ngOnInit(): void {
    if (this.util.getCurrentProjectId() != null) {
      this.project_id = this.util.getCurrentProjectId();
    }
    this.getLabels();

    this.labelSubscriptions.push(this.labelService.changeLabel$.subscribe((val: boolean) => {
      if (val) {
        this.getLabels();
      }
    }));
  }

  getLabels(): void {
    this.labelSubscriptions.push(this.labelService.getLabels(this.project_id).subscribe((resp: LabelMeta) => {
      this.labels = resp.data;
    }))
  }

  checkValue(model: NgModel): void {
    this.initialLabelValue = model.model;
  }

  updateLabel(label: Label, inValid: boolean, model: NgModel): void {
    if(inValid || model.pristine) {
        return;
    }
    if (label.name === this.initialLabelValue) {
      return;
    }

    this.initialLabelValue = label.name;

    this.labelService.updateLabel(label).subscribe(() => {
        this.openSnackBar(`Label '${label.name}' is updated`);

        this.labelService.changeLabel$.next(true);
        this.labelService.changeDatabaseLabel$.next(label);
      },
      (error) => {
        this.openSnackBar(error);
      });
  }

  deleteLabel(label:Label): void {
    if (!label)
      return;
    this.labelService.getLabel(label.id!).subscribe((resp: Label) => {
      if (!resp) return;
      this.showConfirmationDialog(`${label.name} is linked to ${resp.db_count} source databases. Are you sure you want to delete it? This action can not be reverted.`)?.afterClosed().subscribe(result => {
        if (!result)  return;

        this.labelService.deleteLabel(label.id!).subscribe(() => {
          this.openSnackBar(`Label '${label.name}' is deleted from database`);

          this.labelService.changeLabel$.next(true);
          this.labelService.deleteDatabaseLabel$.next(label);
        },
        (error) => {
          this.openSnackBar(error);
        });
      });
    })
  }

  showConfirmationDialog(message: string): MatDialogRef<ConfirmDialogComponent>{
    return this.dialog.open(ConfirmDialogComponent, {
      width: '350px',
      data: <DialogData>{
        message: message,
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Accept',
        cancelBtnText: 'Cancel',
        headerText: 'Confirm'
      },
      ariaLabel: 'delete-label-confirmation-dialog',
      panelClass: 'custom-dialog'
    })
  }

  private openSnackBar(message: string): void {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }

  close(): void {
    this.slidingPanelService.closePanel$.next(true);
  }

  ngOnDestroy(): void {
    this.labelSubscriptions.forEach(
      (subscription: SubscriptionLike) => subscription.unsubscribe());
    this.labelSubscriptions = [];
  }
}
