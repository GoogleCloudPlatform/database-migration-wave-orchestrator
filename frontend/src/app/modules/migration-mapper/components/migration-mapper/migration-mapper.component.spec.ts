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

import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { ComponentFixture, TestBed, flush, fakeAsync } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { Location } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { of } from 'rxjs';

import { MatDialog } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatTableModule } from '@angular/material/table';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatRippleModule } from '@angular/material/core';

import { WaveService } from '@app-services/wave/wave.service';
import { MockWaveService, WAVE_DETAILED } from '@app-services/wave/mock-wave-service.spec';
import { SourceDbService } from '@app-services/source-db/source-db.service';
import { MockSourceDbService } from '@app-services/source-db/mock-source-db.service';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';
import { MappingService } from '@app-services/migration-mapper/mapping.service';
import { MockMappingService } from '@app-services/migration-mapper/mock-mapping.service.spec';
import { TargetsService } from '@app-services/targets/targets.service';
import { MockTargetsService } from '@app-services/targets/mock-targets.service.spec';
import { LabelService } from '@app-services/label/label.service';
import { MockLabelService } from '@app-services/label/mock-label.service.spec';

import { MigrationWaveManagerComponent } from './../../../migration-wave-manager/components/migration-wave-manager/migration-wave-manager.component';
import { MigrationMapperComponent } from './migration-mapper.component';
import { WaveAssignComponent } from "../wave-assign/wave-assign.component";

class MatDialogMock {
  open() {
    return {
      afterClosed: () => of({ ok: true, event: 'assign', wave: 'New wave'})
    };
  }
}

describe('MigrationMapperComponent', () => {
  let component: MigrationMapperComponent;
  let fixture: ComponentFixture<MigrationMapperComponent>;
  let location: Location;
  let mappingService: MappingService;
  let localStore: any;
  const mockUtilService: UtilService = new MockUtilService() as UtilService;
  const mockMappingService: MappingService = new MockMappingService() as MappingService;
  const mockTargetsService: TargetsService = new MockTargetsService() as TargetsService;
  const mockSourceDbService: SourceDbService = new MockSourceDbService() as SourceDbService;
  const mockWaveService: WaveService = new MockWaveService() as WaveService;
  const mockLabelService: LabelService = new MockLabelService() as LabelService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        FormsModule, ReactiveFormsModule, MatDialogModule, MatTableModule,
        MatTooltipModule, MatSelectModule, HttpClientTestingModule, MatInputModule,
        MatFormFieldModule, MatRippleModule, BrowserAnimationsModule, MatSnackBarModule,
        RouterTestingModule.withRoutes([
          { path: 'migrationwavemanager', component: MigrationWaveManagerComponent }
        ])
      ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [MigrationMapperComponent, WaveAssignComponent],
      providers: [
        { provide: UtilService, useValue: mockUtilService },
        { provide: MappingService, useValue: mockMappingService },
        { provide: TargetsService, useValue: mockTargetsService },
        { provide: SourceDbService, useValue: mockSourceDbService },
        { provide: WaveService, useValue: mockWaveService },
        { provide: LabelService, useValue: mockLabelService },
        { provide: MatDialog, useClass: MatDialogMock }
      ]
    })
    .compileComponents();
    fixture = TestBed.createComponent(MigrationMapperComponent);
    component = fixture.componentInstance;
    location = TestBed.inject(Location);
    mappingService = TestBed.inject(MappingService);
    fixture.detectChanges();

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
  });

  afterEach(() => {
    fixture.destroy();
  });

  function whenUiIsStabilized() {
    fixture.detectChanges();
    flush();
  }

  it('setFilterPredicate, should return true for is_configured: true', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: true }, '{"status":"configured"}')).toEqual(true);
  });

  it('setFilterPredicate, should return true for is_configured: true and labels (no labels)', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: true, labels: []}, '{"status":"configured","label":"no_label"}')).toEqual(true);
  });

  it('setFilterPredicate, should return true for is_configured: true and labels (label1111)', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: true, labels: [{id: 11, name: 'label1111'}]}, '{"status":"configured","label":"label1111"}')).toEqual(true);
  });

  it('setFilterPredicate, should return true for is_configured: false', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: false }, '{"status":"not configured"}')).toEqual(true);
  });

  it('setFilterPredicate, should return true for is_configured: false and labels (no labels)', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: false, labels: []}, '{"status":"not configured","label":"no_label"}')).toEqual(true);
  });

  it('setFilterPredicate, should return true for is_configured: false and labels (label1111)', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: false, labels: [{id: 11, name: 'label1111'}]}, '{"status":"not configured","label":"label1111"}')).toEqual(true);
  });

  it('setFilterPredicate, should return false for is_configured: false', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: false }, '{"status":"configured"}')).toEqual(false);
  });

  it('setFilterPredicate, should return false for is_configured: false and labels (no labels)', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: false, labels: []}, '{"status":"configured","label":"no labels"}')).toEqual(false);
  });

  it('setFilterPredicate, should return false for is_configured: false and labels (label1111)', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: false, labels: [{id: 11, name: 'label1111'}]}, '{"status":"configured","label":"label1111"}')).toEqual(false);
  });

  it('setFilterPredicate, should return true for is_configured: false', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ is_configured: false }, '{"status":""}')).toEqual(true);
  });

  it('setFilterPredicate, should return true for wave_id: 5', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ wave_id: 5 }, '{"status":"assigned"}')).toEqual(true);
  });

  it('setFilterPredicate, should return false for wave_id: 5 and labels ("label":"select all")', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ wave_id: 5, labels: []}, '{"status":"assigned","label":"select all"}')).toEqual(false);
  });

  it('setFilterPredicate, should return false for wave_id: undefined', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ wave_id: undefined }, '{"status":"assigned"}')).toEqual(false);
  });

  it('setFilterPredicate, should return false for wave_id: 5', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ wave_id: 5 }, '{"status":"not assigned"}')).toEqual(false);
  });

  it('setFilterPredicate, should return true for wave_id: undefined', () => {
    const filterfx = component['setFilterPredicate']();

    expect(filterfx({ wave_id: undefined }, '{"status":"not assigned"}')).toEqual(true);
  });

  it('ngOnInit, should remove item', () => {
    component.ngOnInit();

    expect(window.localStorage.removeItem).toHaveBeenCalledWith('filterStateMigration');
  });  

  it(`should go to url '/migrationwavemanager'`, fakeAsync(() => {
    whenUiIsStabilized();
    const manageWavesBtn = fixture.debugElement.query(By.css('a')).nativeElement;
    manageWavesBtn.click();
    fixture.detectChanges();

    fixture.whenStable().then(() => {
      expect(location.path()).toEqual('/migrationwavemanager');
    });
  }));

  it('should show target hostname in the table', fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    expect(row1.cells[0].textContent).toEqual('test');
    expect(row2.cells[0].textContent).toEqual('serverapp_3891');
  }));

  it('should show database name in the table', fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    expect(row1.cells[1].textContent).toEqual('test');
    expect(row2.cells[1].textContent).toEqual('APPDB_3891');
  }));

  it('should show oracle version in the table', fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    expect(row1.cells[2].textContent).toEqual('12.1');
    expect(row2.cells[2].textContent).toEqual('11.2');
  }));

  it('should show type of database in the table', fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    expect(row1.cells[3].textContent).toEqual('Real Application Cluster');
    expect(row2.cells[3].textContent).toEqual('Real Application Cluster');
  }));

  it(`should show 'Add node' button if the type of database is 'RAC'`, fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const addNodeBtn = row1.cells[4].querySelector('a');

    expect(addNodeBtn).toBeDefined();
    expect(addNodeBtn.textContent).toBe('+ Add Node');
  }));

  it(`should show amount of nodes based on 'fe_rac_nodes' and 'rac_nodes' parameters`, fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    const nodesRef1 = row1.cells[4].querySelectorAll('.d-flex');
    const nodesRef2 = row2.cells[4].querySelectorAll('.d-flex');

    expect(nodesRef1.length).toEqual(1);
    expect(nodesRef2.length).toEqual(2);
  }));

  it(`should show labels of nodes of database type 'RAC' starting from 1 and increasing each next one on 1`, fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const row2 = tableRows[2];
    const nodesRef1 = row1.cells[4].querySelectorAll('.d-flex mat-label');
    const nodesRef2 = row2.cells[4].querySelectorAll('.d-flex mat-label');

    expect(nodesRef1[0].textContent).toEqual('RAC Node 1:');
    expect(nodesRef2[0].textContent).toEqual('RAC Node 1:');
    expect(nodesRef2[1].textContent).toEqual('RAC Node 2:');
  }));

  it('should show disabled mat-select in target host column if the wave is running', fakeAsync(() => {
    whenUiIsStabilized();
    component.waves = new Array(WAVE_DETAILED);
    component.waves[0].is_running = true;
    fixture.detectChanges();

    const nodeSelectRef = fixture.debugElement.query(By.css('.d-flex mat-select')).nativeElement;
    expect(nodeSelectRef.getAttribute('aria-disabled')).toEqual('true');
  }));

  it('should show targets names in the options of select in target host name column', fakeAsync(() => {
    whenUiIsStabilized();
    const nodeSelectRef = fixture.debugElement.query(By.css('.d-flex .mat-select-trigger')).nativeElement;
    nodeSelectRef.click();
    flush();
    fixture.detectChanges();

    const matOptions = document.querySelectorAll('.mat-option');
    const firstOption = matOptions[0].querySelector('.mat-option-text');
    const secondOption = matOptions[1].querySelector('.mat-option-text');

    expect(firstOption?.textContent).toEqual('');
    expect(secondOption?.textContent).toEqual('test-bms');
  }));

  it('should show targets disabled options if it`s id is in the mappings bms list', fakeAsync(() => {
    whenUiIsStabilized();
    const nodeSelectRef = fixture.debugElement.query(By.css('.d-flex .mat-select-trigger')).nativeElement;
    nodeSelectRef.click();
    flush();
    fixture.detectChanges();

    const disabledOption = document.querySelectorAll('.mat-option')[2];
    expect(disabledOption.getAttribute('aria-disabled')).toEqual('true');
  }));

  it('should edit migration mapping when the target is selected', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(component, 'updateMappings').and.callThrough();
    spyOn(mappingService, 'editMigrationMapping').and.callThrough();

    const selectRef = fixture.debugElement.query(By.css('.d-flex .mat-select'));
    selectRef.triggerEventHandler('selectionChange', {});
    flush();
    fixture.detectChanges();

    expect(component.updateMappings).toHaveBeenCalledTimes(1);
    expect(mappingService.editMigrationMapping).toHaveBeenCalledTimes(1);
  }));

  it('should show disabled delete target node button if the amount of nodes is less than 2', fakeAsync(() => {
    whenUiIsStabilized();
    const targetNodeBtn = fixture.debugElement.query(By.css('.d-flex .delete-node button')).nativeElement;
    expect(targetNodeBtn.disabled).toBeTrue();
  }));

  it('should show disabled delete target node button if the wave is running', fakeAsync(() => {
    whenUiIsStabilized();
    component.waves = new Array(WAVE_DETAILED);
    component.waves[0].is_running = true;
    fixture.detectChanges();

    const targetNodeBtn = fixture.debugElement.queryAll(By.css('.d-flex .delete-node button'))[1].nativeElement;
    expect(targetNodeBtn.disabled).toBeTrue();
  }));

  it('should delete 1 rac node after clicking the delete button', fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(component, 'deleteNode').and.callThrough();
    spyOn(mappingService, 'editMigrationMapping').and.callThrough();
    spyOn(component, 'getMigrations');

    const targetNodeBtn = fixture.debugElement.queryAll(By.css('.d-flex .delete-node button'))[1].nativeElement;
    targetNodeBtn.click();
    fixture.detectChanges();

    expect(component.deleteNode).toHaveBeenCalledTimes(1);
    expect(mappingService.editMigrationMapping).toHaveBeenCalledTimes(1);
    expect(component.getMigrations).toHaveBeenCalledTimes(1);
  }));

  it(`should add node after clicking '+ Add Node' button`, fakeAsync(() => {
    whenUiIsStabilized();
    spyOn(component, 'addNode');
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row2 = tableRows[2];
    const addNodeBtn = row2.cells[4].querySelector('a');
    addNodeBtn.click();
    fixture.detectChanges();

    expect(component.addNode).toHaveBeenCalledTimes(1);
  }));

  it(`should not show '+ Add Node' if the type of database is Single Instance`, fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row3 = tableRows[3];
    const addNodeBtn = row3.cells[4].querySelector('a');

    expect(addNodeBtn).toBeNull();
  }));

  it(`should not show 'Open Config Editor' link if there are no bms selected`, fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const configEditorLink = row1.cells[5].querySelector('link');

    expect(configEditorLink).toBeNull();
  }));

  it(`should show 'Open Config Editor' after selecting the bms`, fakeAsync(() => {
    whenUiIsStabilized();
    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const configEditorLink = row1.cells[5].querySelector('.link');

    const selectRef = fixture.debugElement.query(By.css('.d-flex .mat-select'));
    selectRef.triggerEventHandler('selectionChange', {});
    flush();
    fixture.detectChanges();

    expect(configEditorLink).toBeDefined();
  }));

  it('should show the lock and no possibility to open config editor page if the wave is running', fakeAsync(() => {
    whenUiIsStabilized();
    component.waves = new Array(WAVE_DETAILED);
    component.waves[0].is_running = true;
    fixture.detectChanges();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row1 = tableRows[1];
    const configEditorLink = row1.cells[5].querySelector('.link');
    const lockIcon = row1.cells[5].querySelector('mat-icon');

    expect(configEditorLink).toBeNull();
    expect(lockIcon).toBeDefined();
  }));

  it(`should not show 'Select Wave:' option if there are no bms selected`, fakeAsync(() => {
    whenUiIsStabilized();
    component.waves = new Array(WAVE_DETAILED);
    fixture.detectChanges();

    const tableRows = fixture.nativeElement.querySelectorAll('tr');
    const row2 = tableRows[2];
    const selectWave = row2.cells[6].querySelector('.custom-select');

    expect(selectWave).toBeNull();
  }));

  it('should create migration mapping after selecting first target hostname', fakeAsync(() => {
    whenUiIsStabilized();
    let event = {
      $event: {},
      row: {
        db_name: 'APPDB_3891',
        db_size: 16544.855,
        db_type: 'RAC',
        fe_rac_nodes: 2,
        db_id: 528,
        nodes: [
          { label: 'RAC Node 1:', value: 111222 },
          { label: 'RAC Node 2:', value: '1' }
        ],
        nodes_amount: 2,
        source_hostname: 'serverapp_3891',
        wave_id: 1,
        bms: [],
        oracle_version: '11.2'
      },
      isWave: false,
      db_type: 'RAC'
    };
    spyOn(mappingService, 'createMigrationMapping').and.returnValue(of({}));
    component.updateMappings(event.$event, event.row, event.isWave, event.db_type);
    flush();
    fixture.detectChanges();

    expect(mappingService.createMigrationMapping).toHaveBeenCalledTimes(1);
  }));

  it('sould set unmapped targets first', () => {
    spyOn(component['subscriptions'], 'push');

    component.getTargets();

    expect(component['subscriptions'].push).toHaveBeenCalled();
    expect(component.targets).toEqual([
      {
        luns: [],
        data: [],
        client_ip: "10.132.0.55",
        cpu: "test",
        created_at: "2022-02-09T08:52:44.158896",
        id: 111222,
        location: "europe-west-3",
        name: "test-bms",
        ram: "16",
        secret_name: "test secret name",
        socket: "test socket",
      },
      {
        luns: [],
        data: [],
        client_ip: "10.132.0.55",
        cpu: "test-2",
        created_at: "2022-02-09T08:52:44.158896",
        id: 1,
        location: "europe-west-3",
        name: "test-bms-2",
        ram: "16",
        secret_name: "test secret name 2",
        socket: "test socket 2",
        isMapped: true
      }
    ]);
  });
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

  it('should open assign wave popup if the assign button is clicked',  fakeAsync(() => {
    spyOn(component, 'assignToWave').and.callThrough();
    whenUiIsStabilized();

    const assignWaveButton = fixture.debugElement.query(By.css('.assign-btn')).nativeElement;
    assignWaveButton.click();

    expect(component.assignToWave).toHaveBeenCalledTimes(1);
  }));

  it('should not open assign wave popup if no mappings are selected',  fakeAsync(() => {
    spyOn(component, 'assignToWave').and.callThrough();
    spyOn(component.dialog, 'open');
    whenUiIsStabilized();

    const statusSelect = fixture.debugElement.query(By.css('.status-filter .mat-select-trigger')).nativeElement;
    statusSelect.click();
    fixture.detectChanges();
    
    const matOption = fixture.debugElement.queryAll(By.css('.mat-option'))[1].nativeElement;
    matOption.click();
    fixture.detectChanges();
    
    const assignWaveButton = fixture.debugElement.query(By.css('.assign-btn')).nativeElement;
    assignWaveButton.click();
    fixture.detectChanges();
    flush();

    expect(component.assignToWave).toHaveBeenCalledTimes(1);
    expect(component.dialog.open).toHaveBeenCalledTimes(0);
  }));

  it('should not open assign wave popup if all selected mappings are not editable',  fakeAsync(() => {
    spyOn(component, 'assignToWave').and.callThrough();
    spyOn(component.dialog, 'open');
    whenUiIsStabilized();
    
    component.dataSource.filteredData?.forEach((mapping) => {
      mapping.editable = false;
    });
    fixture.detectChanges();
    
    const assignWaveButton = fixture.debugElement.query(By.css('.assign-btn')).nativeElement;
    assignWaveButton.click();
    fixture.detectChanges();
    flush();

    expect(component.assignToWave).toHaveBeenCalledTimes(1);
    expect(component.dialog.open).toHaveBeenCalledTimes(0);
  }));

  it('should open assign wave popup on click on the assign button',  fakeAsync(() => {
    spyOn(component, 'assignToWave').and.callThrough();
    spyOn(component.dialog, 'open').and.callThrough();
    whenUiIsStabilized();
    
    const assignWaveButton = fixture.debugElement.query(By.css('.assign-btn')).nativeElement;
    assignWaveButton.click();
    fixture.detectChanges();
    flush();

    expect(component.assignToWave).toHaveBeenCalledTimes(1);
    expect(component.dialog.open).toHaveBeenCalledTimes(2);
  }));
});
