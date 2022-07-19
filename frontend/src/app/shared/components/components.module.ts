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

import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgModule } from '@angular/core';
import { ClipboardModule } from '@angular/cdk/clipboard';

import { MatPaginatorIntl } from '@angular/material/paginator';
import { MatIconModule } from "@angular/material/icon";
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSelectModule } from "@angular/material/select";
import { MatInputModule } from "@angular/material/input";
import { MatNativeDateModule } from '@angular/material/core';
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatDividerModule } from '@angular/material/divider';
import { MatButtonModule } from "@angular/material/button";
import { MatRippleModule } from '@angular/material/core';
import { MatDialogModule } from "@angular/material/dialog";
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatChipsModule } from '@angular/material/chips';

import { BaseMaterialTableComponent } from "./base-material-table/base-material-table.component";
import { BannerComponent } from "./banner/banner.component";
import { CustomPaginatorIntl } from "./base-material-table/custom-paginator.service";
import { ConfigEditorSidebarComponent } from './config-editor-sidebar/config-editor-sidebar.component';
import { CodeClipboardComponent } from './code-clipboard/code-clipboard.component';
import { DateTimeComponent } from './date-time/date-time.component';
import { ManageLabelsComponent } from './manage-labels/manage-labels.component';
import { LabelComponent } from './label/label.component';

@NgModule({
  declarations: [
    // Components
    BaseMaterialTableComponent,
    BannerComponent,
    ConfigEditorSidebarComponent,
    CodeClipboardComponent,
    DateTimeComponent,
    ManageLabelsComponent,
    LabelComponent
  ],
  imports: [
    // Angular Modules
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    // External Modules
    ClipboardModule,
    // Material
    MatFormFieldModule,
    MatIconModule,
    ClipboardModule,
    MatTooltipModule,
    MatDatepickerModule,
    MatSelectModule,
    MatNativeDateModule,
    MatInputModule,
    MatDividerModule,
    MatAutocompleteModule,
    MatButtonModule,
    MatRippleModule,
    MatDialogModule,
    MatChipsModule
  ],
  exports: [
    // Components
    BaseMaterialTableComponent,
    BannerComponent,
    ConfigEditorSidebarComponent,
    CodeClipboardComponent,
    DateTimeComponent,
    ManageLabelsComponent,
    LabelComponent
  ],
  providers: [
    {
      provide: MatPaginatorIntl,
      useClass: CustomPaginatorIntl
    }
  ],
})
export class SharedComponentsModule {}
