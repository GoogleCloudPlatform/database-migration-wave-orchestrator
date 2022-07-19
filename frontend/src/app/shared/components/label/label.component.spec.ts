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
import { HttpClient } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { By } from '@angular/platform-browser';

import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBarModule } from '@angular/material/snack-bar';

import { LabelService } from '@app-services/label/label.service';
import { MockLabelService } from '@app-services/label/mock-label.service.spec';

import { LabelComponent } from './label.component';

describe('LabelComponent', () => {
  let component: LabelComponent;
  let fixture: ComponentFixture<LabelComponent>;
  let labelService: LabelService;
  const mockLabelService: LabelService = new MockLabelService()  as LabelService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormsModule, ReactiveFormsModule, BrowserAnimationsModule, MatInputModule, 
        MatAutocompleteModule, MatChipsModule, MatSnackBarModule],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [ LabelComponent ],
      providers: [
        { provide: LabelService, useValue: mockLabelService },
        { provide: HttpClient, useValue: null }
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LabelComponent);
    component = fixture.componentInstance;
    labelService = TestBed.inject(LabelService);
    fixture.detectChanges();
  });

  function setLabels() {
    component.labels = [{
      name: 'label1',
      id: 1,
      project_id: 1 },
      {
      name: 'label2',
      id: 2,
      project_id: 1 
    }]
    fixture.detectChanges();
  }

  function setMiltipleDatabaseLabels() {
    component.databaseLabels = [
      {
        name: 'label1',
        id: 1
      },
      {
        name: 'label2',
        id: 2
      },
      {
        name: 'label3',
        id: 3
      },
      {
        name: 'label4',
        id: 4
      },
    ]
    fixture.detectChanges();
  }

  it('should set maxlength error if the value is longer than 15 symbols', async () => {
    setLabels();
    const labelInput = fixture.debugElement.query(By.css('input'));
    labelInput.nativeElement.value = 'testlongvaluefifteen';
    labelInput.triggerEventHandler('input', {
      target: labelInput.nativeElement
    })
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.labelControl.hasError('maxlength')).toEqual(true);
    })
  });

  
  it('should set pattern error if the value is invalid', async () => {
    setLabels();
    const labelInput = fixture.debugElement.query(By.css('input'));
    labelInput.nativeElement.value = 'wrong test-value';
    labelInput.triggerEventHandler('input', {
      target: labelInput.nativeElement
    })
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.labelControl.hasError('pattern')).toEqual(true);
    })
  });

  it('should show all labels after entering the 2 entering the 2 symbol in input', async () => {
    setLabels();
    const labelInput = fixture.debugElement.query(By.css('input'));
    labelInput.nativeElement.dispatchEvent(new Event('focus'));
    labelInput.nativeElement.dispatchEvent(new Event('focusin'));
    labelInput.nativeElement.value = 'la';
    labelInput.triggerEventHandler('input', {
      target: labelInput.nativeElement
    })
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      const matOptions = fixture.debugElement.queryAll(By.css('.mat-option'));
      const matOptionText1 = matOptions[0].nativeElement.querySelector('span').textContent;
      const matOptionText2 = matOptions[1].nativeElement.querySelector('span').textContent;

      expect(matOptionText1).toEqual(' label1 ');
      expect(matOptionText2).toEqual(' label2 ');
    })
  });

  it('should filter labels according to the value of input', async () => {
    setLabels();
    const labelInput = fixture.debugElement.query(By.css('input'));
    labelInput.nativeElement.dispatchEvent(new Event('focus'));
    labelInput.nativeElement.dispatchEvent(new Event('focusin'));
    labelInput.nativeElement.value = 'label2';
    labelInput.triggerEventHandler('input', {
      target: labelInput.nativeElement
    })
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      const matOptions = fixture.debugElement.queryAll(By.css('.mat-option'));
      const matOptionText1 = matOptions[0].nativeElement.querySelector('span').textContent;

      expect(matOptionText1).toEqual(' label2 ');
    })
  });

  it('should add new label to SourceDB', async () => {
    spyOn(labelService, 'addLabelSourceDb').and.callThrough();
    setLabels();

    const labelInput = fixture.debugElement.query(By.css('input'));
    labelInput.nativeElement.value = 'label3';
    labelInput.triggerEventHandler('input', {
      target: labelInput.nativeElement
    })
    fixture.detectChanges();

    labelInput.nativeElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'enter', bubbles: true }));
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      const matChips = fixture.debugElement.query(By.css('.mat-chip'));
      const newLabelText = matChips.childNodes[1].nativeNode.textContent;

      expect(labelService.addLabelSourceDb).toHaveBeenCalledTimes(1);
      expect(newLabelText).toEqual(' label3 ');
    })
  });

  it('should not add new label to SourceDB if it is already in database', async () => {
    spyOn(labelService, 'addLabelSourceDb').and.callThrough();
    setLabels();
    component.databaseLabels = [
      {
        name: 'label3',
        id:1
      },
    ]
    fixture.detectChanges();

    const labelInput = fixture.debugElement.query(By.css('input'));
    labelInput.nativeElement.value = 'label3';
    labelInput.triggerEventHandler('input', {
      target: labelInput.nativeElement
    })
    fixture.detectChanges();

    labelInput.nativeElement.dispatchEvent(new KeyboardEvent('keyup', { key: 'enter', bubbles: true }));
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(labelService.addLabelSourceDb).toHaveBeenCalledTimes(0);
    })
  });

  it('should delete label from SourceDB after clicking the cancel icon', async () => {
    spyOn(labelService, 'deleteLabelSourceDb').and.callThrough();
    setLabels();
    component.databaseLabels = [
      {
        name: 'label1',
        id:1
      },
    ]
    fixture.detectChanges();

    const deleteIcon = fixture.debugElement.query(By.css('mat-icon')).nativeElement;
    deleteIcon.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      const matChips = fixture.debugElement.query(By.css('.mat-chip'));

      expect(labelService.deleteLabelSourceDb).toHaveBeenCalledTimes(1);
      expect(matChips).toBeNull();
    })
  });

  it('should should 3 first labels for database', async () => {
    spyOn(labelService, 'addLabelSourceDb').and.callThrough();
    setLabels();
    setMiltipleDatabaseLabels();
    
    await fixture.whenStable().then(() => {
      const matChips = fixture.debugElement.queryAll(By.css('.mat-chip'));
      expect(matChips.length).toEqual(3);
    })
  });

  it('should show button with quantity of not shown labels', async () => {
    spyOn(labelService, 'addLabelSourceDb').and.callThrough();
    setLabels();
    setMiltipleDatabaseLabels();
    
    await fixture.whenStable().then(() => {
      const toggleBtn = fixture.debugElement.query(By.css('.toggle-btn')).nativeElement;
      expect(toggleBtn.textContent).toEqual('+ 1');
    })
  });

  it('should show all labels on click on the toggle button', async () => {
    spyOn(labelService, 'addLabelSourceDb').and.callThrough();
    setLabels();
    setMiltipleDatabaseLabels();

    const toggleBtn = fixture.debugElement.query(By.css('.toggle-btn')).nativeElement;
    toggleBtn.click();
    fixture.detectChanges();
    
    await fixture.whenStable().then(() => {
      const matChips = fixture.debugElement.queryAll(By.css('.mat-chip'));
      expect(matChips.length).toEqual(4);
    })
  });

  it('should show initial 3 labels on click on the toggle button if all labels are shown', async () => {
    spyOn(labelService, 'addLabelSourceDb').and.callThrough();
    setLabels();
    setMiltipleDatabaseLabels();

    const toggleBtn = fixture.debugElement.query(By.css('.toggle-btn')).nativeElement;
    toggleBtn.click();
    fixture.detectChanges();

    toggleBtn.click();
    fixture.detectChanges();
    
    await fixture.whenStable().then(() => {
      const matChips = fixture.debugElement.queryAll(By.css('.mat-chip'));
      expect(matChips.length).toEqual(3);
    })
  });
});