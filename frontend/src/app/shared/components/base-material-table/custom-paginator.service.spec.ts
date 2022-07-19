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
import { MatPaginatorModule, MatPaginatorIntl } from '@angular/material/paginator';

import { CustomPaginatorIntl } from './custom-paginator.service';

describe('CustomPaginatorIntl', () => {
  let service: CustomPaginatorIntl;
  let localStore: any;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [MatPaginatorModule],
      providers: [MatPaginatorIntl, CustomPaginatorIntl],
    })

    localStore = {};

    spyOn(window.localStorage, 'setItem').and.callFake(
      (key, value) => (localStore[key] = value + '')
    );

    service = TestBed.inject(
      CustomPaginatorIntl,
    );
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('getRangeLabel', () => {
    const result = service.getRangeLabel(1, 1, 2);

    expect(result).toEqual(`Page 2 of 2`);
    expect(localStorage.setItem).toHaveBeenCalledWith('pageSize', '1');
  });

  it('getRangeLabel, when length = 0', () => {
    const result = service.getRangeLabel(1, 5, 0);

    expect(result).toEqual(`Page 1 of 1`);
    expect(localStorage.setItem).toHaveBeenCalledWith('pageSize', '5');
  });
});
