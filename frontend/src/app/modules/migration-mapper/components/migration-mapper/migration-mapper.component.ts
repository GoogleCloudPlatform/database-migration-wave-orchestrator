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

import { Component, OnInit, OnDestroy } from '@angular/core';
import { SubscriptionLike } from 'rxjs';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Sort } from "@angular/material/sort";

import { Mapping, Node, Bms } from 'src/app/interfaces/mapping';
import { Wave } from 'src/app/interfaces/wave';
import { Target } from 'src/app/interfaces/targets';
import { SourceDb } from "src/app/interfaces/sourceDb";
import { AddWave, AddWaveResp } from '@app-interfaces/wave';
import { DialogData } from '@app-interfaces/dialog-data';

import { MappingService } from '@app-services/migration-mapper/mapping.service';
import { TargetsService } from '@app-services/targets/targets.service';
import { WaveService } from '@app-services/wave/wave.service';
import { SourceDbService } from '@app-services/source-db/source-db.service';
import { UtilService } from '@app-services/util/util.service';
import { SlidingPanelService } from '@app-services/sliding-panel/sliding-panel.service';

import { WarningDialogComponent } from '../warning/warning.component';
import { BaseMaterialTableComponent } from "@app-shared/components/base-material-table/base-material-table.component";
import { Label, LabelMeta } from '@app-interfaces/label';
import { LabelService } from '@app-services/label/label.service';
import { WaveAssignComponent } from '../wave-assign/wave-assign.component';
import { ConfirmDialogComponent } from '@app-shared/components/confirm-dialog/confirm-dialog.component';


@Component({
  selector: 'app-migration-mapper',
  templateUrl: './migration-mapper.component.html',
  styleUrls: ['./migration-mapper.component.scss'],
})
export class MigrationMapperComponent extends BaseMaterialTableComponent<Mapping | any> implements OnInit, OnDestroy {
  public mappings: Mapping[] | undefined;
  public waves: Wave[] | undefined;
  public targets: Target[] | undefined;
  public ELEMENT_DATA: any[] = [];
  public displayedColumns: string[] | undefined;
  public project_id!: number;
  private subscriptions: SubscriptionLike[] = [];
  public statusFilter = 'All';
  public labels: Label[] = [];
  labelFilter: string[] = [];
  labelsList!: any[];
  filterValues: any = {};
  filter: string = '';

  constructor(
    public dialog: MatDialog,
    private mappingService: MappingService,
    private labelService: LabelService,
    private sourceDbService: SourceDbService,
    private util: UtilService,
    private waveService: WaveService,
    private targetService: TargetsService,
    private snackBar: MatSnackBar,
    private slidingPanelService: SlidingPanelService,
  ) {
    super();
  }

  ngOnInit(): void {
    localStorage.removeItem('filterStateMigration');
    if (this.util.getCurrentProjectId() != null) {
      this.project_id = this.util.getCurrentProjectId();
    }
    this.getMigrations();
    this.getWaves();
    this.getLabels();
    this.displayedColumns = [ 'source_hostname', 'db_name', 'oracle_version' , 'db_type_text' , 'target_host', 'label', 'configuration' , 'wave', 'status'];

    this.subscriptions.push(this.waveService.refreshWaveList$.subscribe((val: boolean) => {
      if (val) {
        this.getWaves();
      }
    }));

    this.subscriptions.push(this.labelService.changeLabel$.subscribe((val: boolean) => {
      if (val) {
        this.getLabels();
      }
    }));
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(
      (subscription: SubscriptionLike) => subscription.unsubscribe());
    this.subscriptions = [];
  }

  applyFilterForTable(filter: any, value?: any): void {
    this.filter = filter;
    this.filterValues[filter] = value.toString();
    this.dataSource.filter = JSON.stringify(this.filterValues);
  }

  selectNoLabel(): void {
    this.labelFilter = ['no_label'];
    this.applyFilterForTable('label', this.labelFilter);
  }

  resetLabelFilter(): void {
    this.labelFilter = [];
    this.applyFilterForTable('label', this.labelFilter);
  }

  setCurrentElement(): void {
    this.removeItemOnce(this.labelFilter, 'no_label');
    this.applyFilterForTable('label', this.labelFilter);
  }

    isDms(target_db_tool_id : number) {
      return (target_db_tool_id == 2 ? true :  false);
    }

  getWaves(): void {
    this.subscriptions.push(
      this.waveService.getMigrationWaves(this.project_id).subscribe((resp: Wave) => {
        this.waves = resp.data;
      })
    );
  }

  getMigrations(): void {
    this.subscriptions.push(
      this.mappingService.getMigrationMappings(this.project_id).subscribe((resp: Mapping) => {
        this.mappings = resp.data;
        console.log("JSON Response: " + resp.data);
        this.ELEMENT_DATA = [];
        resp.data?.forEach((item: Mapping) => {
          item.db_type_text = this.getType(item.db_type);
          //target_db_tool_id: item.target_db_tool_id;
          if (item.db_type === 'SI') {
            this.ELEMENT_DATA?.push(item);
          } else {
            let nodes: Node[] = [];
            const nodesCount = item?.fe_rac_nodes || item.bms.length;

            for(let i = 0; i < nodesCount; i++) {
              nodes.push({ label: `RAC Node ${i + 1}:`, value: item.bms[i]?.id || i + '' });
            }

            const newItem = {
              ...item,
              nodes_amount: nodesCount,
              nodes
            };

            this.ELEMENT_DATA?.push(newItem);
          }
        });
        this.getSourceDbs();
        this.getTargets();
        this.initDataSource(this.ELEMENT_DATA);
      })
    );
  }

  getTargets(): void {
    this.subscriptions.push(
      this.targetService.getUnmappedTargetsProjects(this.project_id).subscribe((resp: Target) => {
        const isMappedArray: Target[] = [];
        const isNotMappedArray: Target[] = [];

        this.targets = resp.data;
        this.targets?.forEach((e: Target) => {
          const isMapped = this.mappings?.some((m: Mapping) => {
            return m?.bms.some((element: Bms) => {
              return element.id === e.id;
            });
          });

          if (isMapped) {
            e.isMapped = true;
            isMappedArray.push(e);
          } else {
            isNotMappedArray.push(e);
          }
        });

        this.targets = [...isNotMappedArray, ...isMappedArray];
      })
    );
  }

  assignToWave(): void {
    if (!this.dataSource.filteredData.length) {
      this.openSnackBar('Please select mappings for assigning');
      return;
    }

    const editableMappingCheck = this.dataSource.filteredData.every((mapping) => !mapping.editable);
    if (editableMappingCheck) {
      this.openSnackBar('All selected mappings cannot be assigned to another wave');
      return;
    }

    const dialogRef = this.dialog.open(WaveAssignComponent, {
      data: {
        waves: this.waves
      },
      width: '550px',
      role: 'alertdialog',
      panelClass: 'custom-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result?.event === 'assign') {
        this.openAssignWaveConfirmationMessage(result.wave);
      }
      (error:string) => {
        this.openSnackBar(error);
      }
    })
  }

  getLabels(): void {
    this.labelService.getLabels(this.project_id).subscribe((resp: LabelMeta) => {
      this.labels = resp.data;

      this.sortLabels();
      this.createLabelsList();
    })
  }

  manageLabels(event: Event): void {
    event.stopPropagation();
    this.slidingPanelService.slidingPanelConfig$.next({ name: 'label', editMode: false });
  }

  getSourceDbs(): void {
    this.subscriptions.push(
      this.sourceDbService.getSourceDbsProjects(this.project_id).subscribe((resp: SourceDb) => {
        resp.data?.forEach((item: SourceDb) => {
          if (!this.mappings?.some((m: Mapping) => m.db_id === item.id)) {
            const nodesCount = item?.fe_rac_nodes || item.rac_nodes;
            let newMapping = {
              db_id: item.id,
              db_type: item.db_type,
              db_name: item.db_name,
              oracle_version: item.oracle_version,
              source_hostname: item.server,
              nodes_amount: nodesCount,
              nodes: [] as Node[],
              wave_id: item.wave_id,
              labels: item.labels,
              db_type_text: this.getType(item.db_type),
              editable: true
            };

            for(let i = 0; i < nodesCount; i++) {
              newMapping.nodes.push({ label: `RAC Node ${i+1}:`, value: i + '' });
            }
            this.ELEMENT_DATA?.push(newMapping);
          }
        });
        this.initDataSource(this.ELEMENT_DATA);
        const sortState: Sort = { active: 'source_hostname', direction: 'asc' };

        if (this.dataSource?.sort) {
          this.dataSource.sort.active = sortState.active;
          this.dataSource.sort.direction = sortState.direction;
          this.dataSource.sort.sortChange.emit(sortState);
        }

        this.setFilterPredicate();
      })
    );
  }

  isWaveRunning(wave_id: number) {
    return this.waves?.find(wave => wave.id === wave_id)?.is_running;
  }

  addNode(row: Mapping): void {
    this.ELEMENT_DATA?.forEach((dataRow: Mapping) => {
      if (dataRow.db_id === row.db_id) {
        dataRow.nodes_amount = dataRow.nodes_amount as number + 1;
        dataRow.nodes?.push({ label: `RAC Node: ${ dataRow.nodes_amount }`, value: dataRow.nodes_amount + 1 + '' });
      }
    });
  }

  deleteNode(row: Mapping, node: number): void {
    this.ELEMENT_DATA?.forEach((dataRow: Mapping) => {
      if (dataRow.db_id === row.db_id) {
        const nodes = dataRow.nodes?.filter((rowNode: any) => {
          return rowNode.value !== node;
        });
        const bmsId: any[] = [];

        nodes?.forEach(el => {
          if (el.value && (typeof el.value === 'number')) {
            bmsId.push(el.value);
          }
        });

        this.updateMigrationMapping(row.db_id, bmsId, nodes?.length || 0, row.wave_id, true, dataRow);
      }
    });
  }

  getType(db_type: string | undefined): string {
    switch (db_type) {
      case 'SI':
        return 'Single Instance';
      case 'RAC':
        return 'Real Application Cluster';
      default:
        return 'DG'; // TODO
    }
  }

  updateMappings($event: any, row: Mapping, isWave: boolean, db_type: string): void {
    const isSingle = db_type === 'SI';
    let bmsId: any[] = [];

    if (isSingle) {
      if ($event.value) {
        bmsId.push(row?.bms && row?.bms[0]?.id || $event.value);
      }
    } else {
      row.nodes?.forEach((node: Node) => {
        if (node.value && (typeof node.value === 'number')) {
          bmsId.push(node.value);
        }
      });
    }

    const nodesCount = row.nodes?.length || 0;

    if (this.mappings?.some((m: Mapping) => m.db_id === row.db_id )) {
      const isHideMessage = localStorage.getItem('hideMessage');

      if (!isWave && !isHideMessage) {
        this.openDialog(row.db_id, bmsId, nodesCount, row.wave_id);
      } else {
        const singleWawe = isWave && isSingle;

        this.updateMigrationMapping(row.db_id, bmsId, nodesCount, row.wave_id, false, {}, singleWawe, isWave);
      }
    } else {
      const newMapping = { db_id: row.db_id, bms_id: bmsId, fe_rac_nodes: nodesCount, wave_id: row.wave_id };

      this.subscriptions.push(
        this.mappingService.createMigrationMapping(newMapping).subscribe(()=> {
          this.getMigrations();
        })
      );
    }
  }

  trackBy(index: number): number {
    return index;
  }

  private sortLabels(): void {
    this.labels.sort(function (a, b) {
      if (a.name > b.name) {
        return 1;
      }
      if (a.name < b.name) {
        return -1;
      }
      return 0;
    });
  }

  private createLabelsList(): void {
    const list: any[] = [];

    this.labels.forEach((val: Label) => {
      list.push({ value: val.name });
    });

    this.labelsList = list;
  }

  private setFilterPredicate(): any {
    return this.dataSource.filterPredicate = (
      data: { is_configured: boolean, wave_id: number },
      filterValue: string
    ) => {
      let searchTerms = JSON.parse(filterValue);
      let isFilterSet = false;
      for (const col in searchTerms) {
        if (searchTerms[col].toString() !== '') {
          isFilterSet = true;
        } else {
          delete searchTerms[col];
        }
      }

      let search = () => {
        let found = false;
        let filterStatus = false;
        let filterForLabel = false;

        if (isFilterSet) {
          if (Object.keys(searchTerms).length > 1) {
            Object.keys(searchTerms).forEach((val: any) => {
              if (val === 'status') {
                filterStatus = this.filterForStatus(searchTerms[val].toLowerCase(), data);
              }

              if (val === 'label') {
                filterForLabel = this.filterForLabel(searchTerms[val], data);
              }
            });

            found = filterStatus && filterForLabel;
          } else {
            if (Object.keys(searchTerms)[0] === 'status') {
              found = this.filterForStatus(searchTerms.status.toLowerCase(), data);
            } else {
              found = this.filterForLabel(searchTerms.label, data);
            }
          }
          return found;
        } else {
          return true;
        }
      }
      return search();
    }
  }

  private filterForStatus(value: string, data: any): boolean {
      if (value === 'all') {
        return true;
      }

      if (value === 'configured' && !!data?.is_configured) {
        return true;
      }

      if (value === 'not configured' && !data?.is_configured) {
        return true;
      }

      if (value === 'assigned' && !!data?.wave_id) {
        return true;
      }

      if (value === 'not assigned' && !data?.wave_id) {
        return true;
      }

      return false;
  }

  private filterForLabel(filterValue: string, data: any): boolean {
    if (filterValue) {
      let value = filterValue.trim();
      let arrLabels = value.split(',');
      if (arrLabels.includes('no_label')) {
        if (data.labels.length < 1) {
          return true;
        }
      }

      if (arrLabels && data?.labels.length) {
        return arrLabels.every(element => data.labels.filter((label: Label) => label.name === element).length > 0)
      }

      return false;
    } else {
      return true;
    }
  }

  private openAssignWaveConfirmationMessage(wave: string): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: <DialogData>{
        message: `By this performing action you will change previous wave assignments for the selected list of mappings.
        Do you want to proceed?`,
        AcceptCtaText: true,
        CancelCtaText: false,
        acceptBtnText: 'Proceed',
        cancelBtnText: 'Cancel',
        headerText: 'Assign wave?'
      },
      width: '550px',
      role: 'alertdialog',
      panelClass: 'custom-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result === true) {
        this.assignWaveMigration(wave);
      }
      (error: string) => {
        this.openSnackBar(error);
      }
    });
  }

  private assignWaveMigration(name: string): void {
    const db_ids = this.dataSource.filteredData.map((data) => data.db_id);
    const assignWaveObj: AddWave = {
      name,
      project_id: this.project_id,
      db_ids
    };

    this.waveService.createMigrationWave(assignWaveObj).subscribe((resp: AddWaveResp) => {
      let message = '';
      if (resp.assigned) {
        message += `Wave '${name}' has been successfully assigned to ${resp.assigned} mappings.`
      }
      if (resp.skipped) {
        message += `And ${resp.skipped} mapping(s) were not assigned due to their relation to already started the migration.`
      }
      if (resp.unmapped) {
        message += `${resp.unmapped} mapping(s) were not assigned due to target absence`;
      }
      this.openSnackBar(message);

      if (resp.assigned) {
        this.getWaves();
        this.getMigrations();
      }
    },
    (error) => {
      this.openSnackBar(error);
    })
  }

  private removeItemOnce(arr: string[], value: string):string[] {
    let index = arr.indexOf(value);

    if (index > -1) {
      arr.splice(index, 1);
    }

    return arr;
  }

  private openSnackBar(message:string) {
    this.snackBar.open(message, 'Close' , {
      duration: 5000,
    });
  }

  private openDialog(dbId: number, bmsId: number[], nodesCount: number, waveId?: number): void {
    const dialogRef = this.dialog.open(WarningDialogComponent, { panelClass: 'custom-dialog' });

    dialogRef.afterClosed().subscribe(result => {
      if (result.isHideMessage) {
        localStorage.setItem('hideMessage', 'true');
      } else {
        localStorage.removeItem('hideMessage');
      }

      if (result.ok) {
        this.updateMigrationMapping(dbId, bmsId, nodesCount, waveId);
      } else {
        this.getMigrations();
      }
    });
  }

  private updateMigrationMapping(dbId: number, bmsId: number[], nodesCount: number, waveId?: number, isDelete?: boolean, dataRow?: any, singleWawe?: boolean, isWave?: boolean): void {
    const updateMapping = { db_id: dbId, bms_id: bmsId, fe_rac_nodes: nodesCount, wave_id: waveId };

    this.subscriptions.push(
      this.mappingService.editMigrationMapping(updateMapping)
        .subscribe(
          () => {
            if (isDelete) {
              (dataRow.nodes_amount as number)--;
            }
            if (!singleWawe && !isWave) {
              this.getMigrations();
            }
          },
          (error) => {
            this.openSnackBar(this.modelingError(error));
          }
        )
    );
  }

  private modelingError(error: any): string {
    if (error?.db_id && error.db_id[0]) {
      return `Error Db ${ error?.db_id && error.db_id[0] }`;
    } else
    if (error?.wave_id && error.wave_id[0]) {
      return `Error Wave ${ error?.wave_id && error.wave_id[0] }`;
    } else
    if (error?.bms_id && error.bms_id[0]) {
      return `Error Bms ${ error?.bms_id && error.bms_id[0] }`;
    } else
    if (error[0]) {
      return error[0];
    } else {
      return 'Unexpected error';
    }
  }
}
