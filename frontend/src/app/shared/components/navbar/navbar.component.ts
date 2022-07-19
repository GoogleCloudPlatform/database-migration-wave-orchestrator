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

import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Location } from '@angular/common';
import { FormControl } from '@angular/forms';
import { Event, NavigationEnd, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { filter, map, startWith } from 'rxjs/operators';


@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})

export class NavbarComponent implements OnInit {
  @Output() sideMenuToggle = new EventEmitter<boolean>();
  isMigrationRoadmapPage = false;

  myControl = new FormControl();
  options: string[] = [
    'search result 1',
    'search result 2',
    'search result 3',
    'search result 4',
    'search result 5',
  ];
  filteredOptions: Observable<string[]> | undefined;

  constructor(private readonly router: Router, private location: Location) {}

  ngOnInit(): void {
    this.filteredOptions = this.myControl.valueChanges.pipe(
      startWith(''),
      map(value => this._filter(value)),
    );
    this.checkIsMigrationRoadmapPage();
  }

  redirectToRoadmap(): void {
    this.router.navigateByUrl('mymigrationprojects/roadmap');
  }

  toggleSideMenu() {
    const newValue = localStorage.getItem('sidebar-state') === 'collapsed' ? 'expanded' : 'collapsed';
    localStorage.setItem('sidebar-state', newValue);
    this.sideMenuToggle.emit();
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();
    return this.options.filter(option => option.toLowerCase().includes(filterValue));
  }

  private checkIsMigrationRoadmapPage() {
    this.isMigrationRoadmapPage = this.location.path() === '/mymigrationprojects/roadmap';

    this.router.events
      .pipe(filter((e: Event): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe((value) => {
        this.isMigrationRoadmapPage = value.urlAfterRedirects.startsWith('/mymigrationprojects/roadmap');
      }
    );
  }
}
