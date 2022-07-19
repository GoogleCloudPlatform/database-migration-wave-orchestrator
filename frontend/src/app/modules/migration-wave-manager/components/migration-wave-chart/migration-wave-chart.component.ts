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

import { Component, ElementRef, Input, OnInit, ViewChild } from "@angular/core";

@Component({
    selector: 'app-migration-wave-chart',
    templateUrl: './migration-wave-chart.component.html'
  })
  export class MigrationWaveChartComponent implements OnInit {
  
  @Input() waveProgress!: {deployed: number, failed: number, undeployed: number};
  @Input() waveIsRunning: boolean = false;
  @Input() waveSteps!: {curr_step: number, total_steps: number};
      
  @ViewChild('canvas', { static: true })
  canvas!: ElementRef<HTMLCanvasElement>;  
  
  private ctx!: CanvasRenderingContext2D | null;
  
  constructor() {}

  ngOnInit(): void {
    this.ctx = this.canvas.nativeElement.getContext('2d');
    this.drawChart();
  }

  drawRunningChart(ctx: CanvasRenderingContext2D, x: number, y:number): void {
    if(this.waveSteps) {
      this.drawGreyChart(ctx, x, y);
      ctx.font = "bold 18px Arial";
      ctx.fillStyle = "black";
      ctx.textAlign ="center"
      ctx.fillText('Step ' + this.waveSteps.curr_step + '/' + this.waveSteps.total_steps, x, y + 5);
      this.drawStatusTopText(ctx, x, 'orange', 'Running');
    }
  }

  drawResultChart(ctx: CanvasRenderingContext2D, x: number, y:number): void {
    const colors = [
      'green',
      'red',
      'gray',
    ]   
       
    let start = 0;     
    let data = Object.values(this.waveProgress);
    let totalValue = data.reduce((previousValue, currentValue) => previousValue + currentValue);
    if(this.waveProgress.undeployed !== totalValue) {
      for (let i in data) {
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.arc(x, y, 50, start, start + (Math.PI * 2 * (data[i] / totalValue)), false);
        ctx.fillStyle = colors[i];
        ctx.fill();
        start += Math.PI * 2 * (data[i] / totalValue);       
      }

      this.drawWhiteColor(ctx, x, y);
      ctx.font = "bold 16px Arial";
      if(this.waveProgress.failed > 0) {        
        ctx.fillStyle = "red";
        if(this.waveProgress.deployed > 0) {
          ctx.fillText(Math.floor(this.waveProgress.failed/totalValue * 100) + '%', 25, y + 5);
          ctx.fillStyle = "black";
          ctx.fillText('/', x - 1, y + 5);
          ctx.fillStyle = "green";
          ctx.fillText(Math.floor(this.waveProgress.deployed/totalValue * 100) + '%', x + 7, y + 5);
        } else {
          ctx.textAlign = "center";
          ctx.fillText(Math.floor(this.waveProgress.failed/totalValue * 100) + '%', x, y + 5);
        }        
      } else {
        ctx.fillStyle = "green";
        ctx.textAlign = "center";
        ctx.fillText(Math.floor(this.waveProgress.deployed/totalValue * 100) + '%', x, y + 5);
      }    
    } else {
      this.drawGreyChart(ctx, x, y);
      this.drawStatusTopText(ctx, x, 'gray', 'Undeployed');
    }
  }

  drawChart():void { 
    if(this.ctx){
      let x = this.ctx.canvas.width / 2;
      let y = this.ctx.canvas.height / 2 + 5;
      if(this.waveIsRunning) {
        this.drawRunningChart(this.ctx, x, y);
      } else {
        this.drawResultChart(this.ctx, x, y);
      }   
    }
    
  } 
  
  drawGreyChart(ctx: CanvasRenderingContext2D, x: number, y:number) {       
    ctx.arc(x, y, 50, 0, 2 * Math.PI, false);
    ctx.fillStyle = 'gray';
    ctx.fill();
    this.drawWhiteColor(ctx, x, y);
  }

  drawWhiteColor(ctx: CanvasRenderingContext2D, x: number, y:number)  {
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.arc(x, y, 40, 0, 2 * Math.PI, false);
    ctx.fillStyle = '#FFFFFF';
    ctx.fill();
  }

  drawStatusTopText(ctx: CanvasRenderingContext2D, x: number, color: string, text: string) {
    ctx.font = "12px Arial";
    ctx.fillStyle = color;
    ctx.textAlign = "center"
    ctx.fillText(text, x, 10);
  }
}
