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

import { Component, OnInit, ViewChild, ElementRef, Output, EventEmitter, OnDestroy } from '@angular/core';
import { FormGroup, FormArray, FormControl, FormBuilder, Validators, AbstractControl } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';

import { MatSnackBar } from '@angular/material/snack-bar';

import { DataTransferRestoreInfo, UploadFileResp, UploadSourceDbFileResp, Validations } from '@app-interfaces/data-transfer';

import { DataTransferService } from '@app-services/data-transfer/data-transfer.service';

import { restoreTypes } from '@app-modules/data-transfer-config-editor/common/restoreTypes';


@Component({
  selector: 'app-data-transfer-restore-parameters',
  templateUrl: './data-transfer-restore-parameters.component.html',
  styleUrls: ['./data-transfer-restore-parameters.component.scss']
})

export class DataTransferRestoreParametersComponent implements OnInit, OnDestroy {
  @ViewChild('configFileUpload', { static: false }) configFileUpload!: ElementRef;
  @ViewChild('passwordFileAdd', { static: false }) passwordFileAdd!: ElementRef;
  @ViewChild('tsnamesFileAdd', { static: false }) tsnamesFileAdd!: ElementRef;
  @ViewChild('listenerFileAdd', { static: false }) listenerFileAdd!: ElementRef;
  @Output() backupPreparationPageChanged = new EventEmitter<boolean>();
  private dataTransferSubscription!: Subscription;
  private runPreRestoreSubscription!: Subscription;
  public restoreForm!: FormGroup;
  public restoreTypes = restoreTypes;
  isUploadConfigFile = false;
  showEditConfigFile = false;
  isClickUpload = false;
  db_id!: number;
  db_name!: string;
  configFileUrl!: string;
  validationDescriptions: any[] = [];
  labelForSubmitButton = 'Submit';
  isRMANDefault = false;

  constructor(
    private dataTransferService: DataTransferService,
    private activatedRoute: ActivatedRoute,
    private snackBar: MatSnackBar,
    private formBuilder: FormBuilder,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.restoreForm = new FormGroup({
      backup_type: new FormControl('', [Validators.required]),
      backup_location: new FormControl('', [Validators.required, this.linkValidation]),
      run_pre_restore: new FormControl(false, []),
      validations: this.formBuilder.array([this.createValidations()]),
      control_file: new FormControl('', [Validators.required, this.controlFileValidation]),
      is_configured: new FormControl(false),
      listener_file: new FormControl(''),
      rman_cmd: new FormControl('', [Validators.required]),
      pfile_content: new FormControl(''),
      pwd_file: new FormControl(''),
      tnsnames_file: new FormControl(''),
      uploadConfigFile: new FormControl('', [Validators.required])
    });

    this.activatedRoute.queryParams.subscribe((params) => {
      this.db_id = params.databaseId;
      this.dataTransferSubscription = this.dataTransferService.getRestoreSettings(params.databaseId).subscribe((resp) => {
        this.db_name = resp.db_name;
        this.validateRequiredFilesFields(resp);
        this.fillForm(resp);
        if(resp.rman_cmd?.length) {
          this.isRMANDefault = false;
        }
      },
      (error) => {
        this.openSnackBar(error);
      });
    });

    this.runPreRestoreSubscription = this.restoreForm.get('run_pre_restore')?.valueChanges.subscribe((val: boolean) => {
      this.labelForSubmitButton = val ? 'Submit and Run Pre-Restore' : 'Submit';

      if (!val) {
        this.restoreForm.get('validations')?.value.forEach((element: any, i: number) => {
          if (element.enabled) {
            this.validations?.controls[i]?.get('enabled')?.setValue(false);
          }
        });
      }
    }) as Subscription;
  }

  ngOnDestroy(): void {
    this.dataTransferSubscription.unsubscribe();
    this.runPreRestoreSubscription.unsubscribe();
  }

  get passwordFileValue(): string|null {
    return this.restoreForm.get('pwd_file')?.value;
  }

  get tsnamesFileValue() : string|null {
    return this.restoreForm.get('tnsnames_file')?.value;
  }

  get listenerFileValue() : string|null {
    return this.restoreForm.get('listener_file')?.value;
  }

  get runPreRestore(): boolean {
    return this.restoreForm.get('run_pre_restore')?.value;
  }

  get validations(): FormArray {
    return this.restoreForm.get('validations') as FormArray;
  }

  uploadConfigFile(): void {
    const uploadFile = this.configFileUpload.nativeElement;
    uploadFile.click();

    const formData = new FormData();
    uploadFile.onchange = () => {
      formData.append("file", uploadFile.files[0], uploadFile.files[0]?.name);
      this.dataTransferService.uploadSourceDbFile(formData, this.db_id).subscribe((resp: UploadSourceDbFileResp) => {
        if (!resp)
          return;

        this.openSnackBar('File uploaded successfully. ');
        this.isUploadConfigFile = true;
        uploadFile.value = null;
        this.configFileUrl = resp.url;
        this.restoreForm.get('uploadConfigFile')?.setValue(resp.content && resp.content);
        this.restoreForm.get('pfile_content')?.setValue(resp.content && resp.content);
        this.isClickUpload = true;
      },
      (error) => {
        this.openSnackBar(error);
        uploadFile.value = null;
        this.isClickUpload = true;
      });
    };
  }

  deleteConfigFile(): void {
    this.dataTransferService.deleteSourceDbFile(this.db_id).subscribe(() => {
      this.restoreForm.get('uploadConfigFile')?.setValue('');
      this.configFileUrl = '';
      this.isUploadConfigFile = false;
      this.showEditConfigFile = false;
    });
  }

  addPasswordFile(): void {
    const addFile = this.passwordFileAdd.nativeElement;
    addFile.click();

    const formData = new FormData();
    addFile.onchange = () => {
      formData.append("file", addFile.files[0], addFile.files[0]?.name);
      this.dataTransferService.uploadPasswordFile(formData, this.db_id).subscribe((resp: UploadFileResp) => {
        if (!resp)
          return;

        this.openSnackBar('File uploaded successfully. ');
        addFile.value = null;
        this.restoreForm.get('pwd_file')?.setValue(resp.url);
      },
      (error) => {
        this.openSnackBar(error);
        addFile.value = null;
      });
    };
  }

  deletePasswordFile(): void {
    this.dataTransferService.deletePasswordFile(this.db_id).subscribe(() => {
      this.restoreForm.get('pwd_file')?.setValue('');
    });
  }

  addTsnamesFile(): void {
    const addFile = this.tsnamesFileAdd.nativeElement;
    addFile.click();

    const formData = new FormData();
    addFile.onchange = () => {
      formData.append("file", addFile.files[0], addFile.files[0]?.name);
      this.dataTransferService.uploadTsnamesFile(formData, this.db_id).subscribe((resp: UploadFileResp) => {
        if (!resp)
          return;

        this.openSnackBar('File uploaded successfully. ');
        addFile.value = null;
        this.restoreForm.get('tnsnames_file')?.setValue(resp.url);
      },
      (error) => {
        this.openSnackBar(error);
        addFile.value = null;
      });
    };
  }

  deleteTsnamesFile(): void {
    this.dataTransferService.deleteTsnamesFile(this.db_id).subscribe(() => {
      this.restoreForm.get('tnsnames_file')?.setValue('');
    });
  }

  addListenerFile(): void {
    const addFile = this.listenerFileAdd.nativeElement;
    addFile.click();

    const formData = new FormData();
    addFile.onchange = () => {
      formData.append("file", addFile.files[0], addFile.files[0]?.name);
      this.dataTransferService.uploadListenerFile(formData, this.db_id).subscribe((resp: UploadFileResp) => {
        if (!resp)
          return;

        this.openSnackBar('File uploaded successfully. ');
        addFile.value = null;
        this.restoreForm.get('listener_file')?.setValue(resp.url);
      },
      (error) => {
        this.openSnackBar(error);
        addFile.value = null;
      });
    };
  }

  deleteListenerFile(): void {
    this.dataTransferService.deleteListenerFile(this.db_id).subscribe(() => {
      this.restoreForm.get('listener_file')?.setValue('');
    });
  }

  saveDraft(): void {
    const validations: any[] = [];

    this.restoreForm.get('validations')?.value.forEach((element: any) => {
      if (element.enabled) {
        validations.push(element.name);
      }
    });
    this.restoreForm.get('pfile_content')?.setValue(this.restoreForm.get('uploadConfigFile')?.value || '');
    this.restoreForm.get('is_configured')?.setValue(false);
    const newRestoreForm = this.createNewRestoreForm();

    newRestoreForm.value.validations = validations;
    this.dataTransferService.createRestoreSettings(this.db_id, newRestoreForm.value).subscribe(() => {
      this.openSnackBar('Restore parameters are saved as draft');
    },
    (error) => {
      this.openSnackBar(error);
    });
  }

  onSubmit(): void {
    let validations: any[] = [];

    this.restoreForm.get('validations')?.value.forEach((element: any) => {
      if (element.enabled) {
        validations.push(element.name);
      }
    });
    this.restoreForm.get('pfile_content')?.setValue(this.restoreForm.get('uploadConfigFile')?.value || '');
    this.restoreForm.get('control_file')?.updateValueAndValidity();

    if (!this.restoreForm.valid) {
      return;
    }

    if (this.restoreForm.get('run_pre_restore')?.value) {
      this.dataTransferService.startPreRestore(this.db_id).subscribe(
        () => {
          this.router.navigate(['/datatransfermanager']);
        },
        (error) => {
          this.openSnackBar(error);
        }
      );
    }

    this.restoreForm.get('is_configured')?.setValue(true);
    const newRestoreForm = this.createNewRestoreForm();

    newRestoreForm.value.validations = validations;
    this.dataTransferService.createRestoreSettings(this.db_id, newRestoreForm.value).subscribe(() => {
      this.openSnackBar('Restore parameters are saved successfully');
    },
    (error) => {
      this.openSnackBar(error);
    });
  }

  readBackupInstruction(): void {
    this.backupPreparationPageChanged.emit(false);
  }

  private createValidations(enabled = false, name: string = ''): FormGroup {
    return this.formBuilder.group({
      enabled: new FormControl(enabled, []),
      name: new FormControl(name, []),
    });
  }

  setRMANScriptTemplate() {
    this.isRMANDefault = true;
    if(this.restoreForm.get('backup_type')?.value === 'full') {
      this.restoreForm.get('rman_cmd')?.setValue(this.getRMANfull());
    } else {
      this.restoreForm.get('rman_cmd')?.setValue(this.getRMANIncArc());
    }
  }

  updateRMANScriptTemplate() {
    if(this.isRMANDefault && this.restoreForm.get('backup_type')?.value !== 'full') {
      this.restoreForm.get('rman_cmd')?.setValue(this.getRMANIncArc());
    }
  }

  updateRMANScript() {
    this.isRMANDefault = false;
  }

  private getRMANfull(): string {
    return `set echo on;
duplicate database for standby nofilenamecheck dorecover backup location '/mnt/gcs';`
  }

  private getRMANIncArc(): string {
    return `set echo on;
{% if db_state.stdout != "NOMOUNT" %}
shutdown immediate;
startup nomount;
{% endif %}
restore standby controlfile from '/mnt/gcs/${this.restoreForm.get('control_file')?.value}';
alter database mount;
catalog start with '+DATA' noprompt;
switch database to copy;
shutdown immediate;
startup mount;
catalog start with '/mnt/gcs' noprompt;
crosscheck backup;
delete noprompt expired backup;
recover database;`
  }

  private openSnackBar(message: string): void {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }

  private linkValidation(control: AbstractControl): {[key: string]: boolean} | null {
    if (!control.value) {
      return null;
    }

    const NO_WHITESPACE_REGEX = /^[^\s]+$/;
    const LINK_REGEX = /.+\/.+/;

    if (control.value.match(NO_WHITESPACE_REGEX) && control.value.match(LINK_REGEX)) {
      return null;
    } else {
      return { invalidFormat: true };
    }
  }

  private controlFileValidation(control: AbstractControl): {[key: string]: boolean} | null {
    if (!control.value) {
      return null;
    }

    const SPACE_SLASH_REGEX = /[\s\/]/;
    if (control.value.match(SPACE_SLASH_REGEX)) {
      return { invalidFormat: true };
    }

    const isDotPresent = control.value.indexOf('.');
    if (isDotPresent === -1) {
      return null;
    }
    
    const EXTENSION_REGEX = /^\S+\.{1}[A-Za-z]+$/;
    if (control.value.match(EXTENSION_REGEX)) {
      return null;
    } else {
      return { invalidFormat: true };
    }
  }

  private validateRequiredFilesFields(resp: DataTransferRestoreInfo): void {
    if (Object.keys(resp).includes('pfile_file') && !resp.pfile_file) { // helper for show/hide error message
      this.isClickUpload = true;
    }
  }

  private fillForm(resp: DataTransferRestoreInfo): void {
    this.configFileUrl = resp.pfile_file;

    this.restoreForm.patchValue(resp);
    if (resp.pfile_content) {
      this.restoreForm.get('uploadConfigFile')?.setValue(resp.pfile_content);
      this.isUploadConfigFile = true;
    }

    if (resp.validations) {
      this.validations.removeAt(0);
      resp.validations.forEach((val: Validations) => {
        this.validationDescriptions.push({ description: val.description, name: val.name });
        this.validations.push(this.createValidations(val.enabled, val.name));
      });
    }
  }

  private createNewRestoreForm(): FormGroup {
    const newRestoreForm = this.restoreForm;

    delete newRestoreForm.value.uploadConfigFile;
    delete newRestoreForm.value.pwd_file;
    delete newRestoreForm.value.tnsnames_file;
    delete newRestoreForm.value.listener_file;

    return newRestoreForm;
  }
}
