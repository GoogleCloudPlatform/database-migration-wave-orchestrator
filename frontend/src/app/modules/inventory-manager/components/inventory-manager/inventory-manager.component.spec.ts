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

import { ComponentFixture, fakeAsync, flush, TestBed, waitForAsync } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { BrowserModule, By } from '@angular/platform-browser';
import { RouterTestingModule } from '@angular/router/testing';
import { FormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatRippleModule } from '@angular/material/core';
import { of, throwError } from 'rxjs';

import { InventoryManagerComponent } from './inventory-manager.component';

import { TargetsService } from '@app-services/targets/targets.service';
import { MockTargetsService } from '@app-services/targets/mock-targets.service.spec';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';

describe('InventoryManagerComponent', () => {
    let component: InventoryManagerComponent;
    let fixture: ComponentFixture<InventoryManagerComponent>;
    let service: TargetsService;
    const mockTargetsService: TargetsService = new MockTargetsService() as TargetsService;
    const mockUtilService: UtilService = new MockUtilService() as UtilService;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
            declarations: [InventoryManagerComponent],
            imports: [CommonModule, BrowserModule, BrowserAnimationsModule, FormsModule, MatTableModule,
                RouterTestingModule, MatSnackBarModule, MatSortModule, MatRippleModule],
            providers: [
                { provide: TargetsService, useValue: mockTargetsService },
                { provide: UtilService, useValue: mockUtilService }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(InventoryManagerComponent);
        component = fixture.componentInstance;
        service = TestBed.inject(TargetsService);

        component.ngOnInit();
    }));

    function whenUiIsStabilized() {
        fixture.detectChanges();
        flush();
    }

    function setSorting() {
        component.dataSource.sort = component.sort;
        fixture.detectChanges();
    }

    it('should show target hostname in the table', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[0].textContent).toEqual('test-bms');
    }));

    it('ngOnInit', () => {
      spyOn(component, 'getTargets');

      component.ngOnInit();

      expect(component.getTargets).toHaveBeenCalled();
      expect(component.patternForSecretName).toEqual('projects/583108012640/secrets/([a-z0-9-_]{1,50})');
    });

    it('should unsubscribe', () => {
      spyOn(component['metadataSettingsSubscription'], 'unsubscribe');

      component.ngOnDestroy();

      expect(component['metadataSettingsSubscription'].unsubscribe).toHaveBeenCalled();
    });

    it('should show CPU Cores in the table', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[1].textContent).toEqual('4');
    }));

    it('should show sockets in the table', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[2].textContent).toEqual('test socket');
    }));

    it('should show RAM in the table', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[3].textContent).toEqual('16');
    }));

    it('should show IP Address in the table', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[4].textContent).toEqual('10.132.0.55');
    }));

    it('should show location in the table', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[5].textContent).toEqual('europe-west-3');
    }));

    it('should show secret name in the input of the table', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        const secretInputValue = row1.cells[6].querySelector('input').value;
        expect(secretInputValue).toEqual('projects/583108012640/secrets/gce-target-test-01');
    }));

    it('should show error for secret name in the input of the table', fakeAsync(() => {
      whenUiIsStabilized();
      setSorting();
      const el = fixture.debugElement.query(By.css('#sname'));

      el.nativeElement.value = 'projec.ts/583108012640/secrets/gce-target-test-02';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      fixture.whenStable().then(()=> {
        const error = fixture.debugElement.query(By.css('#sname-error'));

        expect(error.nativeElement.innerText).toEqual('Should be projects/project_number/secrets/secret_name');
      });
    }));

    it('should start discovery after clicking the "Discovery" button', fakeAsync(() => {
        whenUiIsStabilized();
        spyOn(component, 'startDiscovery');

        const discoveryBtn = fixture.debugElement.query(By.css('button')).nativeElement;
        discoveryBtn.click();
        fixture.detectChanges();

        expect(component.startDiscovery).toHaveBeenCalledTimes(1);
    }));

    it('should show the snackbar if the discovery was successful and renew the list of the targets', fakeAsync(() => {
        whenUiIsStabilized();
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getTargets');

        const discoveryBtn = fixture.debugElement.query(By.css('button')).nativeElement;
        discoveryBtn.click();
        fixture.detectChanges();

        expect(component.openSnackBar).toHaveBeenCalledTimes(1);
        expect(component.getTargets).toHaveBeenCalledTimes(1);
    }));

    it('should show the snackbar if the discovery completed with error', fakeAsync(() => {
        whenUiIsStabilized();
        spyOn(service, 'startTargetsDiscovery').and.returnValue(throwError({ status: 500 }))
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getTargets');

        const discoveryBtn = fixture.debugElement.query(By.css('button')).nativeElement;
        discoveryBtn.click();
        fixture.detectChanges();

        expect(component.openSnackBar).toHaveBeenCalledTimes(1);
        expect(component.getTargets).toHaveBeenCalledTimes(0);
    }));

    it('should show the snackbar if the file upload completed with success', fakeAsync(() => {
        whenUiIsStabilized();
        spyOn(service, 'uploadTargetFile').and.returnValue(of({}));
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getTargets');

        const dataBtn = fixture.debugElement.query(By.css('.upload-file')).nativeElement;
        dataBtn.click();
        fixture.detectChanges();

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(new File([''], 'targets.json'));

        const inputDebugEl = fixture.debugElement.query(By.css('input[type=file]'));
        inputDebugEl.nativeElement.files = dataTransfer.files;

        inputDebugEl.nativeElement.dispatchEvent(new InputEvent('change'));
        fixture.detectChanges();

        expect(service.uploadTargetFile).toHaveBeenCalledTimes(1);
        expect(component.openSnackBar).toHaveBeenCalledTimes(1);
        expect(component.getTargets).toHaveBeenCalledTimes(1);
    }));


    it('should show the snackbar if the file upload completed with error', fakeAsync(() => {
        whenUiIsStabilized();
        spyOn(service, 'uploadTargetFile').and.returnValue(throwError({ status: 500 }));
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getTargets');

        const dataBtn = fixture.debugElement.query(By.css('.upload-file')).nativeElement;
        dataBtn.click();
        fixture.detectChanges();

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(new File([''], 'targets.json'));

        const inputDebugEl = fixture.debugElement.query(By.css('input[type=file]'));
        inputDebugEl.nativeElement.files = dataTransfer.files;

        inputDebugEl.nativeElement.dispatchEvent(new InputEvent('change'));
        fixture.detectChanges();

        expect(service.uploadTargetFile).toHaveBeenCalledTimes(1);
        expect(component.openSnackBar).toHaveBeenCalledTimes(1);
        expect(component.getTargets).toHaveBeenCalledTimes(0);
    }));

    it('should sort table by default according to the created data, starting with the latest', fakeAsync(() => {
        whenUiIsStabilized();
        setSorting();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        const row2 = tableRows[2];

        expect(row1.cells[0].textContent).toEqual('test-bms');
        expect(row2.cells[0].textContent).toEqual('test-bms-2');
    }));

    describe('getTargets', () => {
      beforeEach(() => {
        spyOn<any>(component, 'getTargetsProjects');
        spyOn<any>(component, 'getAllTargetsProjects');

        component.showAvailableProjects = true;
      });

      it('getTargets, should call getTargetsProjects', () => {
        component.getTargets();

        expect(component['getTargetsProjects']).toHaveBeenCalledTimes(1);
        expect(component['getAllTargetsProjects']).not.toHaveBeenCalled();
      });

      it('getTargets, should call getAllTargetsProjects', () => {
        component.showAvailableProjects = false;

        component.getTargets();

        expect(component['getTargetsProjects']).not.toHaveBeenCalled();
        expect(component['getAllTargetsProjects']).toHaveBeenCalledTimes(1);
      });
    });
});

