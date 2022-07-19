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

import { TestBed, ComponentFixture, fakeAsync, flush } from "@angular/core/testing";
import { Component, DebugElement} from "@angular/core";
import { BrowserDynamicTestingModule } from "@angular/platform-browser-dynamic/testing";
import { By } from "@angular/platform-browser";
import { Overlay, OverlayModule, OverlayRef } from "@angular/cdk/overlay";
import { ComponentPortal} from "@angular/cdk/portal";
import { Observable } from "rxjs";

import { ConfigEditorTooltipDirective } from "./config-editor-tooltip.directive";
import { ConfigEditorTooltipComponent } from "./config-editor-tooltip.component";


@Component({
    template:`<span appTooltip="ntp-preferred"></span>`
})
export class TestTooltipComponent{}

describe("Directive: ConfigEditorTooltipDirective",() =>{
    let component: TestTooltipComponent;
    let fixture: ComponentFixture<TestTooltipComponent>;
    let spanEl: DebugElement;
    let overlayService: Overlay;
    let createSpy: jasmine.Spy;
    let overlayRefSpyObj: OverlayRef;

    beforeEach(async() => {
        TestBed.configureTestingModule({
            declarations:[ConfigEditorTooltipDirective,ConfigEditorTooltipComponent, TestTooltipComponent],
            imports:[OverlayModule]
        })
        .overrideModule(BrowserDynamicTestingModule, { set: { entryComponents: [ConfigEditorTooltipComponent] } })
        .compileComponents();

        fixture = TestBed.createComponent(TestTooltipComponent);
        component = fixture.componentInstance;
        spanEl = fixture.debugElement.query(By.css("span"));
        overlayService = TestBed.inject(Overlay);

        ({createSpy, overlayRefSpyObj} = overlaySpyHelper(overlayService));
    });

    afterEach(() => {
        fixture.destroy();
      });

    function whenUiIsStabilized() {
     fixture.detectChanges();
     flush();
     }

    function overlaySpyHelper(overlayService: Overlay) {
        const overlayRefSpyObj = jasmine.createSpyObj({
          attach: new ComponentPortal(ConfigEditorTooltipComponent),
          backdropClick: jasmine.createSpyObj({subscribe: null}),
          detach: null,
          detachments: new Observable()
        });
        const createSpy = spyOn(overlayService, "create").and.returnValue(overlayRefSpyObj);
        return {createSpy, overlayRefSpyObj};
      }

    it("should create overlay", fakeAsync(() => {
        whenUiIsStabilized();

        spanEl.triggerEventHandler("mouseenter", null);
        fixture.detectChanges();
        expect(createSpy).toHaveBeenCalled();
    }));

    it("should show tooltip after hovering the element and hide after hover out", fakeAsync(() => {
        whenUiIsStabilized();
        spanEl.triggerEventHandler("mouseenter", null);
        fixture.detectChanges();
        expect(overlayRefSpyObj.attach).toHaveBeenCalled();

        spanEl.triggerEventHandler("mouseout", null);
        expect(overlayRefSpyObj.detach).toHaveBeenCalled();
    }));
});
