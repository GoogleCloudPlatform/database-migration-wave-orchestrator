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
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTableModule } from '@angular/material/table';
import { of, throwError } from 'rxjs';

import { MatRippleModule } from '@angular/material/core';

import { SourceDatabasesComponent } from './source-databases.component';

import { SourceDbService } from '@app-services/source-db/source-db.service';
import { MockSourceDbService } from '@app-services/source-db/mock-source-db.service';
import { LabelService } from '@app-services/label/label.service';
import { MockLabelService } from '@app-services/label/mock-label.service.spec';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';


describe('SourceDatabasesComponent', () => {
    let component: SourceDatabasesComponent;
    let fixture: ComponentFixture<SourceDatabasesComponent>;
    let service: SourceDbService;
    let localStore: any;
    const mockSourceDbService: SourceDbService = new MockSourceDbService() as SourceDbService;
    const mockLabelService: LabelService = new MockLabelService() as LabelService;
    const mockUtilService: UtilService = new MockUtilService() as UtilService;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
            declarations: [SourceDatabasesComponent],
            imports: [CommonModule, BrowserModule, FormsModule, MatTableModule, RouterTestingModule, MatSnackBarModule, MatRippleModule],
            providers: [
                { provide: SourceDbService, useValue: mockSourceDbService },
                { provide: LabelService, useValue: mockLabelService },
                { provide: UtilService, useValue: mockUtilService }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(SourceDatabasesComponent);
        component = fixture.componentInstance;
        service = TestBed.inject(SourceDbService);

        localStore = {};

        spyOn(window.localStorage, 'getItem').and.callFake((key) =>
          key in localStore ? localStore[key] : null
        );
        spyOn(window.localStorage, 'setItem').and.callFake(
          (key, value) => (localStore[key] = value + '')
        );
        spyOn(window.localStorage, 'removeItem').and.callFake(
          (key) => (localStore[key] = '')
        );
        component.ngOnInit();
    }));

    function whenUiIsStabilized() {
        fixture.detectChanges();
        flush();
    }

    it('setFilterPredicate, should return true for label1111', () => {
      const filterfx = component['setFilterPredicate']();

      expect(filterfx({ labels: [{id: 11, name: 'label1111'}]}, 'label1111')).toEqual(true);
    });

    it('setFilterPredicate, should return true for label1111, label21', () => {
      const filterfx = component['setFilterPredicate']();

      expect(filterfx({ labels: [{id: 11, name: 'label1111'}, {id: 12, name: 'label21'}]}, 'label1111,label21')).toEqual(true);
    });

    it('should show server name in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[0].textContent).toEqual('serverapp_3891');
    }));

    it('should show database name in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[1].textContent).toEqual('APPDB_3891');
    }));

    it('should show oracle version in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[2].textContent).toEqual('11.2');
    }));

    it('should show type of database in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[3].textContent).toEqual('Real Application Cluster');
    }));

    it('should show the snackbar if the file upload completed with success', fakeAsync(() => {
        whenUiIsStabilized();
        spyOn(service, 'uploadSourceDbFile').and.returnValue(of({}));
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getSourceDbs');

        const dataBtn = fixture.debugElement.query(By.css('button')).nativeElement;
        dataBtn.click();
        fixture.detectChanges();

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(new File([''], 'targets.json'));

        const inputDebugEl = fixture.debugElement.query(By.css('input[type=file]'));
        inputDebugEl.nativeElement.files = dataTransfer.files;

        inputDebugEl.nativeElement.dispatchEvent(new InputEvent('change'));
        fixture.detectChanges();

        expect(service.uploadSourceDbFile).toHaveBeenCalledTimes(1);
        expect(component.openSnackBar).toHaveBeenCalledTimes(1);
        expect(component.getSourceDbs).toHaveBeenCalledTimes(1);
    }));
    it('should show the snackbar with amount of records added and updated for override state', fakeAsync(() => {
        whenUiIsStabilized();
        component.overrideDatabase = true;
        spyOn(service, 'uploadSourceDbFile').and.returnValue(of({added: 1, skipped: 0, updated: 1}));
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getSourceDbs');

        const dataBtn = fixture.debugElement.query(By.css('button')).nativeElement;
        dataBtn.click();
        fixture.detectChanges();

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(new File([''], 'targets.json'));

        const inputDebugEl = fixture.debugElement.query(By.css('input[type=file]'));
        inputDebugEl.nativeElement.files = dataTransfer.files;

        inputDebugEl.nativeElement.dispatchEvent(new InputEvent('change'));
        fixture.detectChanges();
        expect(component.openSnackBar).toHaveBeenCalledWith('File uploaded successfully. 1 of new records and 1 of overwritten');
    }));

    it('should show the snackbar with amount of records added and skipped for non-override state', fakeAsync(() => {
        whenUiIsStabilized();
        component.overrideDatabase = false;
        spyOn(service, 'uploadSourceDbFile').and.returnValue(of({added: 1, skipped: 1, updated: 0}));
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getSourceDbs');

        const dataBtn = fixture.debugElement.query(By.css('button')).nativeElement;
        dataBtn.click();
        fixture.detectChanges();

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(new File([''], 'targets.json'));

        const inputDebugEl = fixture.debugElement.query(By.css('input[type=file]'));
        inputDebugEl.nativeElement.files = dataTransfer.files;

        inputDebugEl.nativeElement.dispatchEvent(new InputEvent('change'));
        fixture.detectChanges();
        expect(component.openSnackBar).toHaveBeenCalledWith('File uploaded successfully. 1 of new records and 1 of ignored');
    }));
    it('should show the snackbar if the file upload completed with error', fakeAsync(() => {
        whenUiIsStabilized();
        spyOn(service, 'uploadSourceDbFile').and.returnValue(throwError({ status: 500 }));
        spyOn(component, 'openSnackBar');
        spyOn(component, 'getSourceDbs');

        const dataBtn = fixture.debugElement.query(By.css('button')).nativeElement;
        dataBtn.click();
        fixture.detectChanges();

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(new File([''], 'targets.json'));

        const inputDebugEl = fixture.debugElement.query(By.css('input[type=file]'));
        inputDebugEl.nativeElement.files = dataTransfer.files;

        inputDebugEl.nativeElement.dispatchEvent(new InputEvent('change'));
        fixture.detectChanges();

        expect(service.uploadSourceDbFile).toHaveBeenCalledTimes(1);
        expect(component.openSnackBar).toHaveBeenCalledTimes(1);
        expect(component.getSourceDbs).toHaveBeenCalledTimes(0);
    }));
    it('should show edit labels link in labels column header',  fakeAsync(() => {
        whenUiIsStabilized();
        const editLabelsLink = fixture.debugElement.query(By.css('.manage-label')).nativeElement;
        expect(editLabelsLink).toBeTruthy();
      }));
    it('should open right panel on edit labels link click',  fakeAsync(() => {
        spyOn(component, 'manageLabels').and.callThrough();
        whenUiIsStabilized();
        const editLabelsLink = fixture.debugElement.query(By.css('.manage-label')).nativeElement;
        editLabelsLink.click();
        expect(component.manageLabels).toHaveBeenCalledTimes(1);
    }));

    it('ngOnInit, should remove item', () => {
      component.ngOnInit();

      expect(window.localStorage.removeItem).toHaveBeenCalledWith('filterState');
    });
});


