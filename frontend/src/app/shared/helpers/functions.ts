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

import { DB_Types } from "../../interfaces/mapping";
/**
 *  Returns formatted date to display on UI, example:
 *    - input: 'Wed, 08 Dec 2021 16:23:14 GMT'
 *    - output: 'Dec 8, 2021'.
 */
export function formatDate(date: string): string {
  const formattedDate = new Date(date);
  const monthName = formattedDate.toLocaleString('default', { month: 'short' });

  return `${monthName} ${formattedDate.getDate()}, ${formattedDate.getFullYear()}`;
}

/**
 * Returns time in readable format. Example:
 *   - input: 30000
 *   - output: 00:00:30.
 */
export function formatMillisecondsToTime(milliseconds: number): string {
  if(milliseconds < 0) {
    return '-'
  }
  let seconds: number|string = Math.floor((milliseconds / 1000) % 60);
  let minutes: number|string = Math.floor((milliseconds / (1000 * 60)) % 60);
  let hours: number|string = Math.floor((milliseconds / (1000 * 60 * 60)) % 24);

  hours = (hours < 10) ? '0' + hours : hours;
  minutes = (minutes < 10) ? '0' + minutes : minutes;
  seconds = (seconds < 10) ? '0' + seconds : seconds;

  return hours + ':' + minutes + ':' + seconds;
}

export function getDBType(value: string | undefined): string {
  if(!value) {
    return "";
  }
  const type =  Object.entries(DB_Types).find(([key,]) => key === value)?.[1];
  return type ?  type : "";
}
