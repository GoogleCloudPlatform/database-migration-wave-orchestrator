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

import { Component, TemplateRef, ViewChild, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from "@angular/forms";
import { SelectionModel } from "@angular/cdk/collections";
import { MatSnackBar } from "@angular/material/snack-bar";

import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";

const ELEMENT_DATA: any[] = [
  {position: 1, name: 'Hydrogen', weight: 1.0079, symbol: 'H'},
  {position: 2, name: 'Helium', weight: 4.0026, symbol: 'He'},
  {position: 3, name: 'Lithium', weight: 6.941, symbol: 'Li'},
  {position: 4, name: 'Beryllium', weight: 9.0122, symbol: 'Be'},
  {position: 5, name: 'Boron', weight: 10.811, symbol: 'B'},
  {position: 6, name: 'Carbon', weight: 12.0107, symbol: 'C'},
  {position: 7, name: 'Nitrogen', weight: 14.0067, symbol: 'N'},
  {position: 8, name: 'Oxygen', weight: 15.9994, symbol: 'O'},
  {position: 9, name: 'Fluorine', weight: 18.9984, symbol: 'F'},
  {position: 10, name: 'Neon', weight: 20.1797, symbol: 'Ne'},
];
@Component({
  selector: 'app-ui-kit',
  templateUrl: './ui-kit.component.html',
  styleUrls: ['./ui-kit.component.scss']
})
export class UiKitComponent extends BaseMaterialTableComponent<any> implements OnInit {
  form: FormGroup;
  radiobuttonValue = 4;
  mainLinks = [
    { name: 'Migration Projects' },
    { name: 'Software Library' },
    { name: 'Source Databases Inventory' },
    { name: 'Target (BMS) Inventory' },
    { name: 'Migration Mapper' },
    { name: 'Migration Wave Manager' },
    { name: 'Deployment History' },
  ];
  toppingList: string[] = ['Extra cheese', 'Mushroom', 'Onion', 'Pepperoni', 'Sausage', 'Tomato'];

  displayedColumns: string[] = ['select', 'name', 'weight', 'symbol', 'actions'];
  selection = new SelectionModel<any>(true, []);

  @ViewChild('error') error!: TemplateRef<any>;
  @ViewChild('warning') warning!: TemplateRef<any>;
  @ViewChild('success') success!: TemplateRef<any>;
  @ViewChild('info') info!: TemplateRef<any>;

  constructor(private formBuilder: FormBuilder, private snackBar: MatSnackBar) {
    super();
    this.form = this.formBuilder.group({
      toppingList: new FormControl('' , [Validators.required]),
      name: new FormControl('' , [Validators.required, Validators.maxLength(1)]),
    });
  }

  ngOnInit(): void {
    this.initDataSource(ELEMENT_DATA);
  }

  snackBarDismiss(): void {
    this.snackBar.dismiss();
  }

  openErrorSnackBar(): void {
    this.snackBar.openFromTemplate(this.error);
  }

  openWarningSnackBar(): void {
    this.snackBar.openFromTemplate(this.warning, {
      duration: 1000
    });
  }

  openSuccessSnackBar(): void {
    this.snackBar.openFromTemplate(this.success, {
      duration: 1000
    });
  }

  openInfoSnackBar(): void {
    this.snackBar.openFromTemplate(this.info, {
      duration: 1000
    });
  }

  masterToggle(): void {
    if (this.isAllSelected()) {
      this.selection.clear();
      return;
    }

    this.selection.select(...this.dataSource.data);
  }

  isAllSelected(): boolean {
    const numSelected = this.selection.selected.length;
    const numRows = this.dataSource.data.length;

    return numSelected === numRows;
  }

  checkboxLabel(row?: any): string {
    if (!row) {
      return `${this.isAllSelected() ? 'deselect' : 'select'} all`;
    }

    return `${this.selection.isSelected(row) ? 'deselect' : 'select'} row ${row.position + 1}`;
  }
}
