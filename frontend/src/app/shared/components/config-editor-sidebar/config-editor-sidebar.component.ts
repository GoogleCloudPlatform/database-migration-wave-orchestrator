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

import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from "@angular/router";
import { Subscription } from "rxjs";

import { Mapping } from "@app-interfaces/mapping";

import { MappingService } from "@app-services/migration-mapper/mapping.service";

import { getDBType }  from "@app-shared/helpers/functions";
import { UtilService } from '@app-services/util/util.service';
import { SourceDb } from '@app-interfaces/sourceDb';
import { SourceDbService } from '@app-services/source-db/source-db.service';

@Component({
  selector: 'app-config-editor-sidebar',
  templateUrl: './config-editor-sidebar.component.html'
})
export class ConfigEditorSidebarComponent implements OnInit, OnDestroy {
  @Input() panelTitle: string = 'Config Editor';
  private routeSubscription!: Subscription;
  mappings!: Mapping;
  sourceDb!: SourceDb;
  dbType!: string;

  constructor(
    private readonly mappingService: MappingService,
    private readonly sourceDbService: SourceDbService,
    private utilService: UtilService,
    private readonly activatedRoute: ActivatedRoute) {}

  ngOnInit(): void {
    this.routeSubscription = this.activatedRoute.queryParams.subscribe((params) => {
      this.loadData(params.databaseId);
    });
  }

  ngOnDestroy() {
    this.routeSubscription.unsubscribe();
  }

  private loadData(databaseId: string): void {
    this.mappingService.getMappingsByDbId(databaseId).subscribe((response) => {
      if (!response.data) return;
      this.mappings = response.data[0];
      if (this.mappings) {
        this.dbType = getDBType(response.data[0].db_type);
      }
    });

    this.sourceDbService.getSourceDb(Number(databaseId)).subscribe(response => {
      if (!response) return;
      this.sourceDb = response;
    });
  }
  
  goBack(){
    this.utilService.goBack();
  }
}
