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

import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

import { SlidingPanelConfig } from '@app-interfaces/sliding-panel-config';

@Injectable({
  providedIn: 'root'
})
export class SlidingPanelService {
  readonly INIT_SLIDING_PANEL_CONFIG = {
    name: '',
    editMode: false,
    waveId: null
  };

  slidingPanelConfig$: BehaviorSubject<SlidingPanelConfig> = new BehaviorSubject<SlidingPanelConfig>(
    this.INIT_SLIDING_PANEL_CONFIG,
  );

  closePanel$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
}
