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
import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { RouterTestingModule } from '@angular/router/testing';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { By } from '@angular/platform-browser';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';

import { WaveService } from '@app-services/wave/wave.service';
import { UtilService } from '@app-services/util/util.service';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';
import { MockWaveService, UNDEPLOYED_WAVE_MAPPING, WAVE_DETAILED, WAVE_MAPPING, WAVE_OPERATION } from '@app-services/wave/mock-wave-service.spec';

import { ViewMigrationWaveComponent } from './view-migration-wave.component';


describe('ViewMigrationWaveComponent', () => {
	let component: ViewMigrationWaveComponent;
	let fixture: ComponentFixture<ViewMigrationWaveComponent>;
	const mockUtilService: UtilService = new MockUtilService() as UtilService;
	const mockWaveService: WaveService = new MockWaveService() as WaveService;

	beforeEach(waitForAsync(() => {
		TestBed.configureTestingModule({
			schemas: [CUSTOM_ELEMENTS_SCHEMA],
			declarations: [ ViewMigrationWaveComponent],
			imports: [CommonModule, FormsModule, RouterTestingModule, BrowserAnimationsModule, MatButtonModule, MatTableModule, MatCheckboxModule, MatFormFieldModule, MatSelectModule, MatIconModule, MatSnackBarModule],
			providers: [
				{provide: WaveService, useValue: mockWaveService},
				{provide: UtilService, useValue: mockUtilService}
			]
		})

		.compileComponents();
		fixture = TestBed.createComponent(ViewMigrationWaveComponent);
		component = fixture.componentInstance;
		component.ngOnInit();
	}));

	function whenUiIsStabilized() {
		fixture.detectChanges();
		flush();
	}

	function givenWaveWithMapping() {
		component.wave.mappings?.push(WAVE_MAPPING);
	}

	function givenUndeployedWaveWithMapping() {
		component.wave.mappings?.push(UNDEPLOYED_WAVE_MAPPING)
	}

	function givenWaveIsRunning() {
		component.wave.curr_operation = WAVE_OPERATION;
		component.wave.is_running = true;
		component.wave.step = {curr_step: 1, total_steps: 3};
		if(component.wave.mappings) {
			component.wave.mappings[0].bms[0].logs_url = "url";
		}
	}

	it('should show wave details', fakeAsync(() =>  {
			whenUiIsStabilized();
			const wave_name = fixture.nativeElement.querySelector('.wave-details div:first-child b').innerHTML;
			const wave_deployment_date = fixture.nativeElement.querySelector('.wave-details div:nth-child(2) b').innerHTML;
			const wave_mappings = fixture.nativeElement.querySelector('.wave-details div:nth-child(3) b').innerHTML;
			expect(wave_name).toEqual(WAVE_DETAILED.name);
			expect(wave_deployment_date).toEqual('Not deployed yet');
			expect(wave_mappings).toEqual(WAVE_DETAILED.mappings.length.toString());
	}));

	it('should show add mappings link for empty wave', fakeAsync(() => {
		whenUiIsStabilized();
		const add_mappings = fixture.nativeElement.querySelector('.wave-actions .add-mappings');
		expect(add_mappings).toBeTruthy();
	}));

	it('should show action buttons and grid for wave with mappings', fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		fixture.detectChanges();
		const add_mappings = fixture.nativeElement.querySelector('.wave-actions .add-mappings');
		const start_deployment = fixture.nativeElement.querySelector('.wave-actions .start-deployment');
		const start_cleanup = fixture.nativeElement.querySelector('.wave-actions .start-cleanup');
		const mappings = fixture.nativeElement.querySelector('.wave-operations');
		expect(add_mappings).toBeFalsy();
		expect(start_cleanup).toBeTruthy();
		expect(start_deployment).toBeTruthy();
		expect(mappings).toBeTruthy();
	}));

	it('should show wave mappings in grid', fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		givenWaveWithMapping();
		component.applyStatusFilter();
		fixture.detectChanges();
		const mappings =  fixture.debugElement.queryAll(By.css('.mat-row'));
		expect(mappings.length).toBe(2);
	}));

	it('should show deselected mappings by default', fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		component.applyStatusFilter();
		component.getDisplayedColumns();
		fixture.detectChanges();
		const selectAllCheckbox = fixture.debugElement.query(By.css('.mat-header-cell mat-checkbox .mat-checkbox-input')).nativeElement;
		const selectCheckbox = fixture.debugElement.query(By.css('.mat-row:first-child mat-checkbox .mat-checkbox-input')).nativeElement;
		expect(selectAllCheckbox.checked).toBeFalsy();
		expect(selectCheckbox.checked).toBeFalsy();
	}));

	it('should hide selectAll checkbox if no configured mappings', fakeAsync(() => {
		whenUiIsStabilized();
		givenUndeployedWaveWithMapping();
		const selectAllCheckbox = fixture.debugElement.query(By.css('.mat-header-cell mat-checkbox .mat-checkbox-input'));
		expect(selectAllCheckbox).toBeFalsy();
	}));

	it('should send empty mappings ids list if no mapping selected', fakeAsync(() => {
		whenUiIsStabilized();
		expect(component.getMappings().length).toBe(0);
	}));

	it('should send mappings ids when selected in grid', fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		component.applyStatusFilter();
		fixture.detectChanges();
		const selectCheckbox = fixture.debugElement.query(By.css('.mat-row:first-child mat-checkbox .mat-checkbox-input')).nativeElement;
		selectCheckbox.click();
		flush();
		expect(selectCheckbox.checked).toBeTruthy();
		expect(component.getMappings()).toEqual([1]);
	}));

	it('should hide operation relaited columns in grid if wave is undeployed', fakeAsync(() => {
		whenUiIsStabilized();
		givenUndeployedWaveWithMapping();
		component.getDisplayedColumns();
		fixture.detectChanges();
		const mappingsGridHeaders = fixture.debugElement.queryAll(By.css('.mat-header-row .mat-header-cell'));
		expect(mappingsGridHeaders.length).toEqual(6);
	}));

	it('should show operation relaited columns in grid if at least one mappingin wave is undeployed', fakeAsync(() => {
		whenUiIsStabilized();
		givenUndeployedWaveWithMapping();
		givenWaveWithMapping();
		component.getDisplayedColumns();
		fixture.detectChanges();
		const mappingsGridHeaders = fixture.debugElement.queryAll(By.css('.mat-header-row .mat-header-cell'));
		expect(mappingsGridHeaders.length).toEqual(9);
	}));

	it('should show show log link for running mapping', fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		givenWaveIsRunning();
		component.getDisplayedColumns();
		component.applyStatusFilter();
		fixture.detectChanges();
		const logLink = fixture.debugElement.query(By.css('.mat-row:first-child .show-log')).nativeElement;
		expect(logLink.innerHTML).toEqual('Show Log');
	}));

	it("should show disabled buttons 'Start Deployment' and 'Cleanup' if checkboxes are not selected", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		fixture.detectChanges();
		const deploymentBtn = fixture.debugElement.query(By.css(".start-deployment")).nativeElement;
		const cleanupBtn = fixture.debugElement.query(By.css(".start-cleanup")).nativeElement;

		expect(deploymentBtn.disabled).toBeTruthy();
		expect(cleanupBtn.disabled).toBeTruthy();

		spyOn(component, "startDeployment");
		spyOn(component, "startCleanUp");
		deploymentBtn.click();
		fixture.detectChanges();
		expect(component.startDeployment).toHaveBeenCalledTimes(0);

		cleanupBtn.click();
		fixture.detectChanges();
		expect(component.startCleanUp).toHaveBeenCalledTimes(0);
	}));

	it("should show active buttons 'Start Deployment' and 'Cleanup' if checkbox is selected", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		component.applyStatusFilter();
		fixture.detectChanges();
		const deploymentBtn = fixture.debugElement.query(By.css(".start-deployment")).nativeElement;
		const cleanupBtn = fixture.debugElement.query(By.css(".start-cleanup")).nativeElement;
		const selectCheckbox = fixture.debugElement.query(By.css('.mat-row:first-child mat-checkbox .mat-checkbox-input')).nativeElement;
		selectCheckbox.click();
		flush();
		fixture.detectChanges();

		expect(deploymentBtn.disabled).toBeFalsy();
		expect(cleanupBtn.disabled).toBeFalsy();

		spyOn(component, "startDeployment");
		spyOn(component, "startCleanUp");
		deploymentBtn.click();
		fixture.detectChanges();
		expect(component.startDeployment).toHaveBeenCalledTimes(1);

		cleanupBtn.click();
		fixture.detectChanges();
		expect(component.startCleanUp).toHaveBeenCalledTimes(1);
	}));

	it("should show status filter if wave is not running", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		fixture.detectChanges();
		const statusFilter = fixture.debugElement.query(By.css('.status-filter'));
		expect(statusFilter).toBeTruthy();
	}));

	it("should hide status filter if wave is not running", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		givenWaveIsRunning();
		fixture.detectChanges();
		const statusFilter = fixture.debugElement.query(By.css('.status-filter'));
		expect(statusFilter).toBeFalsy();
	}));

	it("should filter mappings on Deployment Status", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		givenUndeployedWaveWithMapping();
		component.showConfiguredOnly = false;
		whenUiIsStabilized();
		spyOn(component, "applyStatusFilter").and.callThrough();
		const selectTrigger = fixture.debugElement.query(By.css('.status-filter .mat-select-trigger')).nativeElement;
		selectTrigger.click();
		whenUiIsStabilized();
		const depOption = fixture.debugElement.queryAll(By.css('.mat-select-panel mat-option'))[1].nativeElement;
		depOption.click();
		expect(component.applyStatusFilter).toHaveBeenCalledTimes(1);
		whenUiIsStabilized();
		expect(component.dataSource.filteredData.length).toBe(1);
		const mappings =  fixture.debugElement.queryAll(By.css('.mat-row'));
		expect(mappings.length).toBe(1);
	}));

	it("should filter mappings on Configuration Ready Status", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		givenUndeployedWaveWithMapping();
		whenUiIsStabilized();
		spyOn(component, "applyStatusFilter").and.callThrough();
		const isConfiguredOnlyCheckbox = fixture.debugElement.query(By.css('mat-checkbox.configured-only .mat-checkbox-input')).nativeElement;
		isConfiguredOnlyCheckbox.click();
		whenUiIsStabilized();
		expect(component.showConfiguredOnly).toBeFalse();
		expect(component.applyStatusFilter).toHaveBeenCalledTimes(1);
		whenUiIsStabilized();
		expect(component.wave.mappings?.length).toBe(2);
		const mappings =  fixture.debugElement.queryAll(By.css('.mat-row'));
		expect(mappings.length).toBe(2);
	}));

	it("should not start deployment if non-deployment mappins is selected", fakeAsync(() => {
		spyOn(component, "startDeployment").and.callThrough();
		spyOn(component, "openSnackBar");
		whenUiIsStabilized();
		givenWaveWithMapping();
		component.applyStatusFilter();
		whenUiIsStabilized();
		const deploymentBtn = fixture.debugElement.query(By.css(".start-deployment")).nativeElement;
		const selectCheckbox = fixture.debugElement.query(By.css('.mat-row:first-child mat-checkbox .mat-checkbox-input')).nativeElement;
		selectCheckbox.click();
		whenUiIsStabilized();
		expect(deploymentBtn.disabled).toBeFalsy();
		deploymentBtn.click();
		expect(component.startDeployment).toHaveBeenCalledTimes(1);
		component.startDeployment();
		expect(component.openSnackBar).toHaveBeenCalledWith('Before starting deployment, please select only deployable mappings.');
	}));

	it("should show notification when the deployment is started", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		component.applyStatusFilter();
		fixture.detectChanges();
		const deploymentBtn = fixture.debugElement.query(By.css(".start-deployment")).nativeElement;

		const selectCheckbox = fixture.debugElement.query(By.css('.mat-row:first-child mat-checkbox .mat-checkbox-input')).nativeElement;
		selectCheckbox.click();
		flush();
		fixture.detectChanges();

		spyOn(component, "openSnackBar");
		deploymentBtn.click();
		fixture.detectChanges();
		expect(component.openSnackBar).toHaveBeenCalledTimes(1);
	}));

	it("should show notification when the cleanup is started", fakeAsync(() => {
		whenUiIsStabilized();
		givenWaveWithMapping();
		component.applyStatusFilter();
		fixture.detectChanges();
		const cleanupBtn = fixture.debugElement.query(By.css(".start-cleanup")).nativeElement;

		const selectCheckbox = fixture.debugElement.query(By.css('.mat-row:first-child mat-checkbox .mat-checkbox-input')).nativeElement;
		selectCheckbox.click();
		flush();
		fixture.detectChanges();

		spyOn(component, "openSnackBar");
		cleanupBtn.click();
		fixture.detectChanges();
		expect(component.openSnackBar).toHaveBeenCalledTimes(1);
	}));
});
