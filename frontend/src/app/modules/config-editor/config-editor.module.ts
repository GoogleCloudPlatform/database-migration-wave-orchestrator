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

import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

import { MatButtonModule } from "@angular/material/button";
import { MatInputModule } from "@angular/material/input";
import { MatIconModule } from "@angular/material/icon";
import { MatListModule } from "@angular/material/list";
import { MatSlideToggleModule } from "@angular/material/slide-toggle";
import { MatSelectModule } from "@angular/material/select";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { SharedModule } from '@app-shared/shared.module';
import { IConfig, NgxMaskModule } from "ngx-mask";

import { ConfigeditorRoutingModule } from "./config-editor-routing.module";

import { ConfigEditorComponent } from "./components/config-editor/config-editor.component";
import { ConfigEditorTooltipComponent } from "./components/config-editor-tooltip/config-editor-tooltip.component";
import { ConfigEditorTooltipDirective } from "./components/config-editor-tooltip/config-editor-tooltip.directive";


const maskConfig: Partial<IConfig> = {
  validation: false,
};

@NgModule({
  declarations: [
    ConfigEditorComponent,
    ConfigEditorTooltipComponent,
    ConfigEditorTooltipDirective
  ],
  exports: [],
  imports: [
    CommonModule,
    ConfigeditorRoutingModule,
    MatButtonModule,
    MatInputModule,
    MatIconModule,
    MatListModule,
    MatAutocompleteModule,
    FormsModule,
    MatSlideToggleModule,
    MatSelectModule,
    MatTooltipModule,
    MatCheckboxModule,
    ReactiveFormsModule,
    SharedModule,
    NgxMaskModule.forRoot(maskConfig),
  ]
})
export class ConfigeditorModule { }
