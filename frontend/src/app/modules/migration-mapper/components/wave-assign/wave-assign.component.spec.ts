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
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';

import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatRippleModule } from '@angular/material/core';
import { MatDividerModule } from '@angular/material/divider';

import { AssignWaveDialogData } from '@app-interfaces/migration';

import { WaveAssignComponent } from './wave-assign.component';


const dialogMock = {
    close: () => { }
};

const data: AssignWaveDialogData = {
  waves: [
    {
      id: 1,
      is_running: false,
      name: 'Wave 1',
      project_id: 1,
      status_rate: {deployed: 0, failed: 1, undeployed: 0}
    },
    {
      id: 2,
      is_running: false,
      name: 'Wave 2',
      project_id: 1,
      status_rate: {deployed: 0, failed: 0, undeployed: 1}
    }
  ]
}

describe('WaveAssignComponent', () => {
  let component: WaveAssignComponent;
  let fixture: ComponentFixture<WaveAssignComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ FormsModule, ReactiveFormsModule, BrowserAnimationsModule, MatFormFieldModule, MatInputModule, 
        MatDividerModule, MatSnackBarModule, MatDialogModule, MatSnackBarModule, MatAutocompleteModule, MatRippleModule ],
      schemas: [ CUSTOM_ELEMENTS_SCHEMA ],
      declarations: [ WaveAssignComponent ],
      providers: [
        { provide: MatDialogRef, useValue: dialogMock },
        { provide: MAT_DIALOG_DATA, useValue: data }
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(WaveAssignComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should set maxlenth error if the value is longer than 30 symbols', async () => {
    const waveInput = fixture.debugElement.query(By.css('input'));
    waveInput.nativeElement.value = 'The way too long name of the wave';
    waveInput.triggerEventHandler('input', {
        target: waveInput.nativeElement
      })
      fixture.detectChanges();
  
      await fixture.whenStable().then(() => {
        expect(component.waveControl.hasError('maxlength')).toEqual(true);
      })
  });

  it('should show all waves after entering the entering the 2 symbol in input', async () => {
    const waveInput = fixture.debugElement.query(By.css('input'));
    waveInput.nativeElement.dispatchEvent(new Event('focus'));
    waveInput.nativeElement.dispatchEvent(new Event('focusin'));
    waveInput.nativeElement.value = 'wa';
    waveInput.triggerEventHandler('input', {
      target: waveInput.nativeElement
    })
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      const matOptions = fixture.debugElement.queryAll(By.css('.mat-option'));
      const matOptionText1 = matOptions[0].nativeElement.querySelector('span').textContent;
      const matOptionText2 = matOptions[1].nativeElement.querySelector('span').textContent;

      expect(matOptionText1).toEqual(' Wave 1 ');
      expect(matOptionText2).toEqual(' Wave 2 ');
    })
  });

  it('should filter waves according to the value of input', async () => {
    const waveInput = fixture.debugElement.query(By.css('input'));
    waveInput.nativeElement.dispatchEvent(new Event('focus'));
    waveInput.nativeElement.dispatchEvent(new Event('focusin'));
    waveInput.nativeElement.value = 'Wave 2';
    waveInput.triggerEventHandler('input', {
      target: waveInput.nativeElement
    })
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      const matOptions = fixture.debugElement.queryAll(By.css('.mat-option'));
      const matOptionText1 = matOptions[0].nativeElement.querySelector('span').textContent;

      expect(matOptionText1).toEqual(' Wave 2 ');
    })
  });

  it('should close wave assign wave if cancel button is clicked', async () => {
    spyOn(component.dialogRef, 'close');

    const cancelBtn = fixture.debugElement.query(By.css('button')).nativeElement;
    cancelBtn.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.dialogRef.close).toHaveBeenCalledTimes(1);
    })
  });

  it('should not assign wave if there is no value in input', async () => {
    spyOn(component, 'assignWave').and.callThrough();
    spyOn(component.dialogRef, 'close');

    const assignBtn = fixture.debugElement.queryAll(By.css('button'))[1].nativeElement;
    assignBtn.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.assignWave).toHaveBeenCalledTimes(1);
      expect(component.dialogRef.close).toHaveBeenCalledTimes(0);
    })
  });

  it('should assign wave if there is value in input', async () => {
    spyOn(component, 'assignWave').and.callThrough();
    spyOn(component.dialogRef, 'close');

    const waveInput = fixture.debugElement.query(By.css('input'));
    waveInput.nativeElement.dispatchEvent(new Event('focus'));
    waveInput.nativeElement.dispatchEvent(new Event('focusin'));
    waveInput.nativeElement.value = 'Wave 3';
    waveInput.triggerEventHandler('input', {
      target: waveInput.nativeElement
    })
    fixture.detectChanges();

    const assignBtn = fixture.debugElement.queryAll(By.css('button'))[1].nativeElement;
    assignBtn.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.assignWave).toHaveBeenCalledTimes(1);
      expect(component.dialogRef.close).toHaveBeenCalledWith({ event: 'assign', wave: 'Wave 3' });
    })
  });
});
