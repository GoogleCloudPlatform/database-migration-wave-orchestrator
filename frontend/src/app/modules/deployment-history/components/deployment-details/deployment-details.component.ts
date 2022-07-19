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
import { ActivatedRoute, Router } from "@angular/router";

import { DeploymentHistoryService } from "@app-services/deployment-history/deployment-history.service";

import { DeploymentDetailsData, DeploymentDetailsResponse, DeploymentDetailsResponseMeta } from "@app-interfaces/deployment";

import { formatDate } from "@app-shared/helpers/functions";
import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";

@Component({
  selector: 'app-deployment-details',
  templateUrl: './deployment-details.component.html',
  styleUrls: ['./deployment-details.component.scss']
})
export class DeploymentDetailsComponent extends BaseMaterialTableComponent<DeploymentDetailsData> implements OnInit {
  deploymentId?: string;
  deploymentStartDate?: string;
  displayedColumns = ['source_hostname', 'database', 'target_hostname', 'type', 'version', 'status', 'log'];
  waveId?: string;

  constructor(
    private readonly activatedRoute: ActivatedRoute,
    private router: Router,
    private readonly deploymentHistoryService: DeploymentHistoryService) {
    super();
  }

  ngOnInit(): void {
    this.activatedRoute.queryParams.subscribe((params) => {
      this.waveId = params.wave;
      this.deploymentId = params.operation;
      this.loadData();
    });
  }

  private loadData(): void {
    if (!this.waveId || !this.deploymentId) {
      this.router.navigateByUrl(`/deploymenthistory`);
      return;
    }

    this.deploymentHistoryService.getDeploymentDetails(this.waveId, this.deploymentId).subscribe((response) => {
      if (!response.data || !response.data[0]) return;

      this.initTableData(response.data);
      this.deploymentStartDate = formatDate(response.data[0].bms[0].started_at);
    });
  }

  private initTableData(data: Array<DeploymentDetailsResponse>) {
    const deploymentData: Array<DeploymentDetailsData> = [];

    data.forEach((item) => {
      const data: DeploymentDetailsData = Object.create(item);

      data.source_hostname = item.source_db.source_hostname;
      data.database = item.source_db.db_name;
      data.bms = item.bms;
      data.type = item.source_db.db_type;
      data.version = item.source_db.oracle_version;
      data.log = 'Show Log';

      deploymentData.push(data);
    });

    this.initDataSource(deploymentData);
    this.setSorting();
  }

  private setSorting() {
    this.dataSource.sortingDataAccessor = (item, property) => {
      if (property === 'target_hostname') {
        return item.bms[0].name
      } else {
        let key = item[property as keyof DeploymentDetailsData]?.toLocaleString()
        return  key ? key : '';
      }
    };
  }
}
