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
import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { of } from 'rxjs';

import { MatSnackBar } from '@angular/material/snack-bar';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialog } from '@angular/material/dialog';

import { ScheduleRestoreService } from '@app-services/schedule-restore/schedule-restore.service';

import { ScheduleRestoreComponent } from "./schedule-restore.component";

describe('ScheduleRestoreComponent', () => {
  let component: ScheduleRestoreComponent;
  let fixture: ComponentFixture<ScheduleRestoreComponent>;
  const mockMatDialog = jasmine.createSpyObj<MatDialog>(
    'MockMatDialog',
    ['open'],
  );
  const mockScheduleRestoreService = jasmine.createSpyObj<ScheduleRestoreService>(
    'MockScheduleRestoreService',
    ['getScheduleRestore', 'updateScheduleRestore', 'createScheduleRestore', 'deleteScheduleRestore'],
  );

  mockScheduleRestoreService.getScheduleRestore.and.returnValue(of({ data: [{ id: 1, schedule_time: '' }]} as any));

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ FormsModule, ReactiveFormsModule, MatDialogModule],
      declarations: [ScheduleRestoreComponent],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        { provide: MatDialog, useValue: mockMatDialog },
        { provide: ScheduleRestoreService, useValue: mockScheduleRestoreService },
        {
          provide: MAT_DIALOG_DATA,
          useValue: {}
        },
        {
          provide: MatSnackBar,
          useValue: {}
        }
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ScheduleRestoreComponent);
    component = fixture.componentInstance;
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });

  it('ngOnInit', () => {
    component.ngOnInit();

    expect(mockScheduleRestoreService['getScheduleRestore']).toHaveBeenCalled();
  });

  it('schedule', () => {
    component.schedule();

    expect(mockMatDialog['open']).toHaveBeenCalled();
  });

  it('changeDateTime', () => {
    component.changeDateTime({ isValidForm: true, dateTime: 'dateTime' });

    expect(component.isValidForm).toBeTrue();
    expect(component.dateTime).toBe('dateTime');
  });
});
