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

import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Subscription } from 'rxjs';
import { MatTabGroup } from '@angular/material/tabs';

import { Wave } from '@app-interfaces/wave';

import { UtilService } from '@app-services/util/util.service';
import { WaveService } from '@app-services/wave/wave.service';
import { SlidingPanelService } from '@app-services/sliding-panel/sliding-panel.service';

@Component({
  selector: 'app-migration-wave-manager',
  templateUrl: './migration-wave-manager.component.html',
  styleUrls: ['./migration-wave-manager.component.scss']
})
export class MigrationWaveManagerComponent implements OnInit, OnDestroy {
  public waves!: Wave[] | undefined;
  private readonly project_id!: number;
  private refreshWaveSubscription!: Subscription;
  @ViewChild(MatTabGroup) tabGroup!: MatTabGroup;

  constructor(
    private waveService: WaveService,
    private util:UtilService,
    private slidingPanelService: SlidingPanelService,
  ) {
    if (this.util.getCurrentProjectId() != null) {
      this.project_id = this.util.getCurrentProjectId();
    }
  }

  ngOnInit(): void {
    this.getWaves();

    this.refreshWaveSubscription = this.waveService.refreshWaveList$.subscribe((val: boolean) => {
      if (val) {
      this.refreshWaveList();
    }
  });
}

  ngOnDestroy(): void {
    this.refreshWaveSubscription.unsubscribe();
  }

  onTabChange(selectedTabIndex: number): void {
    localStorage.setItem('selectedTabIndex', String(selectedTabIndex));
  }

  createWave(): void {
    this.slidingPanelService.slidingPanelConfig$.next({ name: 'wave', editMode: false });
  }

  refreshWaveList() {
    this.getWaves();
  }

  private getWaves() {
    this.waveService.getMigrationWaves(this.project_id).subscribe((resp) => {
      this.waves = resp.data?.sort((a, b) => {
        let keyA = a.id;
        let keyB = b.id;
        return ((keyA < keyB) ? -1 : 1);
      });

      if(this.waves) {
        const tabIndex = parseInt(localStorage.getItem('selectedTabIndex') || '');
        this.tabGroup.selectedIndex = tabIndex;
      }
    })
  }
}
