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

import { SubscriptionLike } from 'rxjs';
import {Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatSnackBar } from "@angular/material/snack-bar";
import { Sort } from "@angular/material/sort";

import { LabelMeta, Label } from '@app-interfaces/label';
import { SourceDb } from "@app-interfaces/sourceDb";
import { LabelService } from '@app-services/label/label.service';
import { SlidingPanelService } from '@app-services/sliding-panel/sliding-panel.service';

import { SourceDbService } from "@app-services/source-db/source-db.service";
import { UtilService } from '@app-services/util/util.service';

import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";
import { getDBType } from '@app-shared/helpers/functions';

@Component({
  selector: 'app-source-databases',
  templateUrl: './source-databases.component.html',
  styleUrls: ['./source-databases.component.scss']
})
export class SourceDatabasesComponent extends BaseMaterialTableComponent<SourceDb> implements OnInit, OnDestroy {
  @ViewChild("fileUpload", {static: false}) fileUpload!: ElementRef;
  currentProjectId!: number;
  showDataTable: boolean = false;
  overrideDatabase: boolean = false;
  displayedColumns = [ 'server' , 'db_name' , 'oracle_version' , 'db_type', 'label'];
  ELEMENT_DATA: SourceDb[] | undefined;
  files = [];
  labels: Label[] = [];
  labelFilter: string[] = [];
  labelsList: any[] = [];
  subscriptions: SubscriptionLike[] = [];

  constructor(
    private sourceDbService: SourceDbService,
    private labelService: LabelService,
    private utilService: UtilService,
    private snackBar: MatSnackBar,
    private slidingPanelService: SlidingPanelService,
  ) {
    super();
  }

  ngOnInit(): void {
    localStorage.removeItem('filterState');
    if (this.utilService.getCurrentProjectId() != null) {
      this.currentProjectId = this.utilService.getCurrentProjectId();
    }
    this.getSourceDbs();
    this.getLabels();

    this.subscriptions.push(this.labelService.changeLabel$.subscribe((val: boolean) => {
      if (val) {
        this.getLabels();
      }
    }));
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(
      (subscription: SubscriptionLike) => subscription.unsubscribe());
    this.subscriptions = [];
  }

  applyLabelsFilter(): void {
    this.dataSource.filter = this.labelFilter.toString().trim();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  selectNoLabel(): void {
    this.labelFilter = ['no_label'];
    this.applyLabelsFilter();
  }

  resetLabelFilter(): void {
    this.labelFilter = [];
    this.applyLabelsFilter();
  }

  setCurrentElement(): void {
    this.removeItemOnce(this.labelFilter, 'no_label');   
    this.applyLabelsFilter();
  }

  getSourceDbs() {
    this.sourceDbService.getSourceDbsProjects(this.currentProjectId).subscribe((resp) => {
      this.ELEMENT_DATA = resp.data;
      if(this.ELEMENT_DATA?.length) {
        this.showDataTable = true;
        this.initTableData(this.ELEMENT_DATA);

        if (this.dataSource?.sort) {
          const sortState: Sort = { active: 'server', direction: 'asc' };

          this.dataSource.sort.active = sortState.active;
          this.dataSource.sort.direction = sortState.direction;
          this.dataSource.sort.sortChange.emit(sortState);
        }

        this.setFilterPredicate();
      }
    })
  }

  getLabels(): void {
    this.labelService.getLabels(this.currentProjectId).subscribe((resp: LabelMeta) => {
      this.labels = resp.data;
      this.sortLabels();
      this.createLabelsList();
    })
  }

  manageLabels(event: Event): void {
    event.stopPropagation();
    this.slidingPanelService.slidingPanelConfig$.next({ name: 'label', editMode: false });
  }

  uploadFile() {
    const fileUpload = this.fileUpload.nativeElement;
    fileUpload.click();
    const formData = new FormData();
    fileUpload.onchange = () => {
      formData.append("file", fileUpload.files[0], fileUpload.files[0].name);
      formData.append("project_id", String(this.currentProjectId));
      formData.append("overwrite", String(this.overrideDatabase));
      this.sourceDbService.uploadSourceDbFile(formData).subscribe( resp => {
        if (!resp)
          return;
        this.openSnackBar('File uploaded successfully. ' + this.getResult(resp));
        this.getSourceDbs();
        fileUpload.value = null;
      },
      (error) => {
        this.openSnackBar(error);
        fileUpload.value = null;
      })
    };
  }

  getResult(resp: {added: number, skipped: number, updated: number}): string {
    return this.overrideDatabase
    ? `${resp.added} of new records and ${resp.updated} of overwritten`
    : `${resp.added} of new records and ${resp.skipped} of ignored`
  }

  openSnackBar(message:string) {
    this.snackBar.open(message, 'Accept' , {
      duration: 5000,
    });
  }

  private sortLabels(): void {
    this.labels.sort(function (a, b) {
      if (a.name > b.name) {
        return 1;
      }
      if (a.name < b.name) {
        return -1;
      }
      return 0;
    });
  }

  private createLabelsList(): void {
    const list: any[] = [];

    this.labels.forEach((val: Label) => {
      list.push({ value: val.name });
    });

    this.labelsList = list;
  }

  private setFilterPredicate(): any {
    return this.dataSource.filterPredicate = (
      data: any,
      filterValue: string
    ) => {
      if (filterValue) {
        let value = filterValue.trim();
        let arrLabels = value.split(',');
        if (arrLabels.includes('no_label')) {
          if (data.labels.length < 1) {
            return true;
          }
        }

        if (arrLabels && data?.labels.length) {
          return arrLabels.every(element => data.labels.filter((label: Label) => label.name === element).length > 0)
        }

        return false;
      } else {
        return true;
      }
    }
  }

  private removeItemOnce(arr: string[], value: string):string[] {
    var index = arr.indexOf(value);
    if (index > -1) {
      arr.splice(index, 1);
    }
    return arr;
  }

  private initTableData(data: Array<SourceDb>) {
    const deploymentData: Array<SourceDb> = [];

    data.forEach((item) => {
      const data: SourceDb = Object.create(item);

      data.server = item.server;
      data.db_name = item.db_name;
      data.oracle_version = item.oracle_version;
      data.db_type = getDBType(item.db_type);
      data.id = item.id;
      data.labels = item.labels;

      deploymentData.push(data);
    });

    this.initDataSource(deploymentData);
  }
}
