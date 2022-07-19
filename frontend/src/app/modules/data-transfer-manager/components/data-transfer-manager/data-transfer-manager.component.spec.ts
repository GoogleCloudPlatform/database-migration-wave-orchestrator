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
import { ComponentFixture, TestBed, flush, fakeAsync } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { MatTableModule } from '@angular/material/table';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatMenuModule } from '@angular/material/menu';

import { DataTransferService } from '@app-services/data-transfer/data-transfer.service';
import { MockDataTransferService } from '@app-services/data-transfer/mock-data-transfer.service.spec';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';
import { MatDialog } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';

import { DataTransferManagerComponent } from './data-transfer-manager.component';
import { MatDialogModule } from '@angular/material/dialog';



describe('DataTransferManagerComponent', () => {
  let component: DataTransferManagerComponent;
  let fixture: ComponentFixture<DataTransferManagerComponent>;
  let service: DataTransferService;
  const mockDataTransferService: DataTransferService = new MockDataTransferService() as DataTransferService;
  const mockUtilService: UtilService = new MockUtilService() as UtilService;
  const mockMatDialog = jasmine.createSpyObj<MatDialog>(
    'MockMatDialog',
    ['open'],
  );

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatTableModule, RouterTestingModule, MatSnackBarModule, MatDialogModule, MatMenuModule, MatTooltipModule],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [DataTransferManagerComponent],
      providers: [
        { provide: DataTransferService, useValue: mockDataTransferService },
        { provide: UtilService, useValue: mockUtilService },
        { provide: MatDialog, useValue: mockMatDialog }
      ]
    })
    .compileComponents();
    fixture = TestBed.createComponent(DataTransferManagerComponent);
    component = fixture.componentInstance;
    service = TestBed.inject(DataTransferService);

    fixture.detectChanges();
  });

  afterEach(() => {
    fixture.destroy();
  });

  function whenUiIsStabilized() {
    fixture.detectChanges();
    flush();
  }

  it('should show source hostname in the table', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    expect(row1.cells[0].textContent).toEqual('srv-db-01');
    expect(row2.cells[0].textContent).toEqual('srv-db-02');
  }));

  it('should show DB name in the table', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];

    expect(row1.cells[1].textContent).toEqual('DB1');
    expect(row2.cells[1].textContent).toEqual('DB2');
  }));

  it('should show target hostname in the table', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[3];

    expect(row1.cells[2].textContent).toEqual('bms-target-01');
    expect(row2.cells[2].textContent).toEqual('bms-target-03bms-target-04');
  }));

  it('should show last operation in the table', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    const row3 = tableRows[3];
    const row5 = tableRows[5];

    expect(row1.cells[5].textContent).toEqual('PRE_RESTORE');
    expect(row2.cells[5].textContent).toEqual('BACKUP_RESTORE');
    expect(row3.cells[5].textContent).toEqual('ROLLBACK');
    expect(row5.cells[5].textContent).toEqual('DEPLOYMENT');
  }));

  it('should show last operation status in the table', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row3 = tableRows[3];
    const row4 = tableRows[4];

    expect(row1.cells[6].textContent).toEqual('FAILED 1 errors');
    expect(row3.cells[6].textContent).toEqual('IN_PROGRESS ');
    expect(row4.cells[6].textContent).toEqual('COMPLETE ');
  }));

  it('should show "Show log" in the table if the show link is present', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const firstRowLog = tableRows[1].cells[8].querySelector('button');
    const secondRowLog = tableRows[2].cells[8].querySelector('button');

    expect(firstRowLog).toBeDefined();
    expect(secondRowLog).toBeNull();
  }));

  it('should show pre-restore link if db is configured', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const preRestorLink = tableRows[5].cells[7].querySelector('button');
    expect(preRestorLink.textContent).toEqual('Pre-restore');

  }));

  it('should hide pre-restore link for non-configured db', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const preRestorLink = tableRows[3].cells[7].querySelector('button');
    expect(preRestorLink).toBeFalsy();
  }));

  it('should hide pre-restore link if operation is in Progress', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const preRestorLink = tableRows[6].cells[7].querySelector('button');
    expect(preRestorLink).toBeFalsy();
  }));

  it('should show errors amount if pre-restore failed', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const errorLink = tableRows[1].cells[6].querySelector('a.text-danger');
    expect(errorLink.textContent).toEqual('1 errors');
  }));

  it('should call errors popup onlick on errors link', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();
    spyOn(component, 'showErrors').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const errorLink = tableRows[1].cells[6].querySelector('a.text-danger');
    errorLink.click();
    expect(component.showErrors).toHaveBeenCalledWith(111);
  }));

  it('should show restore button if db is ready for restore', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const buttonRestore = tableRows[7].cells[7].querySelector('button');
    expect(buttonRestore.textContent).toEqual('Restore');
  }));

  it('should hide restore button if restore is in Progress', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const buttonRestore = tableRows[8].cells[7].querySelector('button');
    expect(buttonRestore).toBeFalsy();
  }));

  it('should show rollback button if next operation is roll_back', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(service, 'getTransferMappings').and.callThrough();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const buttonRollback = tableRows[9].cells[7].querySelector('button');
    expect(buttonRollback.textContent).toEqual('Rollback');
  }));

  it('run', () => {
    spyOn(component, 'run');

    component.run(1);

    expect(component.run).toHaveBeenCalledOnceWith(1);
  });

  it('scheduleRestore', () => {
    component.scheduleRestore({ id: 1 });

    expect(mockMatDialog.open).toHaveBeenCalled();
  });
})
