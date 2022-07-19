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

import { HttpClient } from "@angular/common/http";
import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { ComponentFixture, flush, TestBed } from "@angular/core/testing";
import { FormBuilder, FormsModule, ReactiveFormsModule } from "@angular/forms";
import { MatDialog, MatDialogModule } from "@angular/material/dialog";
import { By } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { RouterTestingModule } from "@angular/router/testing";

import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatSnackBarModule } from "@angular/material/snack-bar";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { MatRippleModule } from '@angular/material/core';

import { MockMigrationService } from "@app-services/migration/mock-migration.service.spec";
import { MockUtilService } from "@app-services/util/mock-util-service.spec";
import { UtilService } from "@app-services/util/util.service";
import { MigrationService } from "@app-services/migration/migration.service";

import { NotificationComponent } from "@app-shared/components/notification/notification.component";

import { CreateMigrationComponent } from "./create-migration.component";


describe("CreateMigrationComponent", () => {
  let component: CreateMigrationComponent;
  let fixture: ComponentFixture<CreateMigrationComponent>;
  const mockUtilService: UtilService = new MockUtilService() as UtilService;
  const mockMigrationService:  MigrationService = new MockMigrationService as MigrationService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        FormsModule,
        ReactiveFormsModule,
        MatInputModule,
        MatSelectModule,
        MatSnackBarModule,
        MatDialogModule,
        MatAutocompleteModule,
        MatRippleModule,
        BrowserAnimationsModule,
        RouterTestingModule.withRoutes([
          {path: "softwarelibrary",
          loadChildren: () => import(`../../../software-library/software-library.module`).then(module => module.SoftwareLibraryModule)}
        ])
      ],
      declarations: [CreateMigrationComponent, NotificationComponent],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      providers: [
        { provide: UtilService, useValue: mockUtilService },
        { provide: MigrationService, useValue: mockMigrationService},
        { provide: HttpClient, useValue: null },
        { provide: MatDialog, useValue: null },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateMigrationComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });


  function goToIssuesBtnClick() {
    const goToIssuesButton = fixture.debugElement.query(
      (debugEl) =>
        debugEl.name === "button" &&
        debugEl.nativeElement.textContent === "GO TO ISSUE(S)"
    );
    goToIssuesButton.nativeElement.click();
    fixture.detectChanges();
  }

    it("should focus on name field if all required fields are not filled",() => {
      const createMIgrationButton = fixture.debugElement.query(By.css("button")).nativeElement;
      createMIgrationButton.click();
      fixture.detectChanges();
      goToIssuesBtnClick();

      const nameInput = fixture.debugElement.query(By.css('input[formControlName=name]')).nativeElement;
      const focusElement = document.activeElement;
      expect(focusElement).toEqual(nameInput);
  });

  it("should focus on vpc field if name field is filled correctly",() => {
      const form = component.migrationForm;
      form.controls['name'].setValue("my project name");
      fixture.detectChanges();

      const createMIgrationButton = fixture.debugElement.query(By.css("button")).nativeElement;
      createMIgrationButton.click();
      fixture.detectChanges();
      goToIssuesBtnClick();

      const vpcSelect = fixture.debugElement.query(By.css('[formControlName=vpc]')).nativeElement;
      const focusElement = document.activeElement;
      expect(focusElement).toBe(vpcSelect);
  });
});
