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
import { FormControl, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

import { AssignWaveDialogData } from '@app-interfaces/migration';
import { Wave } from '@app-interfaces/wave';


@Component({
  selector: 'app-wave-assign',
  templateUrl: './wave-assign.component.html',
  styleUrls: ['./wave-assign.component.scss']
})
export class WaveAssignComponent implements OnInit {
  waves: Wave[] | undefined;
  waveControl!: FormControl;
  filteredWaves!: Observable<Wave[] | undefined>;

  constructor(
    private snackBar: MatSnackBar,
    public dialogRef: MatDialogRef<WaveAssignComponent>,
    @Inject(MAT_DIALOG_DATA) public data: AssignWaveDialogData
  ) { }

  ngOnInit(): void {
    this.waveControl = new FormControl('', [Validators.maxLength(30)]);

    this.waves = this.data.waves;
    this.filteredWaves = this.waveControl.valueChanges.pipe(
      startWith(''),
      map(value => value.length > 1 ? this.filterWaves(value) : []),
    );
  }

  assignWave(): void {
    if (!this.waveControl.value) {
      this.openSnackBar('Please choose a wave');
      return;
    }
    this.dialogRef.close({ event: 'assign', wave: this.waveControl.value });
  }

  private filterWaves(value: string): Wave[] | undefined {
    const filterValue = value.toLowerCase();

    return this.waves?.filter((wave) => wave.name.toLowerCase().includes(filterValue));
  }

  private openSnackBar(message:string) {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }
}
