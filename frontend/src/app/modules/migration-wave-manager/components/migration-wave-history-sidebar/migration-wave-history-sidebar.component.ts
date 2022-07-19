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
import { Subscription } from 'rxjs';

import { DatabaseOperationsHistoryResponse, DatabaseOperationsHistoryDetails } from '@app-interfaces/database-operations-history';

import { DeploymentHistoryService } from '@app-services/deployment-history/deployment-history.service';

@Component({
  selector: 'app-migration-wave-history-sidebar',
  templateUrl: './migration-wave-history-sidebar.component.html',
  styleUrls: ['./migration-wave-history-sidebar.component.scss']
})
export class MigrationWaveHistorySidebarComponent implements OnInit, OnDestroy {
  private deploymentDetailsSubscription!: Subscription;
  public deploymentDetails!: DatabaseOperationsHistoryResponse;
  public targetHostname: string = '';

  constructor(private deploymentHistoryService: DeploymentHistoryService) {}

  ngOnInit(): void {
    this.deploymentDetailsSubscription = this.deploymentHistoryService.databaseOperationHistory$.subscribe((response) => {
      this.deploymentDetails = response;

      const historyObj = Object.values(history.state);
      historyObj.length > 1 ? this.targetHostNameHistory(historyObj) : this.targetHostNameUnique(response.operations);
    })
  }

  ngOnDestroy() {
    this.deploymentDetailsSubscription.unsubscribe();
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
