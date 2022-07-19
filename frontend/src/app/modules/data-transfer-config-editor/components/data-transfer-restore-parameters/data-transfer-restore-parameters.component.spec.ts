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

import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { By } from '@angular/platform-browser';
import { of, BehaviorSubject } from 'rxjs';

import { MatRippleModule } from '@angular/material/core';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatInputModule } from '@angular/material/input';

import { DataTransferService } from '@app-services/data-transfer/data-transfer.service';
import { MockDataTransferService } from '@app-services/data-transfer/mock-data-transfer.service.spec';

import { DataTransferRestoreParametersComponent } from './data-transfer-restore-parameters.component';


const activatedRouteMock = {
  queryParams: of({
      databaseId: '123',
  }),
};


describe('DataTransferRestoreParametersComponent', () => {
  let component: DataTransferRestoreParametersComponent;
  let fixture: ComponentFixture<DataTransferRestoreParametersComponent>;
  let dataTransferservice: DataTransferService;
  const mockDataTransferService: DataTransferService = new MockDataTransferService() as DataTransferService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormsModule, ReactiveFormsModule, RouterTestingModule, BrowserAnimationsModule, MatSelectModule,
        MatInputModule, MatSnackBarModule, MatRippleModule],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [DataTransferRestoreParametersComponent],
      providers: [
        { provide: DataTransferService, useValue: mockDataTransferService },
        { provide: ActivatedRoute, useValue: activatedRouteMock },
        { provide: HttpClient, useValue: null}
      ]
    })
    .compileComponents();
    fixture = TestBed.createComponent(DataTransferRestoreParametersComponent);
    component = fixture.componentInstance;
    dataTransferservice = TestBed.inject(DataTransferService);

    fixture.detectChanges();
  });

  afterEach(() => {
    fixture.destroy();
  });

  function fillRestoreForm() {
    const typeFieldSelectRef = fixture.debugElement.query(By.css('.mat-select-trigger')).nativeElement;
    typeFieldSelectRef.click();
    fixture.detectChanges();

    const matOption = fixture.debugElement.query(By.css('.mat-option')).nativeElement;
    matOption.click();
    fixture.detectChanges();

    const backupLocation = fixture.debugElement.query(By.css('#backupLocation'));
    backupLocation.nativeElement.value = 'bucket_folder/bucket_name';
    backupLocation.triggerEventHandler('input', {
      target: backupLocation.nativeElement
    })
    fixture.detectChanges();

    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.nativeElement.value = 'name.txt';
    controlFile.triggerEventHandler('input', {
      target: controlFile.nativeElement
    })
    fixture.detectChanges();

    const rmanScript = fixture.debugElement.query(By.css('#rmanScript'));
    rmanScript.nativeElement.value = 'script';
    rmanScript.triggerEventHandler('input', {
      target: rmanScript.nativeElement
    })
    fixture.detectChanges();

    const uploadConfigFile = fixture.debugElement.query(By.css('#uploadConfigFile'));
    uploadConfigFile.nativeElement.value = 'script';
    uploadConfigFile.triggerEventHandler('input', {
      target: uploadConfigFile.nativeElement
    })
    fixture.detectChanges();
  }

  function addPasswordFile() {
    const addPasswordBtn = fixture.debugElement.query(By.css('.add-password')).nativeElement;
    addPasswordBtn.click();
    fixture.detectChanges();
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(new File([''], 'password.bin'));
    const passwordInput = fixture.debugElement.query(By.css('#passwordFileAdd'));
    passwordInput.nativeElement.files = dataTransfer.files;
    passwordInput.nativeElement.dispatchEvent(new InputEvent('change'));
    fixture.detectChanges();
  }

  function addTsnamesFile() {
    const addTsnamesBtn = fixture.debugElement.query(By.css('.add-tsnames')).nativeElement;
    addTsnamesBtn.click();
    fixture.detectChanges();
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(new File([''], 'password.bin'));
    const passwordInput = fixture.debugElement.query(By.css('#tsnamesFileAdd'));
    passwordInput.nativeElement.files = dataTransfer.files;
    passwordInput.nativeElement.dispatchEvent(new InputEvent('change'));
    fixture.detectChanges();
  }

  function addListenerFile() {
    const addListenerBtn = fixture.debugElement.query(By.css('.add-listener')).nativeElement;
    addListenerBtn.click();
    fixture.detectChanges();
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(new File([''], 'password.bin'));
    const passwordInput = fixture.debugElement.query(By.css('#listenerFileAdd'));
    passwordInput.nativeElement.files = dataTransfer.files;
    passwordInput.nativeElement.dispatchEvent(new InputEvent('change'));
    fixture.detectChanges();
  }

  it('should set db name in the Db_Name title', async () => {
    const dbName = fixture.debugElement.query(By.css('h3')).nativeElement;

    await fixture.whenStable().then(() => {
      expect(dbName.textContent).toEqual('Database name: db_1');
    })
  });

  it('should set values for restore parameters if ther are stored on server', async () => {
    const dataTransferValue = new BehaviorSubject({
      db_name: 'db_1',
      backup_location: 'gcs',
      backup_type: 'archivelogs',
      is_configured: false,
      listener_file: null,
      pfile_content: 'file text content',
      pfile_file: '',
      pwd_file: null,
      rman_cmd: 'run cmd',
      tnsnames_file: null,
      control_file: '',
      run_pre_restore: false,
      validations: [{
        description: '',
        enabled: false,
        name: ''
      }]
    })
    spyOn(dataTransferservice, 'getRestoreSettings').and.returnValue(dataTransferValue);
    component.ngOnInit();
    dataTransferservice.getRestoreSettings(1);
    fixture.detectChanges();

    const restoreType = fixture.debugElement.query(By.css('.mat-select-value-text > span')).nativeElement;
    const backupLocation = fixture.debugElement.query(By.css('#backupLocation')).nativeElement;
    const rmanScript = fixture.debugElement.query(By.css('#rmanScript')).nativeElement;
    const uploadConfigFile = fixture.debugElement.query(By.css('#uploadConfigFile')).nativeElement;

    await fixture.whenStable().then(() => {
      expect(restoreType.textContent).toEqual('Arch Log');
      expect(backupLocation.value).toEqual('gcs');
      expect(rmanScript.value).toEqual('run cmd');
      expect(uploadConfigFile.value).toEqual('file text content');
    })
  });

  it('should set required error for restore type field', async () => {
    const restoreType = fixture.debugElement.query(By.css('#restoreType'));
    restoreType.triggerEventHandler('select', {
      target: restoreType.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('backup_type')?.hasError('required')).toEqual(true);
    })
  });

  it('should set required error for uploadConfigFile type field', async () => {
    const uploadConfigFile = fixture.debugElement.query(By.css('#uploadConfigFile'));
    uploadConfigFile.triggerEventHandler('input', {
      target: uploadConfigFile.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('uploadConfigFile')?.hasError('required')).toEqual(true);
    });
  });

  it('should set empty string to uploadConfigFile', () => {
    component.deleteConfigFile();

    expect(component.restoreForm.get('uploadConfigFile')?.value).toEqual('');
  });

  it('should set required error for backup location field', async () => {
    const backupLocation = fixture.debugElement.query(By.css('#backupLocation'));
    backupLocation.triggerEventHandler('input', {
      target: backupLocation.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('backup_location')?.hasError('required')).toEqual(true);
    })
  });

  it('should set invalidFormat error for backup location field if the format is not correct', async () => {
    const backupLocation = fixture.debugElement.query(By.css('#backupLocation'));
    backupLocation.nativeElement.value = 'bucket folder';
    backupLocation.triggerEventHandler('input', {
      target: backupLocation.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('backup_location')?.hasError('invalidFormat')).toEqual(true);
    })
  });

  it('should not set invalidFormat error for backup location field if the format is correct', async () => {
    const backupLocation = fixture.debugElement.query(By.css('#backupLocation'));
    backupLocation.nativeElement.value = 'bucket_folder/bucket_name';
    backupLocation.triggerEventHandler('input', {
      target: backupLocation.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('backup_location')?.hasError('invalidFormat')).toEqual(false);
    })
  });

  it('should set required error for RMAN script field', async () => {
    const rmanScript = fixture.debugElement.query(By.css('#rmanScript'));
    rmanScript.triggerEventHandler('input', {
      target: rmanScript.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('rman_cmd')?.hasError('required')).toEqual(true);
    })
  });
  
  it('should set RMAN script template when restore type is selected', async () => {
    spyOn(component, 'setRMANScriptTemplate').and.callThrough();
    const restoreType = fixture.debugElement.query(By.css('#restoreType'));
    restoreType.triggerEventHandler('selectionChange',event);
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.setRMANScriptTemplate).toHaveBeenCalledTimes(1);
    })
  });

  it('should undate RMAN script template when control file name is change and script is default', async () => {
    spyOn(component, 'updateRMANScriptTemplate').and.callThrough();
    const restoreType = fixture.debugElement.query(By.css('#restoreType'));
    restoreType.triggerEventHandler('selectionChange',event);
    fixture.detectChanges();
    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.triggerEventHandler('change', event);
    fixture.detectChanges();
    await fixture.whenStable().then(() => {
      expect(component.updateRMANScriptTemplate).toHaveBeenCalledTimes(1);
    })
  });

  it('should not set RMAN script template when RMAN script is not default', async () => {
    spyOn(component, 'updateRMANScriptTemplate').and.callThrough();
    spyOn(component, 'updateRMANScript').and.callThrough();
    const restoreType = fixture.debugElement.query(By.css('#restoreType'));
    restoreType.triggerEventHandler('selectionChange',event);
    fixture.detectChanges();
    const rmanScript = fixture.debugElement.query(By.css('#rmanScript'));
    rmanScript.nativeElement.value = 'another script'
    rmanScript.triggerEventHandler('change', event);
    expect(component.updateRMANScript).toHaveBeenCalledTimes(1);
    fixture.detectChanges();
    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.triggerEventHandler('change', event);
    fixture.detectChanges();
    await fixture.whenStable().then(() => {
      expect(component.updateRMANScriptTemplate).toHaveBeenCalledTimes(1);
      expect(rmanScript.nativeElement.value).toEqual('another script')
    })
  });

  it('should set required error for control file field', async () => {
    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.triggerEventHandler('input', {
      target: controlFile.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('control_file')?.hasError('required')).toEqual(true);
    })
  });

  it('should set invalidFormat error for control file field if there is slash', async () => {
    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.nativeElement.value = 'bucket_folder/bucket_name';
    controlFile.triggerEventHandler('input', {
      target: controlFile.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('control_file')?.hasError('invalidFormat')).toEqual(true);
    })
  });

  it('should set invalidFormat error for control file field if there is space', async () => {
    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.nativeElement.value = 'bucket name';
    controlFile.triggerEventHandler('input', {
      target: controlFile.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('control_file')?.hasError('invalidFormat')).toEqual(true);
    })
  });

  it('should not set invalidFormat error for control file field if there is name presented', async () => {
    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.nativeElement.value = 'bucket_name';
    controlFile.triggerEventHandler('input', {
      target: controlFile.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('control_file')?.hasError('invalidFormat')).toEqual(false);
    })
  });

  it('should not set invalidFormat error for control file field if there is name with extension presented', async () => {
    const controlFile = fixture.debugElement.query(By.css('#controlFile'));
    controlFile.nativeElement.value = 'bucket_name.txt';
    controlFile.triggerEventHandler('input', {
      target: controlFile.nativeElement
    });
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.restoreForm.get('control_file')?.hasError('invalidFormat')).toEqual(false);
    })
  });

  it('should upload password file', async () => {
    spyOn(dataTransferservice, 'uploadPasswordFile').and.callThrough();
    addPasswordFile();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.uploadPasswordFile).toHaveBeenCalledTimes(1);
      expect(component.restoreForm.get('pwd_file')?.value).toEqual('restore-configs/1/pwd_file.ora');
    })
  });

  it('should delete password file on click on the delete icon', async () => {
    spyOn(dataTransferservice, 'deletePasswordFile').and.callThrough();
    addPasswordFile();

    const deletePasswordIcon = fixture.debugElement.query(By.css('[aria-label="delete password file"]')).nativeElement;
    deletePasswordIcon.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.deletePasswordFile).toHaveBeenCalledTimes(1);
      expect(component.restoreForm.get('pwd_file')?.value).toEqual('');
    })
  });

  it('should upload tnsnames.ora file', async () => {
    spyOn(dataTransferservice, 'uploadTsnamesFile').and.callThrough();
    addTsnamesFile();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.uploadTsnamesFile).toHaveBeenCalledTimes(1);
      expect(component.restoreForm.get('tnsnames_file')?.value).toEqual('restore-configs/1/tnsnames_file.ora');
    })
  });

  it('should delete tsnames.ora file on click on the delete icon', async () => {
    spyOn(dataTransferservice, 'deleteTsnamesFile').and.callThrough();
    addTsnamesFile();

    const deleteTsnamesIcon = fixture.debugElement.query(By.css('[aria-label="delete tsnames file"]')).nativeElement;
    deleteTsnamesIcon.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.deleteTsnamesFile).toHaveBeenCalledTimes(1);
      expect(component.restoreForm.get('tnsnames_file')?.value).toEqual('');
    })
  });

  it('should upload listener.ora file', async () => {
    spyOn(dataTransferservice, 'uploadListenerFile').and.callThrough();
    addListenerFile();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.uploadListenerFile).toHaveBeenCalledTimes(1);
      expect(component.restoreForm.get('listener_file')?.value).toEqual('restore-configs/1/listener_file.ora');
    })
  });

  it('should delete listener.ora file on click on the delete icon', async () => {
    spyOn(dataTransferservice, 'deleteListenerFile').and.callThrough();
    addListenerFile();

    const deleteListenerIcon = fixture.debugElement.query(By.css('[aria-label="delete listener file"]')).nativeElement;
    deleteListenerIcon.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.deleteListenerFile).toHaveBeenCalledTimes(1);
      expect(component.restoreForm.get('listener_file')?.value).toEqual('');
    })
  });

  it('should create draft if at least restore type field is selected', async () => {
    spyOn(dataTransferservice, 'createRestoreSettings').and.callThrough();

    const typeFieldSelectRef = fixture.debugElement.query(By.css('.mat-select-trigger')).nativeElement;
    typeFieldSelectRef.click();
    fixture.detectChanges();

    const matOption = fixture.debugElement.query(By.css('.mat-option')).nativeElement;
    matOption.click();
    fixture.detectChanges();

    const saveDraftBtn = fixture.debugElement.query(By.css('.save-draft')).nativeElement;
    saveDraftBtn.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.createRestoreSettings).toHaveBeenCalledTimes(1);
    })
  });

  it('should not create restore parameters if all required fields are not filled', async () => {
    spyOn(dataTransferservice, 'createRestoreSettings');

    const submitBtn = fixture.debugElement.query(By.css('button[type=submit]')).nativeElement;
    submitBtn.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.createRestoreSettings).toHaveBeenCalledTimes(0);
    })
  });

  it('should create restore parameters if all required fields are filled', async () => {
    fillRestoreForm();
    spyOn(dataTransferservice, 'createRestoreSettings').and.callThrough();

    const submitBtn = fixture.debugElement.query(By.css('button[type=submit]')).nativeElement;
    submitBtn.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(dataTransferservice.createRestoreSettings).toHaveBeenCalledTimes(1);
    })
  });

  it('should set is_configured parameter to true if the form is submitted', async () => {
    fillRestoreForm();
    spyOn(dataTransferservice, 'createRestoreSettings').and.callThrough();

    const submitBtn = fixture.debugElement.query(By.css('button[type=submit]')).nativeElement;
    submitBtn.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect((component.restoreForm.get('is_configured')?.value)).toEqual(true);
    })
  });
})
