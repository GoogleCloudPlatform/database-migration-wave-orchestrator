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

import { ComponentFixture, fakeAsync, flush, TestBed, waitForAsync } from '@angular/core/testing';
import { CommonModule } from '@angular/common';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { BrowserModule, By } from '@angular/platform-browser';
import { RouterTestingModule } from '@angular/router/testing';
import { MatTableModule } from '@angular/material/table';

import { MigrationWaveHistorySidebarComponent } from './migration-wave-history-sidebar.component';

import { DeploymentHistoryService } from '@app-services/deployment-history/deployment-history.service';
import { MockDeploymentHistoryService } from '@app-services/deployment-history/mock-deployment-history.service.spec';

describe('MigrationWaveHistorySidebarComponent', () => {
    let component: MigrationWaveHistorySidebarComponent;
    let fixture: ComponentFixture<MigrationWaveHistorySidebarComponent>;
    const mockDeploymentHistoryService: DeploymentHistoryService = new MockDeploymentHistoryService() as DeploymentHistoryService;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
            declarations: [MigrationWaveHistorySidebarComponent],
            imports: [CommonModule, BrowserModule, MatTableModule,
                RouterTestingModule],
            providers: [
                { provide: DeploymentHistoryService, useValue: mockDeploymentHistoryService }
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(MigrationWaveHistorySidebarComponent);
        component = fixture.componentInstance;
        window.history.pushState({ navigationId: 1 }, '', '');

        fixture.detectChanges();
    }));

    function whenUiIsStabilized() {
        fixture.detectChanges();
        flush();
    };

    it('should show source hostname', fakeAsync(() => {
        whenUiIsStabilized();
        const sourceHostNameRef = fixture.debugElement.query(By.css('li:nth-child(1) b')).nativeElement;
        expect(sourceHostNameRef.textContent).toEqual('new-stress-test-db-server49');
    }));

    it('should show database name', fakeAsync(() => {
        whenUiIsStabilized();
        const databaseRef = fixture.debugElement.query(By.css('li:nth-child(2) b')).nativeElement;
        expect(databaseRef.textContent).toEqual('DB49');
    }));

    it('should show type of the oracle version of the database', fakeAsync(() => {
        whenUiIsStabilized();
        const oracleVersionRef = fixture.debugElement.query(By.css('li:nth-child(3) b')).nativeElement;
        expect(oracleVersionRef.textContent).toEqual('19.3.0.0.0');
    }));

    it('should show target hostname', fakeAsync(() => {
        whenUiIsStabilized();
        const targetHostnameRef = fixture.debugElement.query(By.css('li:nth-child(4) b')).nativeElement;
        expect(targetHostnameRef.textContent).toEqual('tests-cycle3-49');
    }));
});

