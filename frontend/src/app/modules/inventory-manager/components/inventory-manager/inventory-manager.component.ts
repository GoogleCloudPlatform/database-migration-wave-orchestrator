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

import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { MatSnackBar } from "@angular/material/snack-bar";
import { Sort } from "@angular/material/sort";
import { Subscription } from "rxjs";

import { Target } from "@app-interfaces/targets";
import { MetadataSettings } from "@app-interfaces/metadata-settings";

import { NotificationService } from "@app-services/notification/notification.service";
import { TargetsService } from "@app-services/targets/targets.service";
import { UtilService } from '@app-services/util/util.service';

import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";

@Component({
  selector: 'app-inventory-manager',
  templateUrl: './inventory-manager.component.html',
  styleUrls: ['./inventory-manager.component.scss']
})
export class InventoryManagerComponent extends BaseMaterialTableComponent<Target> implements OnInit, OnDestroy {
  public displayedColumns = ['name', 'cpu', 'socket', 'ram', 'client_ip', 'location', 'secret_name'];
  ELEMENT_DATA: Target[] | undefined;
  showDataTable: boolean = false;
  showAvailableProjects = true;
  overrideTargets: boolean = false;
  patternForSecretName = '';
  // @ts-ignore
  @ViewChild("fileUpload", { static: false }) fileUpload: ElementRef;
  files = [];
  sortState: Sort = { active: 'created_at', direction: 'desc' };
  metadataSettingsSubscription!: Subscription;

  constructor(
    private targetService: TargetsService,
    private notificationService: NotificationService,
    private snackBar: MatSnackBar,
    private utilService: UtilService,
  ) {
    super();
  }

  ngOnInit(): void {
    this.getTargets();
    this.metadataSettingsSubscription = this.utilService.getMetadataSettings().subscribe((metadataSettings: MetadataSettings) => {
      this.patternForSecretName = `projects/${metadataSettings.project_number}/secrets/([a-z0-9-_]{1,50})`;
    });
  }

  ngOnDestroy() {
    this.metadataSettingsSubscription.unsubscribe();
  }

  getTargets(): void {
    if (this.showAvailableProjects) {
      this.getTargetsProjects();
    } else {
      this.getAllTargetsProjects();
    }
  }

  updateSecretName(row: any, inValid: boolean) {
    const updateData = { 'secret_name': row.secret_name };
    if (!row.id || inValid)
      return;
    this.targetService.updateTargetsProject(row.id, updateData).subscribe(resp => {
      resp ? this.openSnackBar(this.notificationService.GENERAL_SUCCESS_MESSAGE) : null;
      this.openSnackBar('Secret name for project ' + row.name + ' updated successfully');
      this.getTargets();
    })
  }

  openSnackBar(message: string) {
    this.snackBar.open(message, 'Accept', {
      duration: 5000,
    });
  }

  uploadFile() {
    const fileUpload = this.fileUpload.nativeElement;
    fileUpload.click();
    const formData = new FormData();
    fileUpload.onchange = () => {
      formData.append("file", fileUpload.files[0], fileUpload.files[0].name);
      formData.append("overwrite", String(this.overrideTargets));
      this.targetService.uploadTargetFile(formData).subscribe(resp => {
        if (!resp)
          return;
        this.openSnackBar('File uploaded successfully');
        this.getTargets();
        fileUpload.value = null;
      },
      (error) => {
        this.openSnackBar(error);
        fileUpload.value = null;
      })
    };
  }

  startDiscovery() {
    this.targetService.startTargetsDiscovery().subscribe((resp) => {
      if (!resp) {
        return;
      }
      this.openSnackBar('The discovery was successful');
      this.getTargets();
    },
      (error) => {
        this.openSnackBar(error);
      })
  };

  private getTargetsProjects(): void {
    if (this.utilService.getCurrentProjectId() != null) {
      const currentIdNumber = this.utilService.getCurrentProjectId();

      this.targetService.getTargetsProjects(currentIdNumber).subscribe(res => {
        this.ELEMENT_DATA = res.data;

        this.showDataTable = !!this.ELEMENT_DATA?.length;

        this.initDataSource(this.ELEMENT_DATA);
      });
    }
  }

  private getAllTargetsProjects(): void {
    this.targetService.getAllTargetsProjects().subscribe(res => {
      this.ELEMENT_DATA = res.data;

      if (this.ELEMENT_DATA?.length) {
        this.showDataTable = true;
      }

      this.initDataSource(this.ELEMENT_DATA);
    });
  }
}
