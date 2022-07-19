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
import { RouterTestingModule } from "@angular/router/testing";
import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

import { DateTimeComponent } from "./date-time.component";

describe('DateTimeComponent', () => {
  let component: DateTimeComponent;
  let fixture: ComponentFixture<DateTimeComponent>;
  let baseTime: any;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, FormsModule, ReactiveFormsModule,],
      declarations: [DateTimeComponent],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    })
      .compileComponents();

    fixture = TestBed.createComponent(DateTimeComponent);
    component = fixture.componentInstance;

    baseTime = new Date(2022, 9, 23, 0);

    jasmine.clock().install();
    jasmine.clock().mockDate(new Date(baseTime));
  });

  afterEach(() => {
    jasmine.clock().uninstall();
  });

  it('should be created', () => {
    expect(component).toBeTruthy();
  });

  it('ngOnInit', () => {
    spyOn<any>(component, 'generateTimeList');
    spyOn<any>(component, 'setMaxDate');

    component.ngOnInit();

    expect(component['generateTimeList']).toHaveBeenCalled();
    expect(component['setMaxDate']).toHaveBeenCalled();
  });
});
