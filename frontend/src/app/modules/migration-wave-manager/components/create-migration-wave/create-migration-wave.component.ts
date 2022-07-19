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
import { FormControl, FormGroup, FormGroupDirective, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Wave } from '@app-interfaces/wave';
import { SlidingPanelConfig } from '@app-interfaces/sliding-panel-config';

import { NotificationService } from '@app-services/notification/notification.service';
import { UtilService } from '@app-services/util/util.service';
import { WaveService } from '@app-services/wave/wave.service';
import { SlidingPanelService } from '@app-services/sliding-panel/sliding-panel.service';

@Component({
  selector: 'app-create-migration-wave',
  templateUrl: './create-migration-wave.component.html',
  styleUrls: ['./create-migration-wave.component.scss']
})
export class CreateMigrationWaveComponent implements OnInit{
  project_id!: number;
  isEditing = false;
  wave_id!: number;
  migrationWaveForm: FormGroup = new FormGroup({
    name:             new FormControl('' , [Validators.required, Validators.maxLength(30)]),
    project_id:       new FormControl(''),
  });

  constructor(
    private waveService: WaveService,
    private util:UtilService,
    private notificationService: NotificationService,
    private snackBar: MatSnackBar,
    private slidingPanelService: SlidingPanelService,
  ) {}

  ngOnInit(): void {
    this.slidingPanelService.slidingPanelConfig$.subscribe((val: SlidingPanelConfig) => {
      if (val.editMode) {
        this.isEditing = true;
        this.wave_id = val.waveId || 0;
        this.getWaveInfo();
      }

      if (this.util.getCurrentProjectId() != null) {
        this.project_id = this.util.getCurrentProjectId();
        this.migrationWaveForm.get('project_id')?.setValue(this.project_id);
      }
    });
  }

  getWaveInfo(): void {
    this.waveService.getMigrationWave(this.wave_id).subscribe((wave: Wave) => {
      this.migrationWaveForm.get('name')?.setValue(wave.name);
    })
  }

  onSubmit(formDirective: FormGroupDirective): void {
    if (this.migrationWaveForm.valid) {
      if (this.migrationWaveForm.value.project_id === null) {
        this.migrationWaveForm.get('project_id')?.setValue('');
      }

      if (this.isEditing) {
        this.waveService.editMigrationWave(this.migrationWaveForm.value, this.wave_id)
          .subscribe(
            () => {
              this.openSnackBar(this.notificationService.GENERAL_SUCCESS_MESSAGE);
              this.waveService.refreshWaveList$.next(true);
            },
            (error) => {
              this.openSnackBar(error);
            }
          );
      } else {
        this.waveService.createMigrationWave(this.migrationWaveForm.value)
          .subscribe(
            () => {
              this.openSnackBar(this.notificationService.GENERAL_SUCCESS_MESSAGE);
              this.migrationWaveForm.reset();
              formDirective.resetForm();
              this.waveService.refreshWaveList$.next(true);
            },
            (error) => {
              this.openSnackBar(error);
            }
          );
      }
      this.closePanel(formDirective);
    }
  }

  cancel(formDirective: FormGroupDirective): void {
    this.closePanel(formDirective);
  }

  openSnackBar(message:string): void {
    this.snackBar.open(message, 'Accept' , {
      duration: 5000,
    });
  }


  private closePanel(formDirective: FormGroupDirective): void {
    this.migrationWaveForm.reset();
    formDirective.resetForm();
    this.slidingPanelService.closePanel$.next(true);
  }
}
