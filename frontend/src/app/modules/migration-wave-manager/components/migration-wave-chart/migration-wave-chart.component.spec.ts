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
import { MigrationWaveChartComponent } from './migration-wave-chart.component';

describe('MigrationWaveChartComponent', () => {
  let component:MigrationWaveChartComponent;
  let fixture: ComponentFixture<MigrationWaveChartComponent>;
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MigrationWaveChartComponent],
    }).compileComponents();
    fixture = TestBed.createComponent(MigrationWaveChartComponent);
    component = fixture.componentInstance;
  });

  it('should show undeployed chart for new wave', () => {
    spyOn(component, "drawResultChart").and.callThrough();
    spyOn(component, "drawGreyChart");
    component.waveProgress = {deployed: 0, failed: 0, undeployed: 1}
    fixture.detectChanges();
    expect(component.drawResultChart).toHaveBeenCalledTimes(1);
    expect(component.drawGreyChart).toHaveBeenCalledTimes(1);
  });

  it('should show running chart for running wave', () => {
    spyOn(component, "drawRunningChart").and.callThrough();
    spyOn(component, "drawGreyChart");
    component.waveIsRunning = true;
    component.waveSteps = {curr_step: 2, total_steps: 5}
    fixture.detectChanges();
    expect(component.drawRunningChart).toHaveBeenCalledTimes(1);
    expect(component.drawGreyChart).toHaveBeenCalledTimes(1);
  });

  it('should show deploy status chart for wave with deployed mappings', () => {
    spyOn(component, "drawResultChart").and.callThrough();
    spyOn(component, "drawGreyChart");
    component.waveProgress = {deployed: 1, failed: 1, undeployed: 1}
    fixture.detectChanges();
    expect(component.drawResultChart).toHaveBeenCalledTimes(1);
    expect(component.drawGreyChart).toHaveBeenCalledTimes(0);
  });
});
