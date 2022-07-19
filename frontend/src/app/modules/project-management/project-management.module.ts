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
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";
import { MatButtonModule } from "@angular/material/button";
import { MatSidenavModule } from "@angular/material/sidenav";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatSelectModule } from "@angular/material/select";
import { MatOptionModule } from "@angular/material/core";
import { MatInputModule } from "@angular/material/input";
import { MatExpansionModule } from "@angular/material/expansion";
import { MatMenuModule } from "@angular/material/menu";
import { MatListModule } from "@angular/material/list";
import { MatAutocompleteModule } from "@angular/material/autocomplete";

import { DeploymentHistoryModule } from "../deployment-history/deployment-history.module";
import { MigrationsModule } from "../migrations/migrations.module";
import { ProjectManagementRoutingModule } from './project-management-routing.module';
import { MigrationWaveManagerModule } from "../migration-wave-manager/migration-wave-manager.module";
import { ConfigeditorModule } from "../config-editor/config-editor.module";
import { SharedModule } from '@app-shared/shared.module';

import { NavbarComponent } from '@app-shared/components/navbar/navbar.component';
import { SideMenuComponent } from '@app-shared/components/side-menu/side-menu.component';
import { InitialPageComponent } from './components/initial-page/initial-page.component';

@NgModule({
  declarations: [
    NavbarComponent,
    SideMenuComponent,
    InitialPageComponent,
  ],
  imports: [
    CommonModule,
    ProjectManagementRoutingModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatSidenavModule,
    MatFormFieldModule,
    MatSelectModule,
    MatOptionModule,
    MatInputModule,
    MatExpansionModule,
    MatMenuModule,
    MatListModule,
    ReactiveFormsModule,
    MatAutocompleteModule,
    FormsModule,
    DeploymentHistoryModule,
    MigrationsModule,
    MigrationWaveManagerModule,
    ConfigeditorModule,
    SharedModule,
  ]
})
export class ProjectManagementModule { }
