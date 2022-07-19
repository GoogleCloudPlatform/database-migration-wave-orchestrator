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

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';

import { DataTransferManagerRoutingModule } from './data-transfer-manager-routing.module';

import { SharedModule } from '@app-shared/shared.module';

import { DataTransferManagerComponent } from './components/data-transfer-manager/data-transfer-manager.component';
import { MatDialogModule } from '@angular/material/dialog';
import { MatDividerModule } from '@angular/material/divider';
import { ScheduleRestoreComponent } from './components/schedule-restore/schedule-restore.component';
import { ErrorsDialogComponent } from './components/errors-dialog/errors-dialog.component';

@NgModule({
  declarations: [
    DataTransferManagerComponent,
    ScheduleRestoreComponent,
    ErrorsDialogComponent
  ],
  imports: [
    CommonModule,
    DataTransferManagerRoutingModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MatDialogModule,
    MatDividerModule,
    MatTooltipModule,
    MatMenuModule,
    SharedModule
  ]
})
export class DataTransferManagerModule { }

