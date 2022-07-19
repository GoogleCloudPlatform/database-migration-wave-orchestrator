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

import { Component, OnInit, ElementRef } from '@angular/core';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { FormControl, FormGroup, ValidationErrors, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';

import { UtilService } from '@app-services/util/util.service';
import { MigrationService } from '@app-services/migration/migration.service';
import { NotificationService } from '@app-services/notification/notification.service';

import { Migration } from '@app-interfaces/migration';
import { DialogData } from '@app-interfaces/dialog-data';
import { Metadata } from "@app-interfaces/metadata";

import { ConfirmDialogComponent } from '@app-shared/components/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-create-migration',
  templateUrl: './create-migration.component.html',
  styleUrls: ['./create-migration.component.scss']
})

export class CreateMigrationComponent implements OnInit {
  value = '';
  public href: string = '';
  migrationForm: FormGroup = new FormGroup({
    id:               new FormControl('' ),
    name:             new FormControl('' , [Validators.required, Validators.maxLength(30)]),
    description:      new FormControl('',  [Validators.maxLength(256)]),
    vpc:              new FormControl('' , [Validators.required, Validators.maxLength(128)]),
    subnet:           new FormControl('' , [Validators.required, Validators.maxLength(128)]),
  });
  isEditing: boolean = false;
  isViewing: boolean = false;
  currentId: number | undefined;
  formHasErrors: boolean = false;
  metaData: Metadata =  {
    networks: [{ subnetwork: [''], network: '' }],
  };
  chosenNetwork: number = 0;
  filteredNetworks!: Observable<string[]>;
  filteredSubNetworks!: Observable<string[]>;
  filteredServiceAccounts!:  Observable<string[]>;

  constructor(
    private util:UtilService,
    private router: Router,
    private location: Location,
    private activatedRoute: ActivatedRoute,
    private notificationService: NotificationService,
    private migrationService: MigrationService,
    public dialog: MatDialog,
    private snackBar: MatSnackBar,
    private element: ElementRef
  ) {
    this.router.events.subscribe( () => {
      this.isEditing = this.location.path().split('/')[2] === 'edit';
      this.isViewing = this.location.path().split('/')[2] === 'view';
    })
    this.activatedRoute.params.subscribe( () => {
      this.getEditingProject()
    })
  }

  setMetaData(){
      this.migrationService.getMetaData().subscribe( (element: Metadata) => {
        this.metaData = element;
        this.filteredNetworks = this.migrationForm.controls.vpc.valueChanges.pipe(
          startWith(''),
          map(value => {return this.getNetworks(value)}),
        );
      })
  }

  ngOnInit(): void {
    this.getEditingProject();
    this.setMetaData();
  }

  private getNetworks(value: string): string[] {
    return this.metaData.networks?.filter(option => option.network.toLowerCase().includes(value.toLowerCase()))
      .map(network => network.network);
  }

  private getSubNetworks(value: string, index: number): string[] {
    return this.metaData.networks[index].subnetwork
    .filter(option => option.toLowerCase().includes(value.toLowerCase()))
  }

  getSubnet() {
    this.metaData.networks.map((element, index) => {
      if (element.network === this.migrationForm.controls.vpc.value) this.chosenNetwork = index;
    })
    this.filteredSubNetworks = this.migrationForm.controls.subnet.valueChanges.pipe(
      startWith(''),
      map(value => this.getSubNetworks(value, this.chosenNetwork)),
    );
  }

  getEditingProject(){
    if (this.isEditing || this.isViewing) {
      this.currentId = Number(this.activatedRoute.snapshot.paramMap.get('id'));
      this.migrationService.getMigrationProject(this.currentId).subscribe( (project: Migration) => {
        this.migrationForm.setValue(project);
      })

    }

    if(this.isViewing) {
      this.migrationForm.disable();
    }
  }

  editForm() {
    this.router.navigateByUrl(`/mymigrationprojects/edit/${this.currentId}`);
  }

  goBack(){
    this.util.goBack()
  }

  getFormValidationErrors() {
    let errors = 0;
    Object.keys(this.migrationForm.controls).forEach(key => {
      // @ts-ignore
      const controlErrors: ValidationErrors = this.migrationForm.get(key).errors;
      if (controlErrors != null) {
        errors++;
      }
    });
    return errors > 0;
  }

  onSubmit() {
    this.formHasErrors = this.getFormValidationErrors();
    if (this.formHasErrors) return;
    delete this.migrationForm.value.id;
    if (this.isEditing) {
      if (!this.currentId) return;
      this.migrationService.updateMigrationProject(this.currentId , this.migrationForm.value)
      .subscribe(
        (resp:Migration) => {
          this.migrationForm.setValue(resp);
          this.openSnackBar(this.notificationService.GENERAL_SUCCESS_MESSAGE);
          this.migrationService.getAndStoreMigrationsProjects();
          this.router.navigateByUrl(`/mymigrationprojects/view/${this.currentId}`);
        },
        (error) => {
          this.openSnackBar(error);
        }
      )
    } else {
      this.migrationService.createMigrationProject(this.migrationForm.value)
      .subscribe(
        (resp: Migration) => {
          this.openSnackBar(this.notificationService.GENERAL_SUCCESS_MESSAGE);
          localStorage.setItem('currentProjectId' , String(resp.id));
          window.dispatchEvent( new Event('storage'));
          this.migrationService.getAndStoreMigrationsProjects();
          this.router.navigateByUrl(`/softwarelibrary`);
        },
        (error) => {
          this.openSnackBar(error);
        }
      )
    }
  }

  openSnackBar(message:string) {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }

  showConfirmationDialog(): MatDialogRef<ConfirmDialogComponent>{
    return this.dialog.open(ConfirmDialogComponent, {
      width: '250px',
      data: <DialogData>{
        message: 'the project '+this.migrationForm.value.name+'  will be deleted',
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Accept',
        cancelBtnText: 'Cancel',
        headerText: 'Confirm',
        panelClass: 'custom-dialog'
      },
    })
  }

  deleteProject() {
    this.showConfirmationDialog().afterClosed().subscribe(result => {
      if (!result)  return;

      this.migrationService.deleteMigrationProjectPromise(this.currentId)
        .then(() => {
          this.openSnackBar('Project has been deleted successfully');
          this.router.navigateByUrl(`/mymigrationprojects/list`);
        })
        .catch((error) => {
          this.openSnackBar(`Error. ${error.error.errors || 'Unexpected error'}`);
        })
    });
  }

  focusErrorField() {
   for (const key of Object.keys(this.migrationForm.controls)) {
    if (this.migrationForm.controls[key].invalid) {
      const invalidControl = this.element.nativeElement.querySelector('[formcontrolname="' + key + '"]');
      invalidControl.focus();
      break;
    }
   }
  }
}
