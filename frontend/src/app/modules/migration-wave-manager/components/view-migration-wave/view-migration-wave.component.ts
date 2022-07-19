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

import { Component, EventEmitter, Input, OnDestroy, OnInit, Output, ViewChild } from '@angular/core';
import { SelectionModel } from "@angular/cdk/collections";
import { Subscription } from 'rxjs';
import { MatPaginator } from '@angular/material/paginator';
import { MatSnackBar } from '@angular/material/snack-bar';

import { Wave } from '@app-interfaces/wave';

import { WaveService } from '@app-services/wave/wave.service';
import { SlidingPanelService } from '@app-services/sliding-panel/sliding-panel.service';

import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";
import { Sort } from '@angular/material/sort';

@Component({
  selector: 'app-view-migration-wave',
  templateUrl: './view-migration-wave.component.html',
  styleUrls: ['./view-migration-wave.component.scss']
})
export class ViewMigrationWaveComponent extends BaseMaterialTableComponent<any> implements OnInit,  OnDestroy {
  @Input() public wave_id!: number;
  @Output() waveChanged = new EventEmitter<any>();
  
  private waveSubscription!: Subscription;
  public wave!: Wave;
  public displayedColumns: string[] | undefined;
  public showTargets = false;
  public statusFilter = 'all';
  public hasConfiguredMappings: boolean | undefined;
  public showConfiguredOnly = true;
  public showTable = false;
  selection = new SelectionModel<any>(true, []);

  constructor(
    private waveService: WaveService,
    private snackBar: MatSnackBar,
    private slidingPanelService: SlidingPanelService,
  ) {
    super();
  }

  ngOnInit(): void {
    this.getWaveDeatils();
  }

  startDeployment(): void {
    if(this.selection.isEmpty()){
      this.openSnackBar('Before starting deployment or cleanup, please select mapping.');
      return;
    }
    if(this.selection.selected.find((item) => item.is_deployable === false)) {
      this.openSnackBar('Before starting deployment, please select only deployable mappings.');
      return;
    }
    const mappings = {
      db_ids: this.getMappings()
    }
    this.waveService.startDeployment(this.wave_id, mappings).subscribe(() => {
      this.getWaveDeatils();
      this.waveChanged.emit();
      this.openSnackBar(`Starting deployment for ${this.selection.selected.length} target(s)`);
    })
  }

  getWarningTooltip(row: any): string {
    let warningTooltip = 'Deployment is not possible';

    if (!row.is_configured) {
      warningTooltip += 'Mapping is not configured.';
    }
    if (!row.has_secret_name) {
      warningTooltip += 'Secret Name is not felled.';
    }

    return warningTooltip;
	}

  startCleanUp(): void {
    if(this.selection.isEmpty()){
      this.openSnackBar('Before starting deployment or cleanup, please select mapping.');
      return;
    }
    const mappings = {
      db_ids: this.getMappings()
    }
    this.waveService.startCleanUp(this.wave_id, mappings).subscribe(() => {
      this.getWaveDeatils();
      this.waveChanged.emit();
      this.openSnackBar(`Starting cleanup  for ${this.selection.selected.length} target(s)`);
    })
  }

  getMappings() {
    return Array.from(this.selection.selected, (element, index) =>  this.selection.selected[index].db_id);
  }

  deleteWave() {
    this.waveService.deleteWave(this.wave_id).subscribe(() => {
      this.waveChanged.emit();
    })
  }

  getWaveDeatils() {
    this.waveSubscription = this.waveService.getMigrationWaveDetails(this.wave_id).subscribe((resp) => {
      this.wave = resp;
      if(this.wave.mappings) {
        this.showTable = true;
        this.initDataSource(this.wave.mappings);
        this.getDisplayedColumns();
        this.setFilterPredicate();
        this.setSorting();
      }      
    })
  }

  private setFilterPredicate() {
    this.dataSource.filterPredicate = (record,filter) => {
      const matchFilter = [];
      const deployableFilter = filter !== 'all' ? record.is_deployable.toString() === filter : true;
      matchFilter.push(deployableFilter);
      if(this.showConfiguredOnly) {
        const configuredFilter = record.is_configured === true;
        matchFilter.push(configuredFilter);
      }
      return matchFilter.every(Boolean);
    }
    this.applyStatusFilter();
  }

  private setSorting() {    
    this.dataSource.sortingDataAccessor = (item, property) => {
      if (property === 'target_hostname') {
        return item.bms[0].bms_name
      } else {
        let key = item[property as keyof Object]?.toLocaleString()
        return  key ? key : '';
      }
    };
  }

  getDisplayedColumns() {
    if(this.wave.is_running) {
      this.displayedColumns = [ 'server', 'db_name', 'db_type' , 'target_hostname', 'details']
    } else  if(!this.wave.mappings?.some(i => i.operation_id)){
      this.displayedColumns = ['select', 'server', 'is_configured', 'db_name', 'db_type' , 'target_hostname']
    } else {
      this.displayedColumns = [ 'select', 'server', 'is_configured', 'db_name', 'db_type' , 'target_hostname', 'operation_type' , 'operation_status', 'details']
    }
    this.hasConfiguredMappings = this.wave.mappings?.some(e => e.is_configured && e.has_secret_name);
  }

  applyStatusFilter() {
    this.dataSource.filter = this.statusFilter.trim().toLowerCase();
    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  editWave(): void {
    this.slidingPanelService.slidingPanelConfig$.next({ name: 'wave', editMode: true, waveId: this.wave.id });
  }

  toggle(row: any): void {
    this.showTargets = !this.showTargets;
    row.bms.showTargets = this.showTargets;
  } 

  /** Selects all rows if they are not all selected; otherwise clear selection. */
  masterToggle() {
    if (this.isAllSelected()) {
      this.selection.clear();
      return;
    }

    this.selection.select(...this.dataSource.data.filter(e => e.is_configured));
  }

  /** Whether the number of selected elements matches the total number of rows. */
  isAllSelected() {
    const numSelected = this.selection.selected.length;
    const numRows = this.dataSource.data.length;
    return numSelected === numRows;
  }

  /** The label for the checkbox on the passed row */
  checkboxLabel(row?: any): string {
    if (!row) {
      return `${this.isAllSelected() ? 'deselect' : 'select'} all`;
    }
    return `${this.selection.isSelected(row) ? 'deselect' : 'select'} row ${row.position + 1}`;
  }

  ngOnDestroy() {
    this.waveSubscription.unsubscribe();
  }

  openSnackBar(message:string) {
    this.snackBar.open(message, 'Accept' , {
      duration: 5000,
    });
  }
}
