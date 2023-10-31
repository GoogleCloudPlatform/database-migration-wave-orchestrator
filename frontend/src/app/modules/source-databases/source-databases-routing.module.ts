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
import { RouterModule, Routes } from '@angular/router';

import { SourceDatabasesComponent } from "./components/source-databases/source-databases.component";
import { MigvisorImportComponent } from './components/source-databases/migvisor-import/migvisor-import.component';
import { ManualEntryComponent } from './components/source-databases/manual-entry/manual-entry.component';

const routes: Routes = [
  { path: '' , component: SourceDatabasesComponent },
  { path: 'migvisor-import' , component: MigvisorImportComponent },
  { path: 'create' , component: ManualEntryComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SourceDatabasesRoutingModule { }
