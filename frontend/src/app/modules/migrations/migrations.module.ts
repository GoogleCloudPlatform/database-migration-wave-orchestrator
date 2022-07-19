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

import { CUSTOM_ELEMENTS_SCHEMA, NgModule, InjectionToken } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatFormFieldModule, MAT_FORM_FIELD_DEFAULT_OPTIONS } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatStepperModule } from "@angular/material/stepper";
import { MatDialogModule } from "@angular/material/dialog";
import { MatTableModule } from "@angular/material/table";
import { MatSortModule } from "@angular/material/sort";
import { MatPaginatorModule } from "@angular/material/paginator";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatMenuModule } from "@angular/material/menu";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatRadioModule } from "@angular/material/radio";
import { MatDividerModule } from "@angular/material/divider";
import { MatAutocompleteModule } from '@angular/material/autocomplete';

import { NotificationComponent } from "@app-shared/components/notification/notification.component";
import { ConfirmDialogComponent } from "@app-shared/components/confirm-dialog/confirm-dialog.component";

import { MigrationsRoutingModule } from './migrations-routing.module';
import { SharedModule } from '@app-shared/shared.module';

import { CreateMigrationComponent } from "./components/create-migration/create-migration.component";
import { MigrationListingComponent } from "./components/migration-listing/migration-listing.component";
import { MigrationRoadmapSidebarComponent } from "./components/migration-roadmap-sidebar/migration-roadmap-sidebar.component";
import { MigrationRoadmapComponent } from "./components/migration-roadmap/migration-roadmap.component";
import { MigrationsComponent } from './components/migrations/migrations.component';
import { MigrationListingSidebarComponent } from "./components/migration-listing-sidebar/migration-listing-sidebar.component";
import { HighlightPipe } from '@app-shared/components/highlight/highlight.pipe';

@NgModule({
  declarations: [
    MigrationsComponent,
    CreateMigrationComponent,
    MigrationRoadmapComponent,
    MigrationRoadmapSidebarComponent,
    NotificationComponent,
    ConfirmDialogComponent,
    MigrationListingComponent,
    MigrationListingSidebarComponent,
    HighlightPipe
  ],
  imports: [
    CommonModule,
    MigrationsRoutingModule,
    MatButtonModule,
    MatIconModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatStepperModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MatCheckboxModule,
    MatMenuModule,
    MatSnackBarModule,
    MatTooltipModule,
    MatRadioModule,
    MatDividerModule,
    MatAutocompleteModule,
    SharedModule
  ],
  exports: [
    MigrationRoadmapSidebarComponent,
    MigrationListingSidebarComponent
  ],
  providers: [
    {
      provide: MAT_FORM_FIELD_DEFAULT_OPTIONS,
      useValue: { appearance: 'none' }
    }
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class MigrationsModule { }
