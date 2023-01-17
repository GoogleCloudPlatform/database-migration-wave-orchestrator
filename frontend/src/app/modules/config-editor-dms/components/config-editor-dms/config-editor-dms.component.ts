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

import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, ValidatorFn, ValidationErrors, Validators, AbstractControl } from "@angular/forms";
import { ActivatedRoute } from "@angular/router";
import { MatSnackBar } from "@angular/material/snack-bar";
import { SubscriptionLike, Subscription } from 'rxjs';
import { pairwise } from 'rxjs/operators';

import { UtilService } from "@app-services/util/util.service";
import { ConfigEditorDmsService } from "@app-services/config-editor-dms/config-editor-dms.service";
import { MappingService } from "@app-services/migration-mapper/mapping.service";
import { TargetsService } from "@app-services/targets/targets.service";

import {dataMountPurposeOptions , BaseOptions, redundancyOptions, asmDiskOptionSelect, auSizeOptions, errorInfo, dumpflag, migrationJobType, connectionMethod}  from './config-editor-dms.data';
import { ConfigEditorDms, DataMountValues, Node } from "@app-interfaces/configEditorDms";
import { Mapping, Bms } from "@app-interfaces/mapping";
import { Target } from "@app-interfaces/targets";
import { MatAutocompleteSelectedEvent } from '@angular/material/autocomplete';

@Component({
  selector: 'app-config-editor-dms',
  templateUrl: './config-editor-dms.component.html'
})
export class ConfigEditorDmsComponent implements OnInit, OnDestroy {


  configEditorDmsForm: FormGroup;

   mappings: Mapping | undefined;
    allMappings: Mapping[] = [];

    devices!: FormArray;
    disks!: FormArray;

    dataMountPurposeOptions: BaseOptions[];
    lunsOptions!: BaseOptions[];
    auSizeOptions!: BaseOptions[];
    selectedLuns: number[] = [];
    selectedDevicesForDataMountsValues: number[] = [];
    selectedDevicesForAsmConfigValues: number[] = [];
    asmDiskOptionSelect!: any[];
    dumpflag!: any[];
    migrationJobType!: any[];
    connectionMethod!: any[];
    redundancyOptions!: any[];
    targets: Target[] = [];
    compatible = new Map([
      ['19.0', ['19.0', '18.0', '12.2', '12.1', '11.2']],
      ['18.0', ['18.0', '12.2', '12.1', '11.2']],
      ['12.2', ['12.2', '12.1', '11.2']],
      ['12.1', ['12.1', '11.2']],
      ['11.2', ['11.2']],
    ]);

    private routeSubscription!: Subscription;

    private subscriptions: SubscriptionLike[] = [];
    private oracle_version!: string;



  asm_config_values!: FormArray;
  rdbmsValues: string[] = [];

  private currentProjectId!: number;
  private db_id!: number

  public isInvalid = false;
  public isSwapWarningShown = false;
  public isFormDisabled = false;

  constructor(
    private utilService: UtilService,
    private mappingService: MappingService,
    private activatedRoute: ActivatedRoute,
    private formBuilder: FormBuilder,
    private configEditorDmsService: ConfigEditorDmsService,
    private targetService: TargetsService,
    private snackBar: MatSnackBar)
  {
    this.dataMountPurposeOptions = dataMountPurposeOptions;
    this.asmDiskOptionSelect = asmDiskOptionSelect;
    this.dumpflag = dumpflag;
    this.migrationJobType = migrationJobType;
    this.connectionMethod = connectionMethod;
    this.redundancyOptions = redundancyOptions;
    this.auSizeOptions = auSizeOptions;
    this.configEditorDmsForm = this.formBuilder.group({
      created_at:     new FormControl('' , []),
      misc_config_values: new FormGroup({
        oracle_root:       new FormControl('/app', [Validators.required] ),
        ntp_preferred:       new FormControl('', [this.preferredNTPServerValidation]),
        role_separation:     new FormControl(true, [Validators.required]),
        compatible_asm:      new FormControl({value: '', disabled: true}, [ Validators.maxLength(30)]),
        compatible_rdbms:    new FormControl('', [ Validators.maxLength(30)]),
        asm_disk_management: new FormControl('Udev', [Validators.required, Validators.maxLength(20)]),
        swap_blk_device: new FormControl('', [] ),
        is_swap_configured: new FormControl(false)
      }),
      data_mounts_values: this.formBuilder.array([ this.createDevices()]),
      asm_config_values: this.formBuilder.array([ this.createAsmData() ], [Validators.required]),
      install_config_values:   new FormGroup({
        oracle_user:  new FormControl('oracle' , [
          Validators.required,
          Validators.maxLength(30),
          Validators.pattern('[a-zA-Z0-9._]*')]),
        oracle_group: new FormControl('oinstall' , [
          Validators.required,
          Validators.maxLength(30),
          Validators.pattern('[a-zA-Z0-9._]*')]),
        home_name:    new FormControl('dbhome_1' , [Validators.required]),
        grid_user:    new FormControl('grid' , [
          Validators.required,
          Validators.maxLength(30),
          Validators.pattern('[a-zA-Z0-9._]*')]),
        grid_group:   new FormControl('oinstall' , [
          Validators.required,
          Validators.maxLength(30),
          Validators.pattern('[a-zA-Z0-9._]*')]),
      }),
      db_params_values:   new FormGroup({
        db_name:  new FormControl('' , [Validators.required]),
      }),
      is_configured: new FormControl(false, []),
      rac_config_values: new FormGroup({
        cluster_name:  new FormControl('' , [
          Validators.required,
          Validators.minLength(1),
          Validators.maxLength(15),
          Validators.pattern('([a-zA-Z0-9-]){1,15}')
        ]),
        cluster_domain: new FormControl('' , [Validators.required]),
        scan_name: new FormControl('' , [Validators.required]),
        scan_port: new FormControl('' , [
          Validators.required,
          Validators.min(1),
          Validators.max(65535)
        ]),
        scan_ip1: new FormControl('' , [
          Validators.required,
          Validators.pattern('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
        ]),
        scan_ip2: new FormControl('' , [
          Validators.pattern('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
        ]),
        scan_ip3: new FormControl('' , [
          Validators.pattern('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
        ]),
        public_net: new FormControl('' , [Validators.required]),
        private_net: new FormControl('' , [Validators.required]),
        dg_name: new FormControl('' , [Validators.required]),
        rac_nodes: this.formBuilder.array([ this.createRacNode() ])
      }),
    });
  }

  ngOnInit(): void {
    if (this.utilService.getCurrentProjectId() != null) {
      this.currentProjectId = this.utilService.getCurrentProjectId();
    }
    this.getMigrations();
    this.getUnmappedTargets();
    this.activatedRoute.queryParams.subscribe((params) => {
      this.db_id =params.databaseId;
      this.mappingService.getMappingsByDbId(params.databaseId).subscribe((resp) => {
        if (resp.data){
          this.mappings = resp.data[0];
          this.initValueForRacNodes(this.mappings);
          this.configEditorDmsForm.get('db_params_values')?.get('db_name')?.setValue(this.mappings.db_name);
          this.targetService.getTargetsProject(this.mappings.bms[0].id).subscribe(targets => {
            this.lunsOptions = [];
            targets.luns.forEach((element: any, index: number) => {
              this.lunsOptions.push(
                {
                  text: element.storage_volume,
                  value: element.size_gb ,
                  selected : false ,
                  id: index,
                  size_gb: element.size_gb
                }
              );
            })
            this.configEditorDmsService.getConfigEditor(params.databaseId).subscribe( (resp:ConfigEditorDms) => {
              this.fillForm(resp);
              this.checkDisableForm(this.mappings as Mapping);
            });
          });
        }
      })
    });


    this.subscriptions.push(
      this.configEditorDmsForm.get('data_mounts_values')?.valueChanges.pipe(pairwise()).subscribe(([prevValue,nextValue]: [DataMountValues[], DataMountValues[]]) => {
        this.checkMountPointValidator(prevValue, nextValue);

        const software = nextValue.find(this.findSoftware);
        const diag = nextValue.find(this.findDiag);
        const notSwap = nextValue.find(this.findNotSwap);
        const oracleRoot = this.configEditorDmsForm?.get('misc_config_values')?.get('oracle_root');

        this.selectedDevicesForDataMountsValues = [];

        if (software) {
          oracleRoot?.setValue(software.mount_point + '/app');
        } else
        if (diag) {
          oracleRoot?.setValue(diag.mount_point + '/app');
        } else
        if (notSwap) {
          oracleRoot?.setValue(notSwap.mount_point + '/app');
        } else {
          oracleRoot?.setValue('/app');
        }

        nextValue?.forEach((val: any) => {
          this.lunsOptions?.forEach((v) => {
            if ((v.text === val.blk_device) && !this.selectedDevicesForDataMountsValues.includes(v.id as number)) {
              this.selectedDevicesForDataMountsValues.push(v.id as number);
            }
          });
        });
        this.selectedLuns = [...this.selectedDevicesForDataMountsValues, ...this.selectedDevicesForAsmConfigValues];
      }) as SubscriptionLike
    );

    this.subscriptions.push(
      this.configEditorDmsForm.get('asm_config_values')?.valueChanges.subscribe(value => {
        this.selectedDevicesForAsmConfigValues = [];

        if (value[0]?.diskgroup) {
          this.configEditorDmsForm?.get('rac_config_values')?.get('dg_name')?.setValue(value[0]?.diskgroup);
        }

        value?.forEach((val: any) => {
          val.disks?.forEach((element: any) => {
            this.lunsOptions?.forEach((v) => {
              if ((v.text === element.blk_device) && !this.selectedDevicesForAsmConfigValues.includes(v.id as number)) {
                this.selectedDevicesForAsmConfigValues.push(v.id as number);
              }
            });
          });
        });
        this.selectedLuns = [...this.selectedDevicesForDataMountsValues, ...this.selectedDevicesForAsmConfigValues];
      }) as SubscriptionLike
    );
  }

  ngOnDestroy(): void {
    this.routeSubscription && this.routeSubscription.unsubscribe();
    this.subscriptions.forEach(
      (subscription: SubscriptionLike) => subscription.unsubscribe());
    this.subscriptions = [];
    sessionStorage.removeItem('configEditorData')
  }

  private fillForm(resp: ConfigEditorDms) {
    this.configEditorDmsForm.patchValue(resp);

    const dataMountsValues = this.configEditorDmsForm.get('data_mounts_values') as FormArray;

    if (resp.misc_config_values?.swap_blk_device) {
      resp.data_mounts_values.push({
        blk_device: resp.misc_config_values?.swap_blk_device,
        fstype: 'xfs',
        mount_opts: 'nofail',
        mount_point: '',
        name: '',
        purpose: "swap",
      })
    }
    if (resp.data_mounts_values) {
      dataMountsValues.removeAt(0)
      resp.data_mounts_values.forEach((dmv) => {
        this.lunsOptions.forEach( (lun, index) => {
          if (lun.text === dmv.blk_device){
            this.selectedLuns[index] = index;
          }
        })
        dataMountsValues.push(this.createDevices
          (dmv.blk_device, dmv.fstype, dmv.mount_opts, dmv.mount_point.trim(), dmv.name, dmv.purpose));
      });
    } else {
      dataMountsValues.push(this.createDevices());
    }

    const asmConfigValues = this.configEditorDmsForm.get('asm_config_values') as FormArray;

    if (resp.asm_config_values?.length > 0) {
      asmConfigValues.removeAt(0);
      resp.asm_config_values.forEach((acv: any ) => {
        asmConfigValues.push(
          this.formBuilder.group({
              diskgroup:  new FormControl(acv.diskgroup , [Validators.required]),
              au_size:    new FormControl(acv.au_size, [Validators.required]),
              redundancy: new FormControl(acv.redundancy , [Validators.required]),
              disks: this.fillDisk(acv.disks)
            }
          ));
      } );
    }


  }



  fillDisk(disks: { blk_device: string , size: string , name: string }[]): FormArray {
    const formArray = new FormArray([]);
    disks?.forEach( (element) => {
      formArray.push(
        new FormGroup({
          blk_device: new FormControl(element.blk_device , [Validators.required]),
          size:   new FormControl(element.size , []),
          name:   new FormControl(element.name , [Validators.required]),
        }))
    })
    return formArray
  }

  checkDisableForm(mapping: Mapping): void {
    if (mapping.is_deployed) {
      this.isFormDisabled = true;
      this.configEditorDmsForm.disable();
    }
  }

  async onSubmit() {
    this.prepareForm();

    if (await this.customValidateForm(this.configEditorDmsForm)) {
      if (!this.currentProjectId) return;
      this.configEditorDmsForm.get('is_configured')?.setValue(true);
      this.configEditorDmsService.createConfigEditorsingleInstance(this.configEditorDmsForm.value, this.db_id)
        .subscribe(() => {
          this.openSnackBar('Configuration saved successfully', 'OK');
        })
    }
  }

  prepareForm() {
    if (this.mappings?.db_type !== 'RAC') {
      delete this.configEditorDmsForm.value.rac_config_values;
      delete this.configEditorDmsForm.controls.rac_config_values;
    } else {
      this.configEditorDmsForm.setValidators(this.checkScanIpValidator());
      this.racNodes.updateValueAndValidity();

      this.configEditorDmsForm.value.rac_config_values.rac_nodes.forEach((racNode: Node) => {
        if (racNode.node_id) {
          this.targets.forEach(target => {
            if (target.id === racNode.node_id) {
              racNode.node_ip = target.client_ip + '';
            }
          });
        }
      });
    }

    let oracleRootPrev = ''
    this.ldspFaDevices.controls.map( element => {
      if(element.value.purpose === 'software'){
        oracleRootPrev = `${element.value.mount_point}`
      }
    })

    let swap_blk_device = null;
    this.ldspFaDevices.controls.map((e, i) => {
      if(e.value.purpose === 'swap' && e.value.blk_device) {
        swap_blk_device = e.value.blk_device;
        this.configEditorDmsForm.value.data_mounts_values.splice(i, 1);
      }
    })

    if(swap_blk_device) {
      this.configEditorDmsForm.get('misc_config_values')?.get('swap_blk_device')?.setValue(swap_blk_device);
    }
    else {
      this.configEditorDmsForm.get('misc_config_values')?.get('swap_blk_device')?.setValue('');
    }

    this.configEditorDmsForm.get('misc_config_values')?.get('oracle_root')?.setValue(oracleRootPrev + '/app');

    const localSwapNameValidation = this.ldspFaDevices.controls.find((device: any) => device.get('purpose')!.value === 'swap');
    if (localSwapNameValidation) {
      localSwapNameValidation.get('name')?.setErrors(null);
      localSwapNameValidation.get('mount_point')?.setErrors(null);
    }
  }

  saveDraft() {
    this.prepareForm();
    if (!this.currentProjectId) return;
    this.configEditorDmsForm.get('is_configured')?.setValue(false);
    this.configEditorDmsService.createConfigEditorsingleInstance(this.configEditorDmsForm.value, this.db_id)
      .subscribe(() => {
        this.openSnackBar('Configuration Draft is saved', 'OK');
      })
  }

  getNamesFromAsm(form: FormGroup) : boolean{
    const tempArray: any[] = [];
    form.get('asm_config_values')?.value.forEach( (element: { diskgroup: any; }) => {
      tempArray.push(element.diskgroup)
    })
    return tempArray.includes('DATA1') && tempArray.includes('RECO1')
  }

    getRolValue(): boolean {
      return this.configEditorDmsForm.get('misc_config_values')?.get('role_separation')?.value
    }

  private customValidateForm(form: FormGroup) {
    if(form.get('asm_config_values')?.value.length < 1 && !this.getNamesFromAsm(form)){
      this.openSnackBar('ERROR! : You must create at least one ASM configurations' , 'OK');
      return false;
    }

    /*if(this.diskSizeValidator().length){
      this.diskSizeValidator().forEach((e: errorInfo)  => {
        this.openSnackBar(`ERROR! : the maximum size of the disks that may be added to a diskgroup should not exceed ${e.value} bg` , 'OK');
      })
      return false;
    }*/


    if (!this.configEditorDmsForm.get('misc_config_values')?.get('swap_blk_device')?.value &&
       !this.configEditorDmsForm.get('misc_config_values')?.get('is_swap_configured')?.value &&
       Number(this.oracle_version) < 18) {
         this.openSnackBar('ERROR! : The swap configuration is required for oracle versions less the 18', 'OK');
         return false;
    }

    const checkSwapError = () => {
      return this.ldspFaDevices.controls.some((control) => control.get('purpose')?.hasError('swapIsAlreadyConfigured')) ||
      this.configEditorDmsForm.get('misc_config_values')?.get('is_swap_configured')?.hasError('swapIsAlreadyConfigured');
    }
    if (checkSwapError()) {
      this.openSnackBar('ERROR! : swap configuration is wrong' , 'OK');
      return false;
    }

    const dublicatePurposesCheck = () => this.ldspFaDevices.controls.some((control) => control.get('purpose')?.hasError('incorrect'));
    if (dublicatePurposesCheck()) {
      this.openSnackBar('ERROR! : the local data parameter purpose is dublicated' , 'OK');
      return false;
    }

    const scanIpDublicateCheck = () => {
      return form.get('rac_config_values')?.get('scan_ip2')?.hasError('notUnique') ||
      form.get('rac_config_values')?.get('scan_ip3')?.hasError('notUnique');
    }

    const isVipIpDublicate = this.racNodes?.controls.some(element => {
      return element.get('vip_ip')?.hasError('notUnique');
    });

    if (isVipIpDublicate) {
      this.openSnackBar('ERROR! : VIP IP has to be unique' , 'OK');
      this.isInvalid = true;
      return false;
    }

    if (scanIpDublicateCheck()) {
      this.openSnackBar('ERROR! : SCAN IP-Address has to be unique' , 'OK');
      this.isInvalid = true;
      return false;
    }

    const mountPointCheck = () => this.ldspFaDevices.controls.some((control) => control.get('mount_point')?.hasError('notUnique'));
    if (mountPointCheck()) {
      this.openSnackBar('ERROR! : the local data parameter mount point has to be unique' , 'OK');
      this.isInvalid = true;
      return false;
    }

    if (form.get('misc_config_values')?.get('ntp_preferred')?.hasError('invalidFormat')) {
      this.openSnackBar('ERROR! : Preferred NTP server must be either of IP address or domain.com(domain.gov.com) type' , 'OK');
      this.isInvalid = true;
      return false;
    }

    if (!form.valid) {
      this.openSnackBar('ERROR! : missing fields' , 'OK');
      this.isInvalid = true;
      return false;
    }

    return  true
  }

  openSnackBar(message: string, action: string) {
    this.snackBar.open(message, action , {
      duration: 5000
    });
  }

  private createDevices(blk_device = '', fstype = 'xfs', mount_opts = 'nofail', mount_point = '', name = '', purpose = ''): FormGroup {
    return this.formBuilder.group({
      purpose:     new FormControl(purpose , [Validators.required]),
      blk_device:  new FormControl(blk_device , [Validators.required]),
      name:        new FormControl(name , [Validators.required, Validators.pattern('^\\S.*')]),
      fstype:      new FormControl(fstype , [Validators.required]),
      mount_point: new FormControl(mount_point , [Validators.required, Validators.pattern('^\/.*')]),
      mount_opts: new FormControl(mount_opts , [Validators.required])
    });
  }


  private createAsmData(): FormGroup {
    return this.formBuilder.group({
      diskgroup:  new FormControl('' , [Validators.required]),
      au_size:    new FormControl('4M' , [Validators.required]),
      redundancy: new FormControl('EXTERNAL' , [Validators.required]),
      disks: new FormArray(
        [
          new FormGroup({
            blk_device: new FormControl('' , [Validators.required]),
            size:   new FormControl('' , []),
            name:   new FormControl('' , [Validators.required]),
          })
        ]
      )
    });
  }

  private static crateAsmDisk(): FormGroup{
    return new FormGroup({
      blk_device: new FormControl('', [Validators.required]),
      size: new FormControl('', []),
      name: new FormControl('', [Validators.required])
    })
  }

  get ldspFaDevices () {
    return this.configEditorDmsForm.get('data_mounts_values') as FormArray
  }

  get asmFaData () {
    return this.configEditorDmsForm.get('asm_config_values') as FormArray
  }

  get racNodes(): FormArray {
    return this.configEditorDmsForm.get('rac_config_values')?.get('rac_nodes') as FormArray;
  }

  asmFaDevices (index: number) {
    return this.asmFaData.controls[index].get('disks') as FormArray
  }

  addDevice(): void {
    if (this.isFormDisabled) {
      return;
    }

    this.devices = this.configEditorDmsForm.get('data_mounts_values') as FormArray;
    this.devices.push(this.createDevices());
  }

  addNode(): void {
    if (this.isFormDisabled) {
      return;
    }

    this.racNodes.push(this.createRacNode());
  }

  addAsmData() {
    if (this.isFormDisabled) {
      return;
    }

    this.asm_config_values = this.configEditorDmsForm.get('asm_config_values') as FormArray;
    this.asm_config_values.push(this.createAsmData());
  }

  addDeviceAsmConf(index: number) {
    if (this.isFormDisabled) {
      return;
    }

    this.disks = this.asmFaDevices(index);
    this.disks.push(ConfigEditorDmsComponent.crateAsmDisk());
  }

  removeDevice(i: number) {
    if (this.ldspFaDevices.length == 1 || this.isFormDisabled)
      return;
    this.ldspFaDevices.removeAt(i);
    this.validateSwap();
  }

  removeNode(i: number): void {
    if (this.racNodes.length === 1 || this.isFormDisabled) {
      return;
    }
    this.racNodes.removeAt(i);
  }

  removeDiskGroup(i: number): void {
    if (this.asmFaData.length === 1 || this.isFormDisabled) {
      return;
    }
    this.asmFaData.removeAt(i);
  }

  validatePurposeOptions(event: MatAutocompleteSelectedEvent, index: any) {
    /* Validate software*/
    let tempArray: any[] = []
    const indices = [];
    this.ldspFaDevices.value.forEach((element: any) => {
      tempArray.push(element.purpose)
    });
    let idx = tempArray.indexOf(event.option.value);
    this.validateSwap();
    while (idx != -1) {
      indices.push(idx);
      idx = tempArray.indexOf(event.option.value, idx + 1);
    }

    if (indices.length > 1) {
      this.ldspFaDevices.controls[index].get('purpose')?.setErrors({'incorrect': true})
      this.openSnackBar(`${event.option.value} already selected`, 'OK');
    }

    if (event.option.value === 'swap' &&
      this.configEditorDmsForm.get('misc_config_values')?.get('is_swap_configured')?.value) {
      this.ldspFaDevices.controls[index].get('purpose')?.setErrors({'swapIsAlreadyConfigured': true});
      this.openSnackBar('Swap is configured on server', 'OK');
    }
    /*Validate swap */

    if (event.option.value === 'swap') {
      this.ldspFaDevices.controls[index].get('mount_point')?.setValue('');
      this.ldspFaDevices.controls[index].get('name')?.setValue('');
    }
  }









  assignSize(j: number , k : number , sizeValue:string) {
    this.asmFaDevices(j).controls[k].get('size')?.setValue(sizeValue);

  }

  private createRacNode(): FormGroup {
    return this.formBuilder.group({
      node_id: new FormControl('' , [Validators.required]),
      vip_name: new FormControl('' , [Validators.required]),
      vip_ip: new FormControl('' , [
        Validators.required,
        Validators.pattern('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
      ]),
      node_ip: new FormControl('' , []),
    });
  }

  private getUnmappedTargets(): void {
    this.subscriptions.push(
      this.targetService.getUnmappedTargetsProjects(this.currentProjectId).subscribe((resp: Target) => {
        this.targets = resp.data;
        this.targets?.forEach((e: Target) => {
          const isMapped = this.allMappings?.some((m: Mapping) => {
            return m?.bms.some((element: Bms) => {
              return element.id === e.id;
            });
          });

          if (isMapped) {
            e.isMapped = true;
          }
        });
      })
    );
  }

  private getMigrations(): void {
    this.subscriptions.push(
      this.mappingService.getMigrationMappings(this.currentProjectId).subscribe((resp: Mapping) => {
        this.allMappings = resp.data as Mapping[];
      })
    );
  }

  private initValueForRacNodes(mappings: Mapping): void {
    if (mappings.bms.length) {
      this.racNodes.controls.pop();
      mappings.bms.forEach((bms: Bms) => {
        this.racNodes.controls.unshift(this.formBuilder.group({
          node_id: new FormControl(bms.id , [Validators.required]),
          vip_name: new FormControl('' , [Validators.required]),
          vip_ip: new FormControl('' , [
            Validators.required,
            Validators.pattern('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
          ]),
          node_ip: new FormControl('' , []),
        }));
      });
    }
  }




  checkScanIpValidator(): ValidatorFn {
    return (group: any): ValidationErrors | null => {
      const scanIp1 = group.get('rac_config_values').get('scan_ip1');
      const scanIp2 = group.get('rac_config_values').get('scan_ip2');
      const scanIp3 = group.get('rac_config_values').get('scan_ip3');

      if (scanIp2.value !== '' && scanIp1.value === scanIp2.value) {
        scanIp2.setErrors({ notUnique: true });
      } else
      if (
        (scanIp3.value !== '' && scanIp1.value === scanIp3.value) ||
        (scanIp2.value !== '' && scanIp3.value && scanIp3.value !== '' && scanIp2.value === scanIp3.value)
      ) {
        scanIp3.setErrors({ notUnique: true });
      } else {
        this.racNodes.controls.forEach((element, i, arr) => {
          const vipIp = arr[i]?.get('vip_ip')?.value;

          if (
            (scanIp1.value !== '' && vipIp !== '' && scanIp1.value === vipIp) ||
            (scanIp2.value !== '' && vipIp !== '' && scanIp2.value === vipIp) ||
            (scanIp3.value !== '' && vipIp !== '' && scanIp3.value === vipIp) ||
            ((i > 0) && arr[i-1]?.get('vip_ip')?.value !== '' && vipIp !== '' && arr[i-1]?.get('vip_ip')?.value === vipIp)
          ) {
            arr[i]?.get('vip_ip')?.setErrors({ notUnique: true });
          }
        });
      }

      return null;
    };
  }

  private checkMountPointValidator(prevValue: DataMountValues[], nextValue: DataMountValues[]) {
    const mountPointValues = nextValue.map(value => value.mount_point);

    nextValue.forEach((value,index) => {
      const count = mountPointValues.filter(mountPoint => mountPoint === value.mount_point).length;

      if(value?.mount_point !== prevValue[index]?.mount_point && count > 1) {
        this.ldspFaDevices.controls[index].get('mount_point')?.setErrors({ notUnique: true });
      }
    });
  }

  private preferredNTPServerValidation(control: AbstractControl): {[key: string]: boolean} | null {
    if (!control.value) {
      return null;
    }

    const IP_REGEX = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    const DOMAIN_REGEX = /^[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$/;

    if(control.value.match(IP_REGEX) || control.value.match(DOMAIN_REGEX)) {
      return null;
    } else {
      return {invalidFormat: true};
    }
  }

  private findSoftware(element: any): boolean {
    return element.purpose === 'software' ? element : false;
  }

  private findDiag(element: any): boolean {
    return element.purpose === 'diag' ? element : false;
  }

  private findNotSwap(element: any): boolean {
    return element.purpose !== 'swap' ? element : false;
  }

  private validateSwap(): void {
    let tempArray: any[] = [];

    this.ldspFaDevices.value.forEach((element: any) => {
      tempArray.push(element.purpose)
    });

    const notSwap = tempArray.find((element: any) => {
      return element === 'diag' || element === 'software';
    });



    if (
      (tempArray.length === 1 && tempArray[0] === 'swap') ||
      (tempArray.length > 1 && !notSwap)
    ) {
      tempArray.forEach((el, i) => {
        this.ldspFaDevices.controls[i].get('purpose')?.setErrors({'incorrectSwap': true});
      });
    }

    if (tempArray.length > 1 && notSwap) {
      tempArray.forEach((el, i) => {
        this.ldspFaDevices.controls[i].get('purpose')?.setErrors(null);
      });
    }
  }
}

