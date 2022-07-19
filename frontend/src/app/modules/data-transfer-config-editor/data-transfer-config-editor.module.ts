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


import { SharedModule } from '@app-shared/shared.module';

import { MatButtonModule } from "@angular/material/button";
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

import { DataTransferConfigEditorComponent } from './components/data-transfer-config-editor/data-transfer-config-editor.component';
import { DataTransferConfigEditorRoutingModule } from './data-transfer-config-editor-routing.module';
import { DataTransferIntroComponent } from './components/data-transfer-intro/data-transfer-intro.component';
import { DataTransferRestoreParametersComponent } from './components/data-transfer-restore-parameters/data-transfer-restore-parameters.component';


@NgModule({
  declarations: [
    DataTransferConfigEditorComponent,
    DataTransferIntroComponent,
    DataTransferRestoreParametersComponent
  ],
  imports: [
    CommonModule,
    DataTransferConfigEditorRoutingModule,

    MatTooltipModule,
    MatIconModule,
    MatButtonModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
  
    FormsModule,
    ReactiveFormsModule,
    SharedModule
  ]
})
export class DataTransferConfigEditorModule { }
