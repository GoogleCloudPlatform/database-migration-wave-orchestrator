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
import { ComponentFixture, TestBed } from "@angular/core/testing";
import { Router } from '@angular/router';
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { RouterTestingModule } from "@angular/router/testing";
import { of } from "rxjs";

import { MatDialog } from "@angular/material/dialog";

import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatRippleModule } from '@angular/material/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FormsModule } from "@angular/forms";
import { MatTableModule } from "@angular/material/table";

import { MockUtilService } from "@app-services/util/mock-util-service.spec";
import { UtilService } from "@app-services/util/util.service";
import { MigrationService } from "@app-services/migration/migration.service";

import { Migration } from "@app-interfaces/migration";

import { MigrationListingComponent } from "./migration-listing.component";
import { MigrationsComponent } from '../migrations/migrations.component';
import { HighlightPipe } from "@app-shared/components/highlight/highlight.pipe";
import { MatMenuModule } from "@angular/material/menu";


describe("MigrationListingComponent", () => {
  let component: MigrationListingComponent;
  let fixture: ComponentFixture<MigrationListingComponent>;
  let router: Router;
  const mockUtilService: UtilService = new MockUtilService() as UtilService;
  const mockMigrationService = jasmine.createSpyObj<MigrationService>(
    'MockMigrationService', ['projectList', 'getMigrationsProjects'],
  );

  mockMigrationService.projectList.and.returnValue(of({} as Migration));
  mockMigrationService.getMigrationsProjects.and.returnValue(of({ data: [
    {
      description: '',
      id: 70,
      name: '396_ch',
      subnet: 'regions/europe-west1/subnetworks/bms-subnpriv-oracle-rac',
      vpc: 'global/networks/bms-priv-oracle-rac'
    }
  ]} as Migration));

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatSnackBarModule,
        MatRippleModule,
        BrowserAnimationsModule,
        FormsModule,
        MatTableModule,
        MatMenuModule,
        RouterTestingModule.withRoutes([{
          path:'mymigrationprojects', component: MigrationsComponent
        }])
      ],
      declarations: [
        MigrationListingComponent,
        HighlightPipe
      ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        { provide: UtilService, useValue: mockUtilService },
        { provide: MigrationService, useValue: mockMigrationService },
        { provide: MatDialog, useValue: null },
        { provide: MatSnackBar, useValue: null },
        HighlightPipe
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(MigrationListingComponent);
    component = fixture.componentInstance;
    router = TestBed.get(Router);

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('ngOnInit', () => {
    let navigateSpy: any;

    beforeEach(() => {
      navigateSpy = spyOn(router, 'navigateByUrl');
      spyOn(component, 'getMigrations');
    });

    it('should call navigateByUrl', () => {
      mockMigrationService.projectList.and.returnValue(of({} as Migration));
      component.ngOnInit();

      expect(navigateSpy).toHaveBeenCalled();
    });

    it('should not call navigateByUrl', () => {
      mockMigrationService.projectList.and.returnValue(of({
        data: [
          {
            description: '',
            id: 70,
            name: '396_ch',
            subnet: 'regions/europe-west1/subnetworks/bms-subnpriv-oracle-rac',
            vpc: 'global/networks/bms-priv-oracle-rac'
          }
        ]
      } as Migration));

      component.ngOnInit();

      expect(navigateSpy).not.toHaveBeenCalled();
      expect(component.getMigrations).toHaveBeenCalled();
    });
  });

  it('should unsubscribe', () => {
    spyOn(component['projectListSubscription'], 'unsubscribe');

    component.ngOnDestroy();

    expect(component['projectListSubscription'].unsubscribe).toHaveBeenCalled();
  });

  it('should call navigateByUrl', () => {
    const navigateSpy = spyOn(router, 'navigateByUrl');

    component.redirect('asd');

    expect(navigateSpy).toHaveBeenCalledWith('/asd');
  });

  it('should call initDataSource', () => {
    spyOn<any>(component, 'initDataSource');

    component.getMigrations();

    expect(mockMigrationService.getMigrationsProjects).toHaveBeenCalledWith();
    expect(component.projects).toEqual([
      {
        description: '',
        id: 70,
        name: '396_ch',
        subnet: 'regions/europe-west1/subnetworks/bms-subnpriv-oracle-rac',
        vpc: 'global/networks/bms-priv-oracle-rac'
      }
    ]);
    expect(component['initDataSource']).toHaveBeenCalled();
  });

  describe('action', () => {
    const row = { id: 1 } as Migration;
    beforeEach(() => {
      spyOn(component, 'setSelected');
      spyOn(component, 'redirect');
      spyOn(component, 'deleteProject');
    });

    it('check open', () => {
      component.action('open', row);

      expect(component.setSelected).toHaveBeenCalledWith(1);
      expect(component.redirect).toHaveBeenCalledWith('/softwarelibrary');
    });

    it('check view', () => {
      component.action('view', row);

      expect(component.redirect).toHaveBeenCalledWith('/mymigrationprojects/view/1');
    });

    it('check edit', () => {
      component.action('edit', row);

      expect(component.redirect).toHaveBeenCalledWith('/mymigrationprojects/edit/1');
    });

    it('check delete', () => {
      component.action('delete', row);

      expect(component.deleteProject).toHaveBeenCalledWith(1);
    });
  });

  describe('deleteProject', () => {
    beforeEach(() => {
      spyOn(component, 'showConfirmationDialog');
    });

    it('sould not to call showConfirmationDialog', () => {
      component.deleteProject(undefined);

      expect(component.showConfirmationDialog).not.toHaveBeenCalled();
    });

    it('sould to call showConfirmationDialog', () => {
      component.deleteProject(1);

      expect(component.showConfirmationDialog).toHaveBeenCalled();
    });
  });
});
