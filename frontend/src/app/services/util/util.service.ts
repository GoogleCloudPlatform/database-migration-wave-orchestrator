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

import { Injectable } from '@angular/core';
import { Location } from "@angular/common";
import { HttpClient } from '@angular/common/http';
import { Observable } from "rxjs";
import { catchError, retry } from "rxjs/operators";

import { WaveStepsMeta } from '@app-interfaces/util';
import { MetadataSettings } from "@app-interfaces/metadata-settings";

import { HttpService } from '@app-services/http/http.service';

@Injectable({
  providedIn: 'root'
})
export class UtilService extends HttpService {
  private waveStepsMetaData!:WaveStepsMeta;

  currentProjectId: number | undefined;
  currentProjectName: string | undefined;

  constructor(private location: Location, protected http: HttpClient) {
    super(http);
    window.addEventListener("storage", () => {
      this.currentProjectId =  Number(localStorage.getItem('currentProjectId'));
    });
    this.getWaveStepsMetaData();
  }

  goBack(){
    this.location.back();
  }

  getCurrentProjectId() {
    this.currentProjectId =  Number(localStorage.getItem('currentProjectId'));
    return this.currentProjectId;
  }

  getWaveStepsMetaData():WaveStepsMeta  {
    if (!this.waveStepsMetaData) {
      this.http.get<WaveStepsMeta>(this.apiURL + `/metadata/wave-steps`, this.httpOptions).subscribe(resp => {
        this.waveStepsMetaData = resp;
      })

    }
    return this.waveStepsMetaData;
  }

  getMetadataSettings(): Observable<MetadataSettings> {
    return this.http.get<MetadataSettings>(this.apiURL + '/metadata/settings', this.httpOptions)
      .pipe(
        retry(1),
        catchError(this.handleError)
      )
  }
}
