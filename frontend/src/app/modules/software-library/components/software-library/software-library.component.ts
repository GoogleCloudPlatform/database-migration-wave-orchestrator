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

import { Component, OnInit } from '@angular/core';

import { SoftwareLibraryService } from "@app-services/softwarelibrary/softwarelibrary.service";

@Component({
  selector: 'app-software-library',
  templateUrl: './software-library.component.html',
  styleUrls: ['./software-library.component.scss']
})
export class SoftwareLibraryComponent implements OnInit {
  public uploadUrl?: string;

  constructor(private readonly softwareLibraryService: SoftwareLibraryService) { }

  ngOnInit(): void {
    this.softwareLibraryService.getUploadUrl().subscribe((response) => {
      this.uploadUrl = response.sw_lib_url.slice(0, response.sw_lib_url.indexOf('"'));
    });
  }
}
