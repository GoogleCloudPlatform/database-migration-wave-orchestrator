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

import { Component, Input, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { MatSnackBar } from '@angular/material/snack-bar';

import { AddWave, AddWaveResp, Wave } from '@app-interfaces/wave';

import { WaveService } from '@app-services/wave/wave.service';


@Component({
  selector: 'app-wave',
  templateUrl: './wave.component.html',
  styleUrls: ['./wave.component.scss']
})
export class WaveComponent implements OnInit {
  @Input() waves!: Wave[] | undefined;
  @Input() waveId: number | null = null;
  @Input() project_id!: number;
  @Input() db_id!: number;
  @Input() editable!: boolean;
  waveControl!: FormControl;
  filteredWaves!: Observable<Wave[] | undefined>;

  constructor(
    private waveService: WaveService,
    private snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.setWaveName();

    this.filteredWaves = this.waveControl.valueChanges.pipe(
      startWith(''),
      map(value => value.length > 1 ? this.filterWaves(value) : []),
    )
  }
  
  assignWave(): void {
    if (!this.waveValidation()) {
      return;
    }

    const waveObj: AddWave = {
      name: this.waveControl.value,
      project_id: this.project_id,
      db_ids: [this.db_id]
    };

    this.waveService.createMigrationWave(waveObj).subscribe((resp: AddWaveResp) => {
      if (resp.skipped || resp.unmapped) {
        this.openSnackBar(`The wave ${this.waveControl.value} is not assigned to the database`);
        return;
      }
      this.openSnackBar(`The wave ${this.waveControl.value} is assigned to the database`);
    },
    (error) => {
      this.openSnackBar(error);
    })
  }

  private setWaveName(): void {
    let waveName = '';
    if (this.waveId) {
      waveName = this.waves?.find((wave) => wave.id === this.waveId)!.name!;
    }

    this.waveControl = new FormControl({value: waveName, disabled: !this.editable}, [
      Validators.required,
      Validators.maxLength(30)
    ]);
  }

  private filterWaves(value: string): Wave[] | undefined {
    const filterValue = value.toLowerCase();

    return this.waves?.filter((wave) => wave.name.toLowerCase().includes(filterValue));
  }

  private waveValidation(): boolean {
    if (!this.waveControl.dirty) {
      return false;
    }

    if (!this.waveControl.value) {
      this.openSnackBar('Please choose or enter the name of wave');
      return false;
    }

    if (!this.waveControl.valid) {
      this.openSnackBar('The wave name is not valid');
      return false;
    }

    return true;
  }

  private openSnackBar(message:string) {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }
}
