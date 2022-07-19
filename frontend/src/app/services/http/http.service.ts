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
import { throwError } from 'rxjs';
import { HttpClient, HttpErrorResponse, HttpHeaders } from "@angular/common/http";

import { environment } from "../../../environments/environment";

@Injectable({
  providedIn: 'root'
})
export class HttpService {
  protected apiURL: string;

  constructor(protected http: HttpClient ) {
    this.apiURL = environment.apiURL + '/api';
  }

  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    }),
  }

  httpOptionsFD = {
    headers: new HttpHeaders({
      'Access-Control-Allow-Origin': '*'
    }),
  }

  handleError(error: HttpErrorResponse) {
    let errorMessage;
    if(error.error instanceof ErrorEvent) {
      // Get client-side error
      errorMessage = error.error.message;
    } else {
      // Get server-side error
      errorMessage = error.status === 500 ? 'Something is wrong' :
      error.error.errors
        ? Object.values(error.error.errors)
        : `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    return throwError(errorMessage);
  }
}
