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

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from "@angular/forms";

import { MatIconModule } from "@angular/material/icon";
import { MatButtonModule } from "@angular/material/button";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatInputModule } from "@angular/material/input";
import { MatTableModule } from "@angular/material/table";
import { MatSortModule } from "@angular/material/sort";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatListModule } from "@angular/material/list";
import { MatTooltipModule } from '@angular/material/tooltip';

import { SharedModule } from '@app-shared/shared.module';

import { DeploymentHistoryRoutingModule } from './deployment-history-routing.module';

import { DeploymentHistoryComponent } from './components/deployment-history/deployment-history.component';
import { DeploymentDetailsComponent } from "./components/deployment-details/deployment-details.component";
import { DeploymentDetailsSidebarComponent } from "./components/deployment-details-sidebar/deployment-details-sidebar.component";

@NgModule({
  declarations: [
    DeploymentDetailsComponent,
    DeploymentDetailsSidebarComponent,
    DeploymentHistoryComponent,
  ],
  exports: [
    DeploymentDetailsSidebarComponent
  ],
  imports: [
    CommonModule,
    MatCheckboxModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MatSnackBarModule,
    MatTooltipModule,
    FormsModule,
    DeploymentHistoryRoutingModule,
    SharedModule,
  ]
})
export class DeploymentHistoryModule { }
