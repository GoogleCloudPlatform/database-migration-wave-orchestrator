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

import { MigrationListingComponent } from './../migration-listing/migration-listing.component';
import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { Router } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from "@angular/router/testing";
import { of } from "rxjs";

import { MatRippleModule } from '@angular/material/core';

import { Migration } from "@app-interfaces/migration";

import { MigrationsComponent } from './migrations.component';

import { MigrationService } from "@app-services/migration/migration.service";

describe('MigrationsComponent', () => {
  const mockMigrationService = jasmine.createSpyObj<MigrationService>(
    'MockMigrationService', ['projectList'],
  );

  let component: MigrationsComponent;
  let fixture: ComponentFixture<MigrationsComponent>;
  let router: Router;

  mockMigrationService.projectList.and.returnValue(of({} as Migration));

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MatRippleModule, RouterTestingModule.withRoutes([{
        path:'mymigrationprojects/list', component: MigrationListingComponent
      }])],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [ MigrationsComponent ],
      providers: [
        { provide: MigrationService, useValue: mockMigrationService }
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MigrationsComponent);
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
    });

    it('should not call navigateByUrl', () => {
      mockMigrationService.projectList.and.returnValue(of({} as Migration));
      component.ngOnInit();

      expect(navigateSpy).not.toHaveBeenCalled();
    });

    it('ngOnInit, should call navigateByUrl', () => {
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

      expect(navigateSpy).toHaveBeenCalled();
    });

    afterEach(() => {
      expect(mockMigrationService.projectList).toHaveBeenCalled();
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
});
