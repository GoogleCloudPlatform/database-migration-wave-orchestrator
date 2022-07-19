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
import { ComponentFixture, fakeAsync, flush, TestBed, tick } from '@angular/core/testing';
import { HttpClient } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatInputModule } from '@angular/material/input';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatRippleModule } from '@angular/material/core';
import { ManageLabelsComponent } from './manage-labels.component';
import { LabelService } from '@app-services/label/label.service';
import { MockLabelService } from '@app-services/label/mock-label.service.spec';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';
import { MatDialogModule } from '@angular/material/dialog';
import { By } from '@angular/platform-browser';


describe('ManageLabelsComponent', () => {
  let component: ManageLabelsComponent;
  let fixture: ComponentFixture<ManageLabelsComponent>;
  let labelService: LabelService;
  const mockLabelService: LabelService = new MockLabelService()  as LabelService;
  const mockUtilService: UtilService = new MockUtilService() as UtilService;
  
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FormsModule, ReactiveFormsModule, BrowserAnimationsModule, MatInputModule, MatSnackBarModule, MatDialogModule, MatRippleModule],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [ ManageLabelsComponent ],
      providers: [
        { provide: LabelService, useValue: mockLabelService },
        { provide: UtilService, useValue: mockUtilService },
        { provide: HttpClient, useValue: null }
      ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ManageLabelsComponent);
    component = fixture.componentInstance;
    labelService = TestBed.inject(LabelService);
    fixture.detectChanges();
  });

  function setLabel() {
    component.labels = [{
      name: 'label1',
      id: 1,
      project_id: 1 },
    ]
    fixture.detectChanges();
  }

  function whenUiIsStabilized() {
    fixture.detectChanges();
    flush();
  }

  it('should show all created labels', fakeAsync(() => {
    whenUiIsStabilized();
    const labelsInputs = fixture.nativeElement.querySelectorAll('.labels-form');
    expect(component.labels.length).toEqual(3);
    expect(labelsInputs.length).toEqual(3);
  }));

  it('should show label name in input', fakeAsync(() => {
    whenUiIsStabilized();
    setLabel();
    const labelInput = fixture.debugElement.query(By.css('.labels-form input'));
    expect(labelInput.nativeElement.getAttribute('ng-reflect-model')).toEqual(component.labels[0].name);
  }));

  it('should not call update label if value is not changed', fakeAsync(() => {
    whenUiIsStabilized();
    setLabel();
    spyOn(labelService, 'updateLabel').and.callThrough();
    const labelInput = fixture.debugElement.query(By.css('.labels-form input'));
    labelInput.nativeElement.focus();
    labelInput.nativeElement.blur();
    whenUiIsStabilized();
    expect(labelService.updateLabel).toHaveBeenCalledTimes(0);
  }));

  it('should call update label if value is changed', fakeAsync(() => {
    whenUiIsStabilized();
    setLabel();
    spyOn(labelService, 'updateLabel').and.callThrough();
    const labelInput = fixture.debugElement.query(By.css('.labels-form input'));
    labelInput.nativeElement.focus();  
    labelInput.nativeElement.value = 'lab-el4';
    labelInput.nativeElement.dispatchEvent(new Event('input'));
    labelInput.nativeElement.blur();
    whenUiIsStabilized();
    expect(labelService.updateLabel).toHaveBeenCalledTimes(1);
  }));

  it('should not call update label if value is not valid', fakeAsync(() => {
    whenUiIsStabilized();
    setLabel();
    spyOn(labelService, 'updateLabel').and.callThrough();
    const labelInput = fixture.debugElement.query(By.css('.labels-form input'));
    labelInput.nativeElement.focus();  
    labelInput.nativeElement.value = '4label';
    labelInput.nativeElement.dispatchEvent(new Event('input'));
    labelInput.nativeElement.blur();
    whenUiIsStabilized();
    expect(labelService.updateLabel).toHaveBeenCalledTimes(0);
  }));

  it('should not call update label if value is empty', fakeAsync(() => {
    whenUiIsStabilized();
    setLabel();
    spyOn(labelService, 'updateLabel').and.callThrough();
    const labelInput = fixture.debugElement.query(By.css('.labels-form input'));
    labelInput.nativeElement.focus();  
    labelInput.nativeElement.value = '';
    labelInput.nativeElement.dispatchEvent(new Event('input'));
    labelInput.nativeElement.blur();
    whenUiIsStabilized();
    expect(labelService.updateLabel).toHaveBeenCalledTimes(0);
  }));

  it('should call delete label on delete icon click', fakeAsync(() => {
    whenUiIsStabilized();
    setLabel();
    spyOn(component, 'deleteLabel');
    const labelDelete = fixture.debugElement.query(By.css('.labels-form .delete-label'));
    labelDelete.nativeElement.click();
    expect(component.deleteLabel).toHaveBeenCalledTimes(1);
  }));

  it('when click on delete button it should show warning popup with db count amount', fakeAsync(() => {
    whenUiIsStabilized(); 
    setLabel();   
    spyOn(labelService, 'getLabel').and.callThrough();
    spyOn(component, 'showConfirmationDialog').and.callThrough();
    const labelDelete = fixture.debugElement.query(By.css('.labels-form .delete-label'));
    labelDelete.nativeElement.click();
    expect(labelService.getLabel).toHaveBeenCalledTimes(1);
    expect(component.showConfirmationDialog).toHaveBeenCalledWith('label1 is linked to 3 source databases. Are you sure you want to delete it? This action can not be reverted.')
  }));
});