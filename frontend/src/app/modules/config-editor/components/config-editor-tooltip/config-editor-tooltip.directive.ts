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

import { ComponentRef, Directive, ElementRef, HostListener, Input, OnInit, OnDestroy, Renderer2 } from "@angular/core";
import { Overlay, OverlayRef } from "@angular/cdk/overlay";
import { ComponentPortal } from "@angular/cdk/portal";
import { Subscription } from "rxjs";

import { ConfigEditorTooltipComponent } from "./config-editor-tooltip.component";

@Directive({ selector: "[appTooltip]" })
export class ConfigEditorTooltipDirective implements OnInit, OnDestroy {

  @Input() appTooltip = "";
  private overlayRef!: OverlayRef;
  private tooltipRef!: ComponentRef<ConfigEditorTooltipComponent>;
  private scrollSubcribtion!: Subscription;
  private isTooltipShown = false;
  private isTooltipClicked = false;
  private isTooltipHovered = false;

  constructor(private overlay: Overlay,
              private elementRef: ElementRef,
              private renderer: Renderer2) {
  }

  ngOnInit(): void {
    const positionStrategy = this.overlay.position().flexibleConnectedTo(this.elementRef).withPush(true).withDefaultOffsetX(0)
    .withPositions([{ originX: "end", originY: "center", overlayX: "start", overlayY: "center"},
      { originX: "center", originY: "bottom", overlayX: "center", overlayY: "top"},
      { originX: "start", originY: "center", overlayX: "end", overlayY: "center"}]);
     const scrollStrategy = this.overlay.scrollStrategies.close();

    this.overlayRef = this.overlay.create({ positionStrategy, scrollStrategy });

    this.scrollSubcribtion = this.overlayRef.detachments().subscribe( _ => {
      this.isTooltipShown = false;
      this.isTooltipClicked = false;
    });

    this.renderer.listen("window", "click", (e:Event) => {
     if(e.target !== this.elementRef.nativeElement) {
         this.closeTooltip();
     }
   });
  }

  ngOnDestroy(): void {
      this.scrollSubcribtion.unsubscribe();
  }

  @HostListener("click")
  showTooltipOnClick() {
    if(this.isTooltipClicked){
      this.closeTooltip();
      return;
    }
    if(!this.isTooltipClicked && this.isTooltipHovered){
      this.isTooltipClicked = true;
      if(!this.isTooltipShown){
        this.showTooltip();
      }
    }
  }


  @HostListener("mouseenter")
  show() {
    if(!this.isTooltipClicked){
      this.showTooltip();
      this.isTooltipHovered = true;
      this.isTooltipShown = true;
    }
  }

  @HostListener("mouseout")
  hide() {
    if(!this.isTooltipClicked){
      this.closeTooltip();
      this.isTooltipHovered = false;
    }
  }

  showTooltip(){
   this.tooltipRef = this.overlayRef.attach(new ComponentPortal(ConfigEditorTooltipComponent));
   if(this.tooltipRef.instance){
     this.tooltipRef.instance.description = this.appTooltip;
   }
  }

  closeTooltip(){
    this.overlayRef.detach();
  }
}
