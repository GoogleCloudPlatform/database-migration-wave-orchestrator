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

import { Component, OnInit, Input, OnChanges, SimpleChanges, EventEmitter, Output } from '@angular/core';
import { FormControl, FormGroup, FormBuilder, Validators } from "@angular/forms";
import { MatSelectChange } from '@angular/material/select';

import { FormateDateService } from '@app-services/formate-date/formate-date.service';

import { ChangeDateTime } from "@app-interfaces/date-time";

@Component({
  selector: 'app-date-time',
  templateUrl: './date-time.component.html',
  styleUrls: ['./date-time.component.scss']
})
export class DateTimeComponent implements OnInit, OnChanges {
  timeList!: string[];
  form!: FormGroup;
  minDate = new Date();
  maxDate = new Date();
  minTime = '0:00';
  time: string = '';
  day: string = '';
  @Input() dateTime = '';
  @Output() changeDateTime = new EventEmitter<ChangeDateTime>();

  constructor(
    private formBuilder: FormBuilder,
    private formateDateService: FormateDateService,
  ) {
    this.form = this.formBuilder.group({
      date: new FormControl(this.day, [Validators.required]),
      time: new FormControl(this.time, [Validators.required])
    });
  }

  ngOnInit(): void {
    this.generateTimeList();
    this.setMaxDate();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.dateTime) {
      const scheduleTime = changes.dateTime?.currentValue;

      this.time = this.formateDateService.convert24hourTo12HourFormat(this.formateDateService.getTime(scheduleTime));
      this.day = scheduleTime;

      this.form?.get('date')?.setValue(new Date(this.day));
      this.form?.get('time')?.setValue(this.time);

      const date = new Date(this.form.get('date')?.value.getFullYear(), this.form.get('date')?.value.getMonth(), this.form.get('date')?.value.getDate());
      if(this.isToday(date)) {
        this.setMinTime();
      }       
      this.generateTimeList();
    }
  }

  onDateChange($event: any): void {
    this.minTime = '0:00';
    if(this.isToday($event.value)) {
      this.form?.get('time')?.setValue('');
    } 
    this.changeDateTime.emit({
      isValidForm: this.form.valid,
      dateTime: this.formateDateService.formateDate({
        date: $event.value,
        time: this.form.get('time')?.value
      })
    });
  }

  onTimeChange($event: MatSelectChange): void {
    this.changeDateTime.emit({
      isValidForm: this.form.valid,
      dateTime: this.formateDateService.formateDate({
        date: this.form.get('date')?.value,
        time: $event.value
      })
    });
  }

  private isToday(date: Date) {
    return new Date(this.minDate.getFullYear(), this.minDate.getMonth(), this.minDate.getDate()).getTime() === date.getTime()
  }

  private setMinTime(): void {    
    this.minTime = this.minDate.getHours() + ':' + this.minDate.getMinutes();
  }

  private setMaxDate(): void {
    const date = new Date();
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = date.getDate();
    const hour = date.getHours();

    this.maxDate = new Date(year, month, day, hour + 720);
  }

  private generateTimeList(): void {
    const periods = ['AM', 'PM'];
    const hours = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
    const minutes = ["00", 15, 30, 45 ];

    let timeObj: any = this.add([{}], "p", periods);
    timeObj = this.add(timeObj, "h", hours);
    timeObj = this.add(timeObj, "m", minutes);

    const times: string[] = [];
    for (let t of timeObj) {
      times.push(t.h + ':' + t.m + ' ' + t.p);
    }

    this.timeList = times;
    this.timeList = this.timeList.filter(i => {  
      return this.formateDateService.isTimeBigger(this.formateDateService.convert12HourTo24hourFormat(i), this.minTime)
    });
  }

  private add(tab: any, prop: string, val: any[]): string[] {
    const result = [];

    for (let t of tab) {
      for (let v of val) {
        let tc = { ...t };

        tc[prop] = v;
        result.push(tc);
      }
    }

    return result;
  }
}
