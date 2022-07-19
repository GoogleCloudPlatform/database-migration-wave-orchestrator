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

import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Clipboard, ClipboardModule } from '@angular/cdk/clipboard';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { By } from '@angular/platform-browser';

import { MatSnackBarModule } from '@angular/material/snack-bar';

import { CodeClipboardComponent } from './code-clipboard.component';


describe('CodeClipboardComponent', () => {
  let component: CodeClipboardComponent;
  let fixture: ComponentFixture<CodeClipboardComponent>;
  let clipboard: Clipboard;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ClipboardModule, BrowserAnimationsModule, MatSnackBarModule],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [CodeClipboardComponent],
    })
    .compileComponents();
    fixture = TestBed.createComponent(CodeClipboardComponent);
    component = fixture.componentInstance;
    clipboard = TestBed.inject(Clipboard);

    fixture.detectChanges();
  });

  afterEach(() => {
    fixture.destroy();
  });

  it('should show text from the input', async () => {
    spyOn(component, 'checkAccentText').and.callThrough();
    component.text = 'test code';
    component.ngOnInit();
    fixture.detectChanges();

    const textRef = fixture.debugElement.query(By.css('pre')).nativeElement;

    await fixture.whenStable().then(() => {
      expect(textRef.textContent).toEqual('test code');
    })
  });

  it('should highlight accent text', async () => {
    spyOn(component, 'checkAccentText').and.callThrough();
    component.text = 'test code';
    component.accent = ['code'];
    component.ngOnInit();
    fixture.detectChanges();

    const accentTextRef = fixture.debugElement.query(By.css('pre span')).nativeElement;

    await fixture.whenStable().then(() => {
      expect(accentTextRef.textContent).toEqual('code');
      expect(accentTextRef.classList.value).toEqual('accent');
    })
  });

  it('should copy on click on the copy icon', async () => {
    spyOn(clipboard, 'copy');

    const copyIconRef = fixture.debugElement.query(By.css('mat-icon')).nativeElement;
    copyIconRef.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(clipboard.copy).toHaveBeenCalledTimes(1);
    })
  });

  it('should copy text from the input', async () => {
    spyOn(clipboard, 'copy');
    component.text = 'test code';
    fixture.detectChanges();

    const copyIconRef = fixture.debugElement.query(By.css('mat-icon')).nativeElement;
    copyIconRef.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(clipboard.copy).toHaveBeenCalledWith('test code');
    })
  });

  it('should show notification after the text is copied', async () => {
    spyOn(component, 'copyText').and.callThrough();
    component.text = 'test code';
    fixture.detectChanges();

    const copyIconRef = fixture.debugElement.query(By.css('mat-icon')).nativeElement;
    copyIconRef.click();
    fixture.detectChanges();

    await fixture.whenStable().then(() => {
      expect(component.copyText).toHaveBeenCalledTimes(1);
    })
  });
})


