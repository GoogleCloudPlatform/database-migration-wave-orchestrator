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

import { ComponentFixture, fakeAsync, flush, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from "@angular/router/testing";
import { ActivatedRoute } from "@angular/router";
import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { By } from '@angular/platform-browser';
import { of } from "rxjs";

import { MappingService } from "@app-services/migration-mapper/mapping.service";
import { MockMappingService } from "@app-services/migration-mapper/mock-mapping.service.spec";

import { ConfigEditorSidebarComponent } from "./config-editor-sidebar.component";

import { getDBType }  from "@app-shared/helpers/functions";

import { Mapping } from "@app-interfaces/mapping";
import { HttpClient } from '@angular/common/http';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';

const activatedRouteMock = {
  queryParams: of({
    databaseId: '123',
  }),
};

describe("ConfigEditorSidebarComponent",() => {
  let component: ConfigEditorSidebarComponent;
  let fixture: ComponentFixture<ConfigEditorSidebarComponent>;
  let route: ActivatedRoute;
  let service: MappingService;
  const mockMappingService: MappingService = new MockMappingService() as MappingService;
  const mockUtilService: UtilService = new MockUtilService() as UtilService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule],
      declarations: [ConfigEditorSidebarComponent],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        {provide: UtilService, useValue: mockUtilService},
        {provide: MappingService, useValue: mockMappingService},
        {provide: HttpClient, useValue: null},
        {
          provide: ActivatedRoute,
          useValue: activatedRouteMock
        },
      ]
    })
      .compileComponents();

    fixture = TestBed.createComponent(ConfigEditorSidebarComponent);
    component = fixture.componentInstance;
    route = TestBed.inject(ActivatedRoute);
    service = TestBed.inject(MappingService);

    component.ngOnInit();
  });

  afterEach(() => {
    fixture.destroy();
  });

  function whenUiIsStabilized() {
    fixture.detectChanges();
    flush();
  }

  it("should show oracle release", fakeAsync(() => {
    whenUiIsStabilized();
    fixture.detectChanges();

    const oracleVersionItem = fixture.debugElement
      .query(By.css("li:nth-child(6) b")).nativeElement;
    expect(oracleVersionItem.textContent).toEqual("19.11.0.0.210412");
   })
  );

  it("should show correct db type", fakeAsync(() => {
    whenUiIsStabilized();
    fixture.detectChanges();

    const oracleVersionItem = fixture.debugElement
      .query(By.css("li:nth-child(4) b")).nativeElement;
    expect(oracleVersionItem.textContent).toEqual("Real Application Cluster");
    })
  );

  it("should show server name", fakeAsync(() => {
    whenUiIsStabilized();
    fixture.detectChanges();

    const oracleVersionItem = fixture.debugElement
      .query(By.css("li:nth-child(2) b")).nativeElement;
    expect(oracleVersionItem.textContent).toEqual("test");
   })
 );

  it("should show database name", fakeAsync(() => {
    whenUiIsStabilized();
    fixture.detectChanges();

    const oracleVersionItem = fixture.debugElement
      .query(By.css("li:nth-child(1) b")).nativeElement;
    expect(oracleVersionItem.textContent).toEqual("test");
   })
  );

  it("should show oracle version", fakeAsync(() => {
    whenUiIsStabilized();
    fixture.detectChanges();

    const oracleVersionItem = fixture.debugElement
      .query(By.css("li:nth-child(3) b")).nativeElement;
    expect(oracleVersionItem.textContent).toEqual("18.1");
   })
  );

  it("should show 1 target name", fakeAsync(() => {
    whenUiIsStabilized();
    fixture.detectChanges();

    const oracleVersionItem = fixture.debugElement
      .query(By.css("li:nth-child(5) b")).nativeElement;
    expect(oracleVersionItem.textContent).toEqual("test-cycle1");
   })
  );

  it("should not show release field if no data with oracle release id provided", fakeAsync(() => {
      whenUiIsStabilized();
      fixture.detectChanges();

      component.mappings.oracle_release = undefined;
      fixture.detectChanges();

      const oracleVersionItem = fixture.debugElement
        .query(By.css("li:nth-child(6)"));
      expect(oracleVersionItem).toBeNull();
    })
  );
});
