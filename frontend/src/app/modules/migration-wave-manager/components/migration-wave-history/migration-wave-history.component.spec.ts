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
import { ActivatedRoute } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { of } from 'rxjs';

import { MigrationWaveHistoryComponent } from '@app-modules/migration-wave-manager/components/migration-wave-history/migration-wave-history.component';
import { MigrationWaveManagerComponent } from './../migration-wave-manager/migration-wave-manager.component';

import { DeploymentHistoryService } from '@app-services/deployment-history/deployment-history.service';
import { MockDeploymentHistoryService } from '@app-services/deployment-history/mock-deployment-history.service.spec';


const activatedRouteMock = {
    queryParams: of({
        databaseId: '123',
    }),
};


describe('MigrationWaveHistoryComponent', () => {
    let component: MigrationWaveHistoryComponent;
    let fixture: ComponentFixture<MigrationWaveHistoryComponent>;
    const mockDeploymentHistoryService: DeploymentHistoryService = new MockDeploymentHistoryService() as DeploymentHistoryService;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
            declarations: [MigrationWaveHistoryComponent],
            imports: [CommonModule, BrowserModule, MatTableModule, MatTooltipModule,
                RouterTestingModule.withRoutes([
                    {
                        path: 'migrationwavemanager',
                        component: MigrationWaveManagerComponent
                    }
                ])],
            providers: [
                { provide: DeploymentHistoryService, useValue: mockDeploymentHistoryService },
                {
                    provide: ActivatedRoute,
                    useValue: activatedRouteMock
                },
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(MigrationWaveHistoryComponent);
        component = fixture.componentInstance;
        window.history.pushState({ navigationId: 1 }, '', '');

        component.ngOnInit();
    }));

    function whenUiIsStabilized() {
        fixture.detectChanges();
        flush();
    }


    it('should show header with source_hostname and target hostname', fakeAsync(() => {
        whenUiIsStabilized();
        let headerRef = fixture.debugElement.query(By.css('.section-header')).nativeElement;
        expect(headerRef.textContent).toEqual('Mapping Details for new-stress-test-db-server49 - tests-cycle3-49');
    }));

    it('should show operation type in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[0].textContent).toEqual('DEPLOYMENT');
    }));

    it('should start date type in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[1].textContent).toEqual('Thu, 28 Apr 2022 08:40:48 GMT');
    }));

    it('should complete date type in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[2].textContent).toEqual('Thu, 28 Apr 2022 08:40:49 GMT');
    }));

    it('should calculate duration time in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[3].textContent).toEqual('00:00:01');
    }));

    it('should show operation status in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        expect(row1.cells[4].textContent).toEqual('FAILED');
    }));

    it('should show log link in the table', fakeAsync(() => {
        whenUiIsStabilized();
        const tableRows = fixture.nativeElement.querySelectorAll('tr');
        const row1 = tableRows[1];
        const logLink = row1.cells[5].querySelector('a');
        expect(logLink.textContent).toEqual('Show log');
        expect(logLink.href).toEqual('https://console.cloud.google.com/');
    }));
});

