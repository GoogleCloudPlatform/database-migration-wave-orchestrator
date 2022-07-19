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

import { Component, OnInit, OnDestroy } from '@angular/core';
import { Router } from "@angular/router";
import { Subscription } from "rxjs";

import { Migration } from "@app-interfaces/migration";

import { MigrationService } from "@app-services/migration/migration.service";

@Component({
  selector: 'app-migrations',
  templateUrl: './migrations.component.html',
  styleUrls: ['./migrations.component.scss']
})
export class MigrationsComponent implements OnInit, OnDestroy {
  private projectListSubscription!: Subscription;

  constructor(
    private route: Router,
    private readonly migrationService: MigrationService,
  ) {}

  ngOnInit(): void {
    this.projectListSubscription = this.migrationService.projectList().subscribe((projectList: Migration) => {
      if (projectList.data && projectList.data.length) {
        this.route.navigateByUrl('/mymigrationprojects/list');
      }
    });
  }

  ngOnDestroy(): void {
    this.projectListSubscription.unsubscribe();
  }

  redirect(option: string) {
    this.route.navigateByUrl(`/${option}`);
  }
}
