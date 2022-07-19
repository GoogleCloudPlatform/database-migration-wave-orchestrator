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

import { Component, Output, EventEmitter } from "@angular/core";

@Component({
  selector: 'app-data-transfer-intro',
  templateUrl: './data-transfer-intro.component.html',
  styleUrls: ['./data-transfer-intro.component.scss']
})

export class DataTransferIntroComponent {
  hidePage = false;
  @Output() backupPreparationPageChanged = new EventEmitter<boolean>();

  constructor() {
    this.hidePage = !!localStorage.getItem('hideBackupPreparationPage');
  }

  readyBackup(): void {
    if (this.hidePage) {
      localStorage.setItem('hideBackupPreparationPage', 'true');
    } else {
      localStorage.removeItem('hideBackupPreparationPage');
    }

    this.backupPreparationPageChanged.emit(true);
  }
}
