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

import { InitialPageComponent } from "./components/initial-page/initial-page.component";

import { CurrentProjectGuard } from "@app-guards/current-project/current-project.guard";

const routes: Routes = [
  { path : '' , component: InitialPageComponent, children: [
      {
        path: 'ui-kit',
        loadChildren: () => import(`../ui-kit/ui-kit.module`).then(module => module.UiKitModule),
        canActivate: []
      },
      {
        path:'mymigrationprojects',
        loadChildren: () => import(`../migrations/migrations.module`).then(module => module.MigrationsModule),
        canActivate: []
      },
      {
        path:'softwarelibrary',
        loadChildren: () => import(`../software-library/software-library.module`).then(module => module.SoftwareLibraryModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'sourcedatabases',
        loadChildren: () => import(`../source-databases/source-databases.module`).then(module => module.SourcedatabasesModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'inventorymanager',
        loadChildren: () => import(`../inventory-manager/inventorymanager.module`).then(module => module.InventorymanagerModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'migrationmapper',
        loadChildren: () => import(`../migration-mapper/migration-mapper.module`).then(module => module.MigrationMapperModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'migrationwavemanager',
        loadChildren: () => import(`../migration-wave-manager/migration-wave-manager.module`).then(module => module.MigrationWaveManagerModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'deploymenthistory',
        loadChildren: () => import(`../deployment-history/deployment-history.module`).then(module => module.DeploymentHistoryModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'configeditor',
        loadChildren: () => import(`../config-editor/config-editor.module`).then(module => module.ConfigeditorModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'datatransfermanager',
        loadChildren: () => import(`../data-transfer-manager/data-transfer-manager.module`).then(module => module.DataTransferManagerModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'datatransferconfigeditor',
        loadChildren: () => import(`../data-transfer-config-editor/data-transfer-config-editor.module`).then(module => module.DataTransferConfigEditorModule),
        canActivate: [CurrentProjectGuard]
      },
      {
        path:'**', redirectTo: 'mymigrationprojects/list', pathMatch: 'full'
      },
    ]
  },
  { path: '**', redirectTo: '', pathMatch: 'full' },
];

@NgModule({
  declarations: [],
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ProjectManagementRoutingModule { }
