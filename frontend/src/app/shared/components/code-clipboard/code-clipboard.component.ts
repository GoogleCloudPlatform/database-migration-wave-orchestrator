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

import { Component, Input, OnInit } from '@angular/core';

import { MatSnackBar } from '@angular/material/snack-bar';


@Component({
  selector: 'app-code-clipboard',
  templateUrl: './code-clipboard.component.html'
})
export class CodeClipboardComponent implements OnInit {
  @Input() text = '';
  @Input() accent: string[] = [];
  modifiedText!: string;

  constructor(private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.checkAccentText();
  }

  checkAccentText(): void {
    if (this.accent.length) {
      const REG_EX = new RegExp(this.accent.join('|').replace(/\$/g, '\\$'), 'gi');
      this.modifiedText = this.text.replace(REG_EX, (x) => '<span class="accent">' + x + '</span>');
    } else {
      this.modifiedText = this.text;
    }
  }

  copyText(): void {
    this.snackBar.open('Copied to clipboard', 'Close', {
      duration: 3000,
    });
  }
}