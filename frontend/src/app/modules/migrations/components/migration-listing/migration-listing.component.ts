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

import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog, MatDialogRef } from "@angular/material/dialog";
import { Subscription } from "rxjs";

import { Migration } from "@app-interfaces/migration";
import { DialogData } from "@app-interfaces/dialog-data";

import { MigrationService } from "@app-services/migration/migration.service";
import { UtilService } from "@app-services/util/util.service";

import { ConfirmDialogComponent } from "@app-shared/components/confirm-dialog/confirm-dialog.component";
import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";


@Component({
  selector: 'app-migration-listing',
  templateUrl: './migration-listing.component.html',
  styleUrls: ['./migration-listing.component.scss']
})
export class MigrationListingComponent extends BaseMaterialTableComponent<Migration> implements OnInit, OnDestroy {
  private projectListSubscription!: Subscription;
  displayedColumns = ['name', 'description', 'vpc' , 'subnet' , 'actions'];
  currentProjectId: number | undefined;
  searchQuery: string = '';
  isInlineView = true;
  projects: Migration[] = [];

  constructor(
    private readonly utilService: UtilService,
    private readonly router: Router,
    private readonly migrationService: MigrationService,
    private readonly dialog: MatDialog,
    private readonly snackBar: MatSnackBar
  ) {
    super();
    if (this.utilService.getCurrentProjectId() != null) {
      this.currentProjectId = this.utilService.getCurrentProjectId();
    }
  }

  ngOnInit(): void {
    this.projectListSubscription = this.migrationService.projectList().subscribe((projectList: Migration) => {
      if (!projectList.data || !projectList.data.length) {
        this.router.navigateByUrl('/mymigrationprojects');
        return;
      }

      this.getMigrations();
    });
  }

  ngOnDestroy(): void {
    this.projectListSubscription.unsubscribe();
  }

  redirect(option: string) {
    this.router.navigateByUrl(`/${option}`  )
  }

  getMigrations() {
    this.migrationService.getMigrationsProjects().subscribe((resp) => {
      this.projects = resp.data || [];
      this.initDataSource(resp.data || []);
    })
  }

  action(action:string, row: Migration) {
    switch (action) {
      case 'open':
        this.setSelected(row.id);
        this.redirect('/softwarelibrary');
        break;
      case 'view':
        this.redirect('/mymigrationprojects/view/'+row.id)
        break;

      case 'edit':
        this.redirect('/mymigrationprojects/edit/'+row.id)
        break;

      case 'delete':
        this.deleteProject(row.id)
        break;
    }
  }

  deleteProject(id: number | undefined) {
    if (!id)
      return;
    this.showConfirmationDialog('the project will be deleted')?.afterClosed().subscribe(result => {
      if (!result)  return;

      this.migrationService.deleteMigrationProjectPromise(id)
        .then(() => {
          this.openSnackBar('Project has been deleted successfully', 'Close');
          this.getMigrations();
          localStorage.removeItem('currentProjectId');
        })
        .catch((error) => {
          this.openSnackBar(`Error. ${error.error.errors || 'Unexpected error'}`, 'Close');
        })
    });
  }

  showConfirmationDialog(message: string): MatDialogRef<ConfirmDialogComponent>{
    return this.dialog.open(ConfirmDialogComponent, {
      width: '250px',
      data: <DialogData>{
        message: message,
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Accept',
        cancelBtnText: 'Cancel',
        headerText: 'Confirm'
      },
      ariaLabel: 'migration-projects-confirmation-dialog',
      panelClass: 'custom-dialog'
    })
  }

  openSnackBar(message: string, action: string) {
    this.snackBar.open(message, action , {
      duration: 5000
    });
  }

  setSelected(id?:number) {
    if (id) {
      localStorage.setItem('currentProjectId' , String(id));
      window.dispatchEvent( new Event('storage'));
    }
  }
}

