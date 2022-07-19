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

import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription } from "rxjs";
import { ActivatedRoute } from "@angular/router";

import { DeploymentHistoryService } from "@app-services/deployment-history/deployment-history.service";

import { formatDate } from "@app-shared/helpers/functions";

@Component({
  selector: 'app-deployment-details-sidebar',
  templateUrl: './deployment-details-sidebar.component.html',
  styleUrls: ['./deployment-details-sidebar.component.scss']
})
export class DeploymentDetailsSidebarComponent implements OnInit, OnDestroy {
  completion: number = 0;
  deploymentStatus?: string;
  mappingsCount?: number;
  startDeploymentDate?: string;
  waveId?: string|number;
  waveName?: string;
  routeSubscription!: Subscription;

  constructor(
    private readonly activatedRoute: ActivatedRoute,
    private readonly deploymentHistoryService: DeploymentHistoryService) {}

  ngOnInit(): void {
    this.routeSubscription = this.activatedRoute.queryParams.subscribe((params) => {
      this.waveId = params.wave;
      this.loadData();
    });
  }

  ngOnDestroy() {
    this.routeSubscription.unsubscribe();
  }

  private loadData(): void {
    if (!this.waveId) return;

    this.deploymentHistoryService.getWaveDetails(this.waveId).subscribe((response) => {
      this.completion = response.status_rate && response.mappings
        ? (response.status_rate.deployed / response.mappings?.length) * 100
        : 0;
      this.mappingsCount = response.mappings_count;
      this.waveName = response.name;

      if (response.last_deployment && response.last_deployment.started_at) {
        this.startDeploymentDate = formatDate(response.last_deployment.started_at);
      }

      if (response.is_running) {
        this.deploymentStatus = 'Running';
      } else if (!response.is_running && this.completion === 100) {
        this.deploymentStatus = 'Completed';
      } else {
        this.deploymentStatus = 'Failed';
      }
    });
  }
}
