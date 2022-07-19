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
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';

import { DeploymentHistoryService } from '@app-services/deployment-history/deployment-history.service';

import { formatMillisecondsToTime } from '@app-shared/helpers/functions';

import { DatabaseOperationsHistoryResponse, DatabaseOperationsHistoryDetails } from '@app-interfaces/database-operations-history';

import { BaseMaterialTableComponent } from '@app-shared/components/base-material-table/base-material-table.component';

@Component({
  selector: 'app-migration-wave-history',
  templateUrl: './migration-wave-history.component.html',
  styleUrls: ['./migration-wave-history.component.scss']
})
export class MigrationWaveHistoryComponent extends BaseMaterialTableComponent<DatabaseOperationsHistoryDetails> implements OnInit, OnDestroy {
  private routeSubscription!: Subscription;
  public displayedColumns = ['operation_type', 'started_at', 'completed_at' , 'duration', 'operation_status', 'log'];
  public deploymentDetails!: DatabaseOperationsHistoryResponse;
  public targetHostname: string = '';
  databaseId?: string;

  constructor(
    private deploymentHistoryService: DeploymentHistoryService,
    private readonly router: Router,
    private activatedRoute: ActivatedRoute
  ) {
    super();
  }

  ngOnInit(): void {
    this.routeSubscription = this.activatedRoute.queryParams.subscribe((params) => {
      this.databaseId = params.databaseId;
      this.loadData();
    });
  }

  ngOnDestroy() {
    this.routeSubscription.unsubscribe();
  }

  private loadData(): void {
    if (!this.databaseId) {
      this.router.navigateByUrl('/migrationwavemanager');
      return;
    }

    this.deploymentHistoryService.getDatabaseMappingsHistory(this.databaseId).subscribe((response) => {
      this.initTableData(response.operations);
      this.deploymentDetails = response;

      const historyObj = Object.values(history.state);
      historyObj.length > 1 ? this.targetHostNameHistory(historyObj) : this.targetHostNameUnique(response.operations);
    });
  }

  private initTableData(data: Array<DatabaseOperationsHistoryDetails>) {
    const deploymentData: Array<DatabaseOperationsHistoryDetails> = [];

    data.forEach((item) => {
      const data: DatabaseOperationsHistoryDetails = Object.create(item);

      data.operation_type = item.operation_type;
      data.started_at = item.started_at;
      data.completed_at = item.completed_at;
      // @ts-ignore
      data.duration = formatMillisecondsToTime(new Date(item.completed_at) - new Date(item.started_at));
      data.bms = item.bms;

      deploymentData.push(data);
    });

    this.initDataSource(deploymentData);
  }

  private targetHostNameHistory(history: any[]): void {
    const hostNames = history.reduce((acc, item) => {
      if (typeof item === 'number') {
        return acc;
      }
      acc.push(item.bms_name);
      return acc;
    }, []);

    this.targetHostname = hostNames.join(', ');
  }

  private targetHostNameUnique(operations: DatabaseOperationsHistoryDetails[]): void {
    const hostNames: string[] = [];
    operations.forEach((operation) => {
      operation.bms.forEach(item => {
        if (!hostNames.includes(item.name)) {
          hostNames.push(item.name);
        }
      });
    });

    this.targetHostname = hostNames.join(', ');
  }
}
