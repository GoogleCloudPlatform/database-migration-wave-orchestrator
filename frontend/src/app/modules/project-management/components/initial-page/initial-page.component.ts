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

import { Component, OnInit, ViewChild } from '@angular/core';
import { MatDrawer } from '@angular/material/sidenav';

import { SlidingPanelConfig } from '@app-interfaces/sliding-panel-config';

import { SlidingPanelService } from '@app-services/sliding-panel/sliding-panel.service';


@Component({
  selector: 'app-initial-page',
  templateUrl: './initial-page.component.html',
  styleUrls: ['./initial-page.component.scss']
})
export class InitialPageComponent implements OnInit {
  @ViewChild('drawer') drawer!: MatDrawer;
  panelType = PanelType;
  currentPanel!: PanelType;

  constructor(
    private slidingPanelService: SlidingPanelService,
  ) { }

  ngOnInit() {
    this.slidingPanelService.slidingPanelConfig$.subscribe((val: SlidingPanelConfig) => {
      switch(val.name) {
        case 'label': {
          this.currentPanel = PanelType.label;
          break;
        }
        case 'wave': {
          this.currentPanel = PanelType.wave;
          break;
        }
      }
      if (!!val.name) {
        this.drawer.toggle();
      }
    });

    this.slidingPanelService.closePanel$.subscribe((val: boolean) => {
      if (!!val) {
        this.drawer.close();
      }
    });
  }
}

enum PanelType {
	label = 'label',
  wave = 'wave'
}
