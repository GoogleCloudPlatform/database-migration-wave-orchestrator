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
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatTabsModule } from '@angular/material/tabs';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MAT_TABS_CONFIG } from '@angular/material/tabs';
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatSortModule } from "@angular/material/sort";
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from "@angular/material/divider";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatStepperModule } from '@angular/material/stepper';
import { MatSelectModule } from '@angular/material/select';

import { MigrationWaveManagerRoutingModule } from './migration-wave-manager-routing.module';
import { SharedModule } from '@app-shared/shared.module';

import { CreateMigrationWaveComponent } from '@app-modules/migration-wave-manager/components/create-migration-wave/create-migration-wave.component';
import { ViewMigrationWaveComponent } from '@app-modules/migration-wave-manager/components/view-migration-wave/view-migration-wave.component';
import { MigrationWaveHistoryComponent } from '@app-modules/migration-wave-manager/components/migration-wave-history/migration-wave-history.component';
import { MigrationWaveManagerComponent } from './components/migration-wave-manager/migration-wave-manager.component';
import { MigrationWaveHistorySidebarComponent } from "./components/migration-wave-history-sidebar/migration-wave-history-sidebar.component";
import { MigrationStepProgressComponent } from './components/migration-step-progress/migration-step-progress.component';
import { MigrationWaveChartComponent } from './components/migration-wave-chart/migration-wave-chart.component';


@NgModule({
  declarations: [
    MigrationWaveManagerComponent,
    CreateMigrationWaveComponent,
    ViewMigrationWaveComponent,
    MigrationWaveHistoryComponent,
    MigrationWaveHistorySidebarComponent,
    MigrationStepProgressComponent,
    MigrationWaveChartComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    ReactiveFormsModule,
    MatAutocompleteModule,
    MatSnackBarModule,
    MatTabsModule,
    MatIconModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatProgressSpinnerModule,
    MatTooltipModule,
    MigrationWaveManagerRoutingModule,
    MatDividerModule,
    MatCheckboxModule,
    MatStepperModule,
    SharedModule
  ],
  exports: [
    MigrationWaveHistorySidebarComponent,
    CreateMigrationWaveComponent
  ],
  providers: [
    {provide: MAT_TABS_CONFIG, useValue: {animationDuration: '0ms'}}
  ]
})
export class MigrationWaveManagerModule { }
