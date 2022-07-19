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

import { CommonModule } from '@angular/common';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { BrowserModule, By } from '@angular/platform-browser';
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { DataTransferIntroComponent } from './data-transfer-intro.component';
import { MigrationListingComponent } from '../../../migrations/components/migration-listing/migration-listing.component';

describe('DataTransferIntroComponent', () => {
  let component: DataTransferIntroComponent;
  let fixture: ComponentFixture<DataTransferIntroComponent>;
  let localStore: any;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [DataTransferIntroComponent],
      imports: [CommonModule, BrowserModule, BrowserAnimationsModule,
        RouterTestingModule.withRoutes([{
          path:'mymigrationprojects/list', component: MigrationListingComponent
        }])],
      providers: []
    }).compileComponents();

    localStore = {};

    spyOn(window.localStorage, 'setItem').and.callFake(
      (key, value) => (localStore[key] = value + '')
    );

    spyOn(window.localStorage, 'removeItem').and.callFake(
      (key) => (localStore[key] = '')
    );

    fixture = TestBed.createComponent(DataTransferIntroComponent);
    component = fixture.componentInstance;
  }));

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('readyBackup, should set item to localStorage', () => {
    component.hidePage = true;

    component.readyBackup();

    expect(localStorage.setItem).toHaveBeenCalledWith('hideBackupPreparationPage', 'true');
  });

  it('readyBackup, should remove item from localStorage', () => {
    component.hidePage = false;

    component.readyBackup();

    expect(localStorage.removeItem).toHaveBeenCalledWith('hideBackupPreparationPage');
  });
});

