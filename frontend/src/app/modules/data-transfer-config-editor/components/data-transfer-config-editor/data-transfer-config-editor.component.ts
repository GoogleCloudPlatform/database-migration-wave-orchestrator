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

import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";

import { Mapping } from "@app-interfaces/mapping";

import { MappingService } from "@app-services/migration-mapper/mapping.service";
import { UtilService } from "@app-services/util/util.service";

@Component({
  selector: 'app-data-transfer-config-editor',
  templateUrl: './data-transfer-config-editor.component.html',
  styleUrls: ['./data-transfer-config-editor.component.scss']
})

export class DataTransferConfigEditorComponent implements OnInit{
  mappings: Mapping | undefined;
  public hideIntro: boolean = true;
  private currentProjectId!: number;

  constructor(
    private utilService: UtilService,
    private mappingService: MappingService,
    private activatedRoute: ActivatedRoute) {}

  ngOnInit(): void {
    this.hideIntro = !!localStorage.getItem('hideBackupPreparationPage');

    if (this.utilService.getCurrentProjectId() != null) {
      this.currentProjectId = this.utilService.getCurrentProjectId();
    }
    this.activatedRoute.queryParams.subscribe((params) => {
      this.mappingService.getMappingsByDbId(params.databaseId).subscribe((resp) => {
        if (resp.data){
          this.mappings = resp.data[0];
        }});
      });
  }

  backupPreparationPageChanged($event: boolean): void {
    this.hideIntro = $event;
  }
}
