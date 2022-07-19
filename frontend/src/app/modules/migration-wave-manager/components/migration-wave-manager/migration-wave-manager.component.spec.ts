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

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterTestingModule } from '@angular/router/testing';
import {CUSTOM_ELEMENTS_SCHEMA} from "@angular/core";
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { MigrationWaveManagerComponent } from './migration-wave-manager.component';

import { WaveService } from '@app-services/wave/wave.service';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';
import { MockWaveService } from '@app-services/wave/mock-wave-service.spec';

import { Wave } from '@app-interfaces/wave';

describe('MigrationWaveManagerComponent', () => {
  let component: MigrationWaveManagerComponent;
  let fixture: ComponentFixture<MigrationWaveManagerComponent>;
  const mockUtilService: UtilService = new MockUtilService() as UtilService;
  const mockWaveService: WaveService = new MockWaveService() as WaveService;
  const tabGroup = jasmine.createSpyObj('MatTabGroup', ['selectedIndex']);
  const running_wave: Wave = {
    project_id: 1,
            id: 2,
            name: "wave2",
            is_running: true,
            step: {
              curr_step: 1,
              total_steps: 3,
            }
  }
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [ MigrationWaveManagerComponent ],
      imports: [CommonModule, RouterTestingModule, MatTabsModule, MatProgressSpinnerModule, BrowserAnimationsModule],
      providers: [
        {provide: WaveService, useValue: mockWaveService},
        {provide: UtilService, useValue: mockUtilService}
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MigrationWaveManagerComponent);
    component = fixture.componentInstance;
    component.tabGroup = tabGroup;
    fixture.detectChanges();
  });

  it('should create with waves tabs', () => {
    expect(component).toBeTruthy();
    component.waves?.push(running_wave);
    fixture.detectChanges();
    const tabs = fixture.debugElement.queryAll(By.css('.mat-tab-label'));
    expect(tabs.length).toBe(3);
  });

  it('should show wave details on tab select', () => {
    const tab_active = fixture.debugElement.query(By.css('.mat-tab-label:nth-child(2)')).nativeElement;
    tab_active.click();
    fixture.detectChanges();
    expect(tab_active).toHaveClass('mat-tab-label-active');
  });

  it('should hide wave details on tab deselect', () => {
    component.waves?.push(running_wave);
    fixture.detectChanges();
    const tab_active = fixture.debugElement.query(By.css('.mat-tab-label:nth-child(3)')).nativeElement;
    tab_active.click();
    fixture.detectChanges();
    const tab_inActive= fixture.debugElement.query(By.css('.mat-tab-label:nth-child(2)')).nativeElement;
    expect(tab_inActive).not.toHaveClass('mat-tab-label-active');
  });
});
