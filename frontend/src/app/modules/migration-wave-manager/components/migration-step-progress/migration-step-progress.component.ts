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

import { Component, Input, OnInit } from "@angular/core";

import { WaveSteps, WaveStepsMeta } from "@app-interfaces/util";

import { UtilService } from "@app-services/util/util.service";

@Component({
    selector: 'app-migration-step-progress',
    templateUrl: './migration-step-progress.component.html'
  })
  export class MigrationStepProgressComponent implements OnInit {
    waveStepsMetaData!:WaveStepsMeta;
    public steps: WaveSteps[] = [];
    @Input() processType!: string;
    @Input() currentStep!: number;

    constructor(private utilService: UtilService) {}

    ngOnInit(): void {
      const currentOperation = this.processType.toLowerCase();
      this.waveStepsMetaData = this.utilService.getWaveStepsMetaData();
      this.steps =  this.waveStepsMetaData[currentOperation  as keyof WaveStepsMeta];
    }
  }
