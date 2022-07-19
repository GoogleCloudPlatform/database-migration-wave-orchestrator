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

import { Component, ChangeDetectionStrategy, Input } from "@angular/core";
import { animate, style, transition, trigger, keyframes } from "@angular/animations";
@Component({
  templateUrl: "./config-editor-tooltip.component.html",
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [
    trigger("tooltip", [
      transition(":enter", [
        style({ transform: "scale(1)" }),
        animate(
          "200ms cubic-bezier(0, 0, 0.2, 1)",
          keyframes([
            style({opacity: 0, transform: "scale(0)", offset: 0}),
            style({opacity: 0.5, transform: "scale(0.99)", offset: 0.5}),
            style({opacity: 1, transform: "scale(1)", offset: 1}),
          ]),
        ),
      ]),
      transition(":leave", [
        animate("100ms cubic-bezier(0, 0, 0.2, 1)"), style({ transform: "scale(0)"}),
      ]),
    ]),
  ],
})
export class ConfigEditorTooltipComponent {
  @Input() description = "";
}
