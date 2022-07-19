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

@Injectable({
  providedIn: 'root'
})
export class FormateDateService {
  formateDate(inputDate: any): string {
    const date = new Date(inputDate.date);
    const day = date.getDate();
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const dateString = '' + year + '-' + month + '-' + day;
    const timeString = inputDate.time ? this.convert12HourTo24hourFormat(inputDate.time) : '';
    const combined = new Date(dateString + ' ' + timeString);

    return combined.toISOString();
  }

  getTime(inputDate: string): string {
    if (!inputDate) {
      return '';
    }
    const date = new Date(inputDate);
    let hours: any = date.getHours();
    let minutes: any = date.getMinutes();

    if (minutes === 0) {
      minutes = '0' + minutes;
    }

    return hours + ':' + minutes;
  }

  convert24hourTo12HourFormat(time: any): string {
    const time_part_array = time.split(":");
    let ampm = 'AM';

    if (time_part_array[0] >= 12) {
        ampm = 'PM';
    }
    if (time_part_array[0] > 12) {
        time_part_array[0] = time_part_array[0] - 12;
    }

    const formatted_time = time_part_array[0] + ':' + time_part_array[1] + ' ' + ampm;

    return formatted_time;
  }

  convert12HourTo24hourFormat(timeStr: string): string {
    const [time, modifier] = timeStr.split(' ');
    let [hours, minutes]: any = time.split(':');

    if (hours === '12') {
       hours = '00';
    }
    if (modifier === 'PM') {
       hours = parseInt(hours, 10) + 12;
    }

    return `${hours}:${minutes}`;
  };

  isTimeBigger(timeA: string, timeB: string): boolean {
    const [hA, mA] = timeA.split(':').map(i => Number(i));
    const [hB, mB]: any = timeB.split(':').map(i => Number(i));
    if ((hA > hB) || (hA === hB && mA > mB)) {
      return true;
    } 
    return false;
  }
}
