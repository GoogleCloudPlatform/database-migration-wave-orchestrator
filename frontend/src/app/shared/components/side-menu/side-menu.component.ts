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

import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { MatDrawer } from '@angular/material/sidenav';
import { Event, NavigationEnd, Router } from '@angular/router';
import { filter } from "rxjs/operators";
import { Subscription } from "rxjs";

import { Migration } from '@app-interfaces/migration';

import { MigrationService } from '@app-services/migration/migration.service';
import { UtilService } from "@app-services/util/util.service";

@Component({
  selector: 'app-side-menu',
  templateUrl: './side-menu.component.html',
  styleUrls: ['./side-menu.component.scss']
})
export class SideMenuComponent implements OnInit, OnDestroy {
  private projectListSubscription!: Subscription;
  routeUrl?: string;
  isCreateMigrationPage = false;
  isConfigEditorPage = false;
  isDataTransferConfigEditorPage = false;
  isDeploymentDetailsPage = false;
  isMigrationRoadmapPage = false;
  isMigrationListPage = false;
  isMigrationWaveHistoryPage = false;
  projectList!: Migration[];
  shouldShowSidebar: boolean = localStorage.getItem('sidebar-state') ?
  localStorage.getItem('sidebar-state') === 'expanded' : true;

  @ViewChild('drawer', { static: true }) public drawer!: MatDrawer;

  readonly projectLinks = [
    { name: 'Migration Projects', href: 'mymigrationprojects/list'},

    { name: 'Software Library', href: 'softwarelibrary'},
    { name: 'Source Databases Inventory', href: 'sourcedatabases'},
    { name: 'Target (BMS) inventory', href: 'inventorymanager'},
    { name: 'Migration Mapper', href: 'migrationmapper'},
    { name: 'Migration Wave Manager', href: 'migrationwavemanager'},
    { name: 'Data Transfer Manager', href: 'datatransfermanager'},
    { name: 'Deployment History', href: 'deploymenthistory'}
  ];

  constructor(
    private router: Router,
    private migrationService: MigrationService,
    public utilService: UtilService) {
    window.addEventListener("storage", () => {
      this.getName();
    });
    this.initRouteListener();
  }

  ngOnInit(): void {
    this.projectListSubscription = this.migrationService.projectList().subscribe((projectList: Migration) => {
      if (!projectList.data) return;

      this.projectList = projectList.data.sort((a, b) => a.name.localeCompare(b.name));
      this.getName();
    });

    this.migrationService.getAndStoreMigrationsProjects();
  }

  ngOnDestroy(): void {
    this.projectListSubscription.unsubscribe();
  }

  getName(){
    let currentLsId = Number(localStorage.getItem('currentProjectId'));
    if (this.projectList) {
      const project = this.projectList.filter( element => element.id === currentLsId)[0];
      if (project)
        this.utilService.currentProjectName = project.name;
    }
  }

  openMenu(){
    this.drawer.toggle();
  }

  private initRouteListener() {
    this.router.events
      .pipe(filter((e: Event): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((value) => {
        this.routeUrl = value.urlAfterRedirects;
        this.isCreateMigrationPage = value.urlAfterRedirects.startsWith('/mymigrationprojects/create');
        this.isDeploymentDetailsPage = value.urlAfterRedirects.startsWith('/deploymenthistory/details');
        this.isMigrationRoadmapPage = value.urlAfterRedirects.startsWith('/mymigrationprojects/roadmap');
        this.isMigrationWaveHistoryPage = value.urlAfterRedirects.startsWith('/migrationwavemanager/history');
        this.isConfigEditorPage = value.urlAfterRedirects.startsWith('/configeditor');
        this.isDataTransferConfigEditorPage = value.urlAfterRedirects.startsWith('/datatransferconfigeditor');
        this.isMigrationListPage = value.urlAfterRedirects.startsWith('/mymigrationprojects/list');
      });
  }
}
