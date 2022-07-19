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

import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from "@angular/common/http/testing";

import { FormateDateService } from './formate-date.service';

describe('FormateDateService', () => {
  let service: FormateDateService;
  let baseTime: any;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports:[HttpClientTestingModule]
    });
    service = TestBed.inject(FormateDateService);

    baseTime = new Date(2022, 9, 23);

    jasmine.clock().install();
    jasmine.clock().mockDate(new Date(baseTime));
  });

  afterEach(() => {
    jasmine.clock().uninstall();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('convert24hourTo12HourFormat', () => {
    expect(service.convert24hourTo12HourFormat('18:15')).toBe('6:15 PM');
  });

  it('convert12HourTo24hourFormat', () => {
    expect(service['convert12HourTo24hourFormat']('6:15 PM')).toBe('18:15');
  });

  it('getTime', () => {;
    expect(service.getTime(baseTime)).toBe('0:00');
  });

  it('formateDate', () => {
    spyOn<any>(service, 'convert12HourTo24hourFormat').and.returnValue('18:15');

    service.formateDate({ date: baseTime, time: '6:15 PM' });

    expect(service['convert12HourTo24hourFormat']).toHaveBeenCalledWith('6:15 PM');
  });

  it('isTimeBigger', () => {
    expect(service.isTimeBigger('6:15', '18:15')).toBe(false);
    expect(service.isTimeBigger('20:15', '18:15')).toBe(true);
  });
});
