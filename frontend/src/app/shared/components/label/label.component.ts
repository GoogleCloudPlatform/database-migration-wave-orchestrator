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

import { Component, Input, OnInit, ViewChild, OnDestroy, OnChanges } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { Observable, SubscriptionLike } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

import { MatAutocompleteTrigger } from '@angular/material/autocomplete';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Label } from '@app-interfaces/label';

import { LabelService } from '@app-services/label/label.service';


@Component({
  selector: 'app-label',
  templateUrl: './label.component.html',
  styleUrls: ['./label.component.scss']
})
export class LabelComponent implements OnInit, OnChanges, OnDestroy {
  @Input() labels: Label[] = [];
  @Input() projectId!: number;
  @Input() databaseId!: number;
  @Input() databaseLabels: Label[] = [];
  @ViewChild(MatAutocompleteTrigger) autocomplete!: MatAutocompleteTrigger;
  labelControl!: FormControl;
  filteredLabels!: Observable<Label[]>;
  labelSubscriptions: SubscriptionLike[] = [];
  isLabelSelected = false;
  isLabelExist = false;
  allLabelsShown = false;
  labelQuantityShown: number = 3;

  constructor(
    private labelService: LabelService,
    private snackBar: MatSnackBar
  ) { }

  ngOnInit(): void {
    this.labelControl = new FormControl('', [
      Validators.maxLength(15),
      Validators.pattern('^[A-Za-z][A-Za-z0-9-_]*(?:_[A-Za-z0-9]+)*$')
    ]);

    this.filteredLabels = this.labelControl.valueChanges.pipe(
      startWith(''),
      map(value => value.length > 1 ? this.filterLabels(value) : []),
    );

    this.labelSubscriptions.push(this.labelService.changeDatabaseLabel$.subscribe((label: Label) => {
      const changedLabel = this.databaseLabels.find((item) => item.id === label.id);
      if (changedLabel) {
        changedLabel.name = label.name;
      }
    }))

    this.labelSubscriptions.push(this.labelService.deleteDatabaseLabel$.subscribe((label: Label) => {
      this.databaseLabels = this.databaseLabels.filter((item) => item.id !== label.id);
    }))
  }

  ngOnChanges(): void {
    if (this.labelControl) {
      this.labelControl.updateValueAndValidity();
    }
  }

  ngOnDestroy(): void {
    this.labelSubscriptions.forEach(
      (subscription: SubscriptionLike) => subscription.unsubscribe());
    this.labelSubscriptions = [];
  }

  selectLabel(): void {
    this.isLabelSelected = true;
  }

  toggleLabelShown(): void {
   this.labelQuantityShown = this.labelQuantityShown === 3 ? this.databaseLabels.length : 3;
   this.allLabelsShown = !this.allLabelsShown;
  }

  addLabel(): void {
    this.autocomplete.closePanel();
    if (!this.validateAddLabel()) {
      return;
    }

    this.isLabelExist = this.labels.some((label) => label.name === this.labelControl.value);

    this.addLabelSourceDb();
  }

  deleteLabel(label: Label): void {
    const index = this.databaseLabels.indexOf(label);

    this.labelService.deleteLabelSourceDb(this.databaseId, label.id!).subscribe(() => {
      this.databaseLabels.splice(index, 1);
      this.openSnackBar(`Label '${label.name}' is deleted from database`);
    },
    (error) => {
      this.openSnackBar(error);
    });
  }

  private filterLabels(value: string): Label[] {
    const filterValue = value.toLowerCase();

    return this.labels.filter((label) => label.name.toLowerCase().includes(filterValue));
  }

  private validateAddLabel(): boolean {
    if (!this.labelControl.value) {
      return false;
    }

    if (!this.labelControl.valid) {
      this.labelControl.markAsTouched();
      return false;
    }

    const repeatedDatabaseLabel = () => this.databaseLabels.some((label) => label.name === this.labelControl.value);
    if (repeatedDatabaseLabel()) {
      this.openSnackBar(`Label '${this.labelControl.value}' already exists in database`);
      this.labelControl.setValue('');
      return false;
    }

    return true;
  }

  private addLabelSourceDb() {
    const label: Label = {
      name: this.labelControl.value
    }

    this.labelService.addLabelSourceDb(this.databaseId, label).subscribe((resp: Label) => {
      this.databaseLabels.push(resp);
      this.labelControl.setValue('');

      if (!this.isLabelSelected && !this.isLabelExist) {
        this.labelService.changeLabel$.next(true);
      }
    },
    (error) => {
      this.openSnackBar(error);
      this.labelControl.setValue('');
    });
  }

  private openSnackBar(message: string): void {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }
}