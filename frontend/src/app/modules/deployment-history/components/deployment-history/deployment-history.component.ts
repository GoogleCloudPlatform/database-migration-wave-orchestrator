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

import { Component, OnInit } from '@angular/core';
import { Router } from "@angular/router";

import { DeploymentHistoryService } from "@app-services/deployment-history/deployment-history.service";
import { UtilService } from '@app-services/util/util.service';

import { DeploymentData } from "@app-interfaces/deployment";

import { formatMillisecondsToTime } from "@app-shared/helpers/functions";
import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";

@Component({
  selector: 'app-deployment-history',
  templateUrl: './deployment-history.component.html',
  styleUrls: ['./deployment-history.component.scss']
})
export class DeploymentHistoryComponent extends BaseMaterialTableComponent<DeploymentData> implements OnInit {
  displayedColumns = ['name', 'started_at', 'completed_at', 'duration', 'status', 'mappings_count', 'details'];
  private project_id!: number;

  constructor(
    private route: Router,
    private util:UtilService,
    private readonly deploymentHistoryService: DeploymentHistoryService) {
    super();
  }

  ngOnInit(): void {
    if (this.util.getCurrentProjectId() != null) {
      this.project_id = this.util.getCurrentProjectId();
    }
    this.loadData();
  }

  private loadData(): void {
    this.deploymentHistoryService.getDeploymentList(this.project_id).subscribe((response) => {
      const deploymentData: Array<DeploymentData> = [];
      response.data?.forEach((item) => {
        const data: DeploymentData = item;

        // @ts-ignore
        data.duration = formatMillisecondsToTime(new Date(item.completed_at) - new Date(item.started_at));
        data.details = 'Show details';

        deploymentData.push(data);
      });

      this.initDataSource(deploymentData);
    });
  }
}
