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

import { By } from '@angular/platform-browser';
import { DebugElement } from "@angular/core";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CUSTOM_ELEMENTS_SCHEMA } from "@angular/core";
import { RouterTestingModule } from '@angular/router/testing';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormArray, AbstractControl } from "@angular/forms";
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatRippleModule } from '@angular/material/core';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { of } from 'rxjs';

import { ConfigEditorComponent } from './config-editor.component';

import { redundancyOptions } from './config-editor.data';
import { Mapping } from "@app-interfaces/mapping";

import { ConfigEditorService } from '@app-services/config-editor/config-editor.service';
import { MockConfigEditorService } from '@app-services/config-editor/mock-config-editor.service.spec';
import { MockUtilService } from '@app-services/util/mock-util-service.spec';
import { MockMappingService } from '@app-services/migration-mapper/mock-mapping.service.spec';
import { TargetsService } from '@app-services/targets/targets.service';
import { MockTargetsService } from '@app-services/targets/mock-targets.service.spec';
import { UtilService } from '@app-services/util/util.service';
import { MappingService } from '@app-services/migration-mapper/mapping.service';
import { NgxMaskModule } from 'ngx-mask';
import { MatTooltipModule } from '@angular/material/tooltip';

const activatedRouteMock = {
  queryParams: of({
      databaseId: '123',
  }),
};


xdescribe('ConfigEditorComponent', () => {
let component:ConfigEditorComponent;
let fixture: ComponentFixture<ConfigEditorComponent>;
let formBuilder: FormBuilder;
let configEditorService: ConfigEditorService;
const mockUtilService: UtilService = new MockUtilService() as UtilService;
const mockMappingService: MappingService = new MockMappingService() as MappingService;
const mockTargetsService: TargetsService = new MockTargetsService() as TargetsService;
const mockConfigEditorService: ConfigEditorService = new MockConfigEditorService() as ConfigEditorService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        FormsModule, ReactiveFormsModule, RouterTestingModule, MatSelectModule, MatAutocompleteModule, MatTooltipModule,
        MatSlideToggleModule, MatInputModule, MatRippleModule, BrowserAnimationsModule, MatCheckboxModule, MatSnackBarModule,
        NgxMaskModule.forRoot({
          validation: false,
        }) 
      ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [ ConfigEditorComponent ],
      providers: [
        {provide: UtilService, useValue: mockUtilService},
        {provide: MappingService, useValue: mockMappingService},
        {provide: TargetsService, useValue: mockTargetsService},
        { provide: ActivatedRoute, useValue: activatedRouteMock },
        {provide: ConfigEditorService, useValue: mockConfigEditorService},
        {provide: HttpClient, useValue: null}
      ]
    })
    .compileComponents();
    fixture = TestBed.createComponent(ConfigEditorComponent);
    component = fixture.componentInstance;
    configEditorService = TestBed.inject(ConfigEditorService);
    localStorage.setItem('currentProjectId', '1');
    component.mappings = {
      db_type: 'RAC'
    } as Mapping;
    formBuilder = TestBed.inject(FormBuilder);
    fixture.detectChanges();
  });

  afterEach(() => {
    fixture.destroy();
  });

  function prepareFormWithoutSwap() {
    component.configEditorForm = formBuilder.group({
      created_at: null,
      misc_config_values: formBuilder.group({
        oracle_root: '/app',
        ntp_preferred: '192.168.1.1',
        role_separation: true,
        compatible_rdbms: '11.2',
        asm_disk_management: 'Udev',
        swap_blk_device: '',
        is_swap_configured: false
      }),
      data_mounts_values: formBuilder.array([
        formBuilder.group({
          purpose: 'diag',
          blk_device: '/dev/sdd',
          name: '01',
          fstype: ' ',
          mount_point: '/u01',
          mount_opts: ' '
        })
      ]),
      asm_config_values: formBuilder.array([
        formBuilder.group({
          diskgroup: 'DATA',
          au_size: '4M',
          redundancy: 'EXTERNAL',
          disks: formBuilder.array([
            formBuilder.group({
              blk_device: '/dev/sdc',
              size: '10',
              name: 'test'
            })
          ])
        })
      ]),
      install_config_values: formBuilder.group({
        oracle_user: 'oracle',
        oracle_group: 'oinstall',
        home_name: 'dbhome_1',
        grid_user: 'grid',
        grid_group: 'oinstall'
      }),
      db_params_values: formBuilder.group({
        db_name: 'APPDB_3891'
      }),
      is_configured: true,
      rac_config_values: formBuilder.group({
        cluster_name: 'cluster',
        cluster_domain: 'domain',
        scan_name: 'scan',
        scan_port: 500,
        scan_ip1: '192.168.1.1',
        scan_ip2: '192.168.1.2',
        scan_ip3: '192.168.1.3',
        public_net: 'public',
        private_net: 'private',
        dg_name: 'DATA',
        rac_nodes: formBuilder.array([
          formBuilder.group({
            node_id: 17,
            vip_name: 'vip',
            vip_ip: '192.168.1.1',
            node_ip: '172.25.9.39'
          })
        ])
      })
    })

    fixture.detectChanges();
  }

  it('initValueMiscConfigValues', () => {
    component.configEditorForm = formBuilder.group({
      misc_config_values: formBuilder.group({
        oracle_root: '',
        ntp_preferred: '',
        role_separation: '',
        compatible_asm: '',
        compatible_rdbms: '',
        asm_disk_management: '',
        swap_blk_device: '',
        is_swap_configured: false
      }),
    });
    component.compatible = new Map([
      ['19.0', ['19.0', '18.0', '12.2', '12.1', '11.2']],
      ['18.0', ['18.0', '12.2', '12.1', '11.2']],
      ['12.2', ['12.2', '12.1', '11.2']],
      ['12.1', ['12.1', '11.2']],
      ['11.2', ['11.2']],
    ]);
    component['initValueMiscConfigValues']({
      oracle_version: '18.0.0.0'
    } as Mapping);

    expect(component['oracle_version']).toEqual('18.0');
    expect(component['rdbmsValues']).toEqual(['18.0', '12.2', '12.1', '11.2']);
    expect(component.configEditorForm.get('misc_config_values')?.get('compatible_asm')?.value).toEqual('18.0');
    expect(component.configEditorForm.get('misc_config_values')?.get('compatible_rdbms')?.value).toEqual('18.0');
    component.configEditorForm.get('misc_config_values')?.get('compatible_asm')?.setValue('11.2');
    expect(component.configEditorForm.get('misc_config_values')?.get('compatible_rdbms')?.value).toEqual('11.2');
  });

  it('should set value for oracle_root as mount_point + /app value', async () => {
    const el = fixture.debugElement.query(By.css('#mount-point'));
    const purpose = fixture.debugElement.query(By.css('#purpose'));

    purpose.nativeElement.value ='';
    purpose.nativeElement.dispatchEvent(new Event('select'));
    fixture.detectChanges();
    
    el.nativeElement.value ='';
    el.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    purpose.nativeElement.value ='software';
    purpose.nativeElement.dispatchEvent(new Event('select'));
    fixture.detectChanges();
    
    el.nativeElement.value ='/mount';
    el.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    await fixture.whenStable().then(()=> {
      expect(component.configEditorForm?.get('misc_config_values')?.get('oracle_root')?.value).toEqual('/mount/app');
    });
  });

  it('should set value for oracle_root as mount_point + /app value', async () => {
    const el = fixture.debugElement.query(By.css('#mount-point'));
    const purpose = fixture.debugElement.query(By.css('#purpose'));

    purpose.nativeElement.value ='';
    purpose.nativeElement.dispatchEvent(new Event('select'));
    fixture.detectChanges();
    
    el.nativeElement.value ='';
    el.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    purpose.nativeElement.value ='diag';
    purpose.nativeElement.dispatchEvent(new Event('select'));
    fixture.detectChanges();
    
    el.nativeElement.value ='/u1';
    el.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    await fixture.whenStable().then(()=> {
      expect(component.configEditorForm?.get('misc_config_values')?.get('oracle_root')?.value).toEqual('/u1/app');
    });
  });

  describe('cluster-name field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#cluster-name'));
    });

    it('should set maxlength error for cluster-name field', async () => {
      el.nativeElement.value = '0123456789123456';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('cluster_name')?.hasError('maxlength')).toEqual(true);
        expect(component.configEditorForm?.get('rac_config_values')?.get('cluster_name')?.hasError('required')).toEqual(false);
      });
    });

    it('should not set errors for cluster-name field', async () => {
      el.nativeElement.value = 'name123';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('cluster_name')?.hasError('maxlength')).toEqual(false);
        expect(component.configEditorForm?.get('rac_config_values')?.get('cluster_name')?.hasError('required')).toEqual(false);
        expect(component.configEditorForm?.get('rac_config_values')?.get('cluster_name')?.hasError('pattern')).toEqual(false);
      });
    });

    it('should set required error for cluster-name field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('cluster_name')?.hasError('required')).toEqual(true);
      });
    });

    it('should set pattern error for cluster-name field', async () => {
      el.nativeElement.value = '_';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('cluster_name')?.hasError('pattern')).toEqual(true);
      });
    });
  });

  describe('scan-port field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#scan-port'));
    });

    it('should set required error for scan-port field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_port')?.hasError('required')).toEqual(true);
      });
    });

    it('should set max error for scan-port field', async () => {
      el.nativeElement.value = '65536';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_port')?.hasError('max')).toEqual(true);
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_port')?.hasError('required')).toEqual(false);
      });
    });

    it('should set min error for scan-port field', async () => {
      el.nativeElement.value = '0';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_port')?.hasError('min')).toEqual(true);
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_port')?.hasError('required')).toEqual(false);
      });
    });

    it('should not set errors for scan-port field', async () => {
      el.nativeElement.value = '65534';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_port')?.hasError('max')).toEqual(false);
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_port')?.hasError('required')).toEqual(false);
      });
    });
  });

  describe('scan-ip1 field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#scan-ip1'));
    });

    it('should set required error for scan-ip1 field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip1')?.hasError('required')).toEqual(true);
      });
    });

    it('should set pattern error for scan-ip1 field', async () => {
      el.nativeElement.value = '277.0.0.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip1')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set errors for scan-ip1 field', async () => {
      el.nativeElement.value = '121.3.4.0';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip1')?.hasError('required')).toEqual(false);
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip1')?.hasError('pattern')).toEqual(false);
      });
    });
  });

  describe('scan-ip2 field', () => {
    let el: DebugElement;
    let scanIp1: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#scan-ip2'));
      scanIp1 = fixture.debugElement.query(By.css('#scan-ip1'));
      component.configEditorForm.setValidators(component.checkScanIpValidator());
    });

    it('should set pattern error for scan-ip2 field', async () => {
      el.nativeElement.value = '277.0.0.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip2')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set error for scan-ip2 field', async () => {
      el.nativeElement.value = '121.3.4.0';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip2')?.hasError('pattern')).toEqual(false);
      });
    });

    it('should set notUnique error for scan-ip2 field', async () => {
      scanIp1.nativeElement.value = '1.1.1.1';
      scanIp1.triggerEventHandler('input', {
        target: scanIp1.nativeElement,
      });
      el.nativeElement.value = '1.1.1.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();     
      
      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip2')?.hasError('notUnique')).toEqual(true);
      });
    });
  });

  describe('scan-ip3 field', () => {
    let el: DebugElement;
    let scanIp1: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#scan-ip3'));
      scanIp1 = fixture.debugElement.query(By.css('#scan-ip1'));
      component.configEditorForm.setValidators(component.checkScanIpValidator());
    });

    it('should set pattern error for scan-ip3 field', async () => {
      el.nativeElement.value = '277.0.0.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip3')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set error for scan-ip3 field', async () => {
      el.nativeElement.value = '121.3.4.0';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip3')?.hasError('pattern')).toEqual(false);
      });
    });

    it('should set notUnique error for scan-ip3 field', async () => {
      scanIp1.nativeElement.value = '1.1.1.1';
      scanIp1.triggerEventHandler('input', {
        target: scanIp1.nativeElement,
      });
      el.nativeElement.value = '1.1.1.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('rac_config_values')?.get('scan_ip3')?.hasError('notUnique')).toEqual(true);
      });
    });
  });

  describe('validateSwap', () => { 
    it('should incorrectSwap to be false', () => {
      component.configEditorForm = formBuilder.group({
        data_mounts_values: formBuilder.array([
          formBuilder.group({
            purpose: 'diag',
            blk_device: '',
            name: '',
            fstype: '',
            mount_point: '',
            mount_opts: '',
          }),
          formBuilder.group({
            purpose: 'swap',
            blk_device: '',
            name: '',
            fstype: '',
            mount_point: '',
            mount_opts: '',
          }),
        ]),
        misc_config_values: formBuilder.group({
          oracle_root: ''
        })
      });
  
      component['validateSwap']();
  
      expect(component.ldspFaDevices?.controls[0]?.get('purpose')?.hasError('incorrectSwap')).toEqual(false);
      expect(component.ldspFaDevices?.controls[1]?.get('purpose')?.hasError('incorrectSwap')).toEqual(false);
    });
  
    it('should incorrectSwap to be true', () => {
      component.configEditorForm = formBuilder.group({
        data_mounts_values: formBuilder.array([
          formBuilder.group({
            purpose: 'swap',
            blk_device: '',
            name: '',
            fstype: '',
            mount_point: '',
            mount_opts: '',
          }),
        ]),
        misc_config_values: formBuilder.group({
          oracle_root: ''
        })
      });
  
      component['validateSwap']();
  
      expect(component.ldspFaDevices?.controls[0]?.get('purpose')?.hasError('incorrectSwap')).toEqual(true);
    });
  
    it('should not submit form if swap is not configured if the oracle version is less than 18', () => {
      spyOn(component['subscriptions'], 'push');
      spyOn(component, 'prepareForm').and.callThrough();
      spyOn(component, 'openSnackBar');
      spyOn(configEditorService, 'createConfigEditorsingleInstance');
  
      prepareFormWithoutSwap();
      component['initValueMiscConfigValues']({
        oracle_version: '11.2.0.0'
      } as Mapping);
  
      const submitBtn = fixture.debugElement.query(By.css('button[type=submit]')).nativeElement;
      submitBtn.click();
      fixture.detectChanges();
  
      expect(component.prepareForm).toHaveBeenCalledTimes(1);
      expect(component.openSnackBar).toHaveBeenCalledTimes(1);
      expect(configEditorService.createConfigEditorsingleInstance).toHaveBeenCalledTimes(0);
    });
  
    it('should set error on swap checkbox if swap is already configured', async() => {
      prepareFormWithoutSwap();
      fixture.detectChanges();
  
      const inputElement = fixture.debugElement.query(By.css('#purpose'));
      inputElement.nativeElement.dispatchEvent(new Event('focusin'));
      inputElement.nativeElement.dispatchEvent(new Event('input'));
  
      
      fixture.detectChanges();
      await fixture.whenStable();
      fixture.detectChanges();
  
      const matOptions = document.querySelectorAll('mat-option');
      const optionToClick = matOptions[2] as HTMLElement;
      optionToClick.click();
      fixture.detectChanges();
  
      const swapCheckbox = fixture.debugElement.query(By.css('.mat-checkbox-input')).nativeElement;
      swapCheckbox.click();
      fixture.detectChanges();
  
      await fixture.whenStable().then(() => {
        expect(component.configEditorForm?.get('misc_config_values')?.get('is_swap_configured')?.hasError('swapIsAlreadyConfigured')).toEqual(true);
      })
    });

    it('should set error on swap select if swap checkbox is already checked', async() => {
      prepareFormWithoutSwap();
      fixture.detectChanges();

      const swapCheckbox = fixture.debugElement.query(By.css('.mat-checkbox-input')).nativeElement;
      swapCheckbox.click();
      fixture.detectChanges();

      const addDevice = fixture.debugElement.query(By.css('.row-with-button')).nativeElement;
      addDevice.click();
      fixture.detectChanges();
  
      const inputElement = fixture.debugElement.queryAll(By.css('#purpose'))[1];
      inputElement.nativeElement.dispatchEvent(new Event('focusin'));
      inputElement.nativeElement.dispatchEvent(new Event('input'));
  
      fixture.detectChanges();
      await fixture.whenStable();
      fixture.detectChanges();
  
      const matOptions = document.querySelectorAll('mat-option');
      const optionToClick = matOptions[2] as HTMLElement;
      optionToClick.click();
      fixture.detectChanges();
  
      await fixture.whenStable().then(() => {
        expect(component.ldspFaDevices?.controls[1]?.get('purpose')?.hasError('swapIsAlreadyConfigured')).toEqual(true);
      })
    });
  })

  describe('vip-ip field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#vip-ip'));
    });

    it('should set required error for vip-ip field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect((component.configEditorForm.get('rac_config_values')?.get('rac_nodes') as FormArray)?.controls[0]?.get('vip_ip')?.hasError('required')).toEqual(true);
      });
    });

    it('should set pattern error for vip-ip field', async () => {
      el.nativeElement.value = '277.2.0.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect((component.configEditorForm.get('rac_config_values')?.get('rac_nodes') as FormArray)?.controls[0]?.get('vip_ip')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set errors for vip-ip field', async () => {
      el.nativeElement.value = '121.2.0.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect((component.configEditorForm.get('rac_config_values')?.get('rac_nodes') as FormArray)?.controls[0]?.get('vip_ip')?.hasError('pattern')).toEqual(false);
        expect((component.configEditorForm.get('rac_config_values')?.get('rac_nodes') as FormArray)?.controls[0]?.get('vip_ip')?.hasError('required')).toEqual(false);
      });
    });
  });

  describe('oracle-user field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#oracle-user'));
    });

    it('should set required error for oracle-user field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_user')?.hasError('required')).toEqual(true);
      });
    });

    it('should set maxlength error for oracle-user field', async () => {
      el.nativeElement.value = 'aaaaabbbbbcccccdddddeeeeefffffg';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_user')?.hasError('maxlength')).toEqual(true);
      });
    });

    it('should set pattern error for oracle-user field', async () => {
      el.nativeElement.value = 'wrong oracle user name!';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_user')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set errors for oracle-user field', async () => {
      el.nativeElement.value = 'oracle_name.';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_user')?.hasError('required')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_user')?.hasError('maxlength')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_user')?.hasError('pattern')).toEqual(false);
      });
    });
  });

  describe('oracle-group field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#oracle-group'));
    });

    it('should set required error for oracle-group field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_group')?.hasError('required')).toEqual(true);
      });
    });

    it('should set maxlength error for oracle-group field', async () => {
      el.nativeElement.value = 'aaaaabbbbbcccccdddddeeeeefffffg';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_group')?.hasError('maxlength')).toEqual(true);
      });
    });

    it('should set pattern error for oracle-group field', async () => {
      el.nativeElement.value = 'wrong oracle group name!';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_group')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set errors for oracle-group field', async () => {
      el.nativeElement.value = 'oracle_group.';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_group')?.hasError('required')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_group')?.hasError('maxlength')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('oracle_group')?.hasError('pattern')).toEqual(false);
      });
    });
  });

  describe('grid-user field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#grid-user'));
    });

    it('should set required error for grid-user field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_user')?.hasError('required')).toEqual(true);
      });
    });

    it('should set maxlength error for grid-user field', async () => {
      el.nativeElement.value = 'aaaaabbbbbcccccdddddeeeeefffffg';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_user')?.hasError('maxlength')).toEqual(true);
      });
    });

    it('should set pattern error for grid-user field', async () => {
      el.nativeElement.value = 'wrong grid user name!';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_user')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set errors for grid-user field', async () => {
      el.nativeElement.value = 'grid_user.';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_user')?.hasError('required')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_user')?.hasError('maxlength')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_user')?.hasError('pattern')).toEqual(false);
      });
    });
  });

  describe('grid-group field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#grid-group'));
    });

    it('should set required error for grid-group field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_group')?.hasError('required')).toEqual(true);
      });
    });

    it('should set maxlength error for grid-group field', async () => {
      el.nativeElement.value = 'aaaaabbbbbcccccdddddeeeeefffffg';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_group')?.hasError('maxlength')).toEqual(true);
      });
    });

    it('should set pattern error for grid-group field', async () => {
      el.nativeElement.value = 'wrong grid group name!';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_group')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set errors for grid-group field', async () => {
      el.nativeElement.value = 'grid_group.';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_group')?.hasError('required')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_group')?.hasError('maxlength')).toEqual(false);
        expect(component.configEditorForm?.get('install_config_values')?.get('grid_group')?.hasError('pattern')).toEqual(false);
      });
    });
  });

  describe('local storage name field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#local-storage-name'));
    });

    it('should set required error for name field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.ldspFaDevices?.controls[0].get('name')?.hasError('required')).toEqual(true);
      });
    });

    it('should set pattern error for name field', async () => {
      el.nativeElement.value = ' space';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.ldspFaDevices?.controls[0].get('name')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should not set errors for name field', async () => {
      el.nativeElement.value = 'name';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.ldspFaDevices?.controls[0].get('name')?.hasError('required')).toEqual(false);
        expect(component.ldspFaDevices?.controls[0].get('name')?.hasError('pattern')).toEqual(false);
      });
    });
  });

  describe('mount-point field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#mount-point'));
    });

    it('should set required error for mount-point field', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.ldspFaDevices?.controls[0].get('mount_point')?.hasError('required')).toEqual(true);
      });
    });

    it('should set pattern error for mount-point field', async () => {
      el.nativeElement.value = '123';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.ldspFaDevices?.controls[0].get('mount_point')?.hasError('pattern')).toEqual(true);
      });
    });

    it('should set unique error for mount-point field', async () => {
      function mockCheckMountPointValidator(control: AbstractControl) {
        const mountPointsValues = ['/u01','/u03'];
        mountPointsValues.push(control.value);

        const count = mountPointsValues.filter((item: string) => item === control.value).length;

        return count > 1 ? of({ notUnique: true }) : of(null);
      }

      component.ldspFaDevices?.controls[0].get('mount_point')?.clearAsyncValidators();
      component.ldspFaDevices?.controls[0].get('mount_point')?.setAsyncValidators(mockCheckMountPointValidator.bind(this));
      fixture.detectChanges();


      el.nativeElement.value = '/u01';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();


      await fixture.whenStable().then(()=> {
        expect(component.ldspFaDevices?.controls[0].get('mount_point')?.hasError('notUnique')).toEqual(true);
      });
    });

    it('should not set errors for mount-point field', async () => {
      el.nativeElement.value = '/uo1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.ldspFaDevices?.controls[0].get('mount_point')?.hasError('required')).toEqual(false);
        expect(component.ldspFaDevices?.controls[0].get('mount_point')?.hasError('pattern')).toEqual(false);
      });
    });
  });

  describe('ntp-preferred field', () => {
    let el: DebugElement;

    beforeEach(() => {
      el = fixture.debugElement.query(By.css('#ntp-preferred'));
    });

    it('should not set error for ntp-preferred field if the field is empty', async () => {
      el.nativeElement.value = '';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('misc_config_values')?.get('ntp_preferred')?.hasError('invalidFormat')).toEqual(false);
      });
    });

    it('should set invalidFormat error for ntp-preferred field if the format of IP address is invalid', async () => {
      el.nativeElement.value = '277.0.0.1';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('misc_config_values')?.get('ntp_preferred')?.hasError('invalidFormat')).toEqual(true);
      });
    });

    it('should set invalidFormat error for ntp-preferred field if the format of domain is invalid', async () => {
      el.nativeElement.value = 'wrongdomain';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('misc_config_values')?.get('ntp_preferred')?.hasError('invalidFormat')).toEqual(true);
      });
    });

    it('should not set errors for ntp-preferred field if the format is IP address', async () => {
      el.nativeElement.value = '121.3.4.0';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('misc_config_values')?.get('ntp_preferred')?.hasError('invalidFormat')).toEqual(false);
      });
    });

    it('should not set errors for ntp-preferred field if the format is domain.com', async () => {
      el.nativeElement.value = 'my-domain_check.com';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('misc_config_values')?.get('ntp_preferred')?.hasError('invalidFormat')).toEqual(false);
      });
    });

    it('should not set errors for ntp-preferred field if the format is domain.gov.uk', async () => {
      el.nativeElement.value = 'domain.gov.uk';
      el.triggerEventHandler('input', {
        target: el.nativeElement,
      });
      fixture.detectChanges();

      await fixture.whenStable().then(()=> {
        expect(component.configEditorForm?.get('misc_config_values')?.get('ntp_preferred')?.hasError('invalidFormat')).toEqual(false);
      });
    });
  });



  it('removeDiskGroup, should not remove DiskGroup', () => {
    component.configEditorForm = formBuilder.group({
      asm_config_values: formBuilder.array([
        formBuilder.group({
          diskgroup: '',
          au_size: '',
          redundancy: '',
          disks: [{
            blk_device: '',
            size: '',
            name: ''
          }]
        }),
      ])
    });

    component.removeDiskGroup(0);

    expect(component.asmFaData.length).toEqual(1);
  });

  it('removeDiskGroup, should remove DiskGroup', () => {
    component.configEditorForm = formBuilder.group({
      asm_config_values: formBuilder.array([
        formBuilder.group({
          diskgroup: 'a',
          au_size: 'a',
          redundancy: 'a',
          disks: [{
            blk_device: 'a',
            size: 'a',
            name: 'a'
          }]
        }),
        formBuilder.group({
          diskgroup: 'b',
          au_size: 'b',
          redundancy: 'b',
          disks: [{
            blk_device: 'b',
            size: 'b',
            name: 'b'
          }]
        })
      ])
    });

    component.removeDiskGroup(0);

    expect(component.asmFaData.length).toEqual(1);
  });

  it('should added device', () => {
    component.configEditorForm = formBuilder.group({
      data_mounts_values: formBuilder.array([
        formBuilder.group({
          purpose: '',
          blk_device: '',
          name: '',
          fstype: '',
          mount_point: '',
          mount_opts: '',
        }),
      ])
    });

    component.addDevice();

    expect(component.devices.length).toEqual(2);
  });

  it('should show redundancy Options for oracle versions lower 12.2', () => {
    const a = redundancyOptions.filter(item => !item.is_new_version);
    component.initRedundancy('12.1');
    expect(component.redundancyOptions).toEqual(a);
  });
  it('should show redundancy Options for oracle versions higher 12.1', () => {
    const a = redundancyOptions;
    expect(component.redundancyOptions).toEqual(a);
  });
  it('should disable redundancy option depending on devices amount, when device amount is 1 active is only EXTERNAL', async () => {
    const redundancySelect = fixture.debugElement.query(By.css('.redundancy .mat-select-trigger')).nativeElement;
    redundancySelect.click();
    fixture.detectChanges();
    await fixture.whenStable().then(() => {
      const redundancyOptionsList = fixture.debugElement.queryAll(By.css('mat-option'));
      expect(redundancyOptionsList.length).toEqual(redundancyOptions.length);
      const disabledRedundancyOptions = fixture.debugElement.queryAll(By.css('mat-option.mat-option-disabled'));
      expect(disabledRedundancyOptions.length).toEqual(redundancyOptions.length - 1);
      const activeRedundancyOption = fixture.debugElement.query(By.css('mat-option:not(.mat-option-disabled)'));
      const activeRedundancyOptionText = activeRedundancyOption.query(By.css('.mat-option-text')).nativeElement.innerHTML;
      expect(activeRedundancyOptionText).toEqual(redundancyOptions[0].text);
    });
  });
  it('should disable redundancy option depending on devices amount, when device amount is 2 EXTERNAL and NORMAL are active', async () => {
    const addDeviceLink = fixture.debugElement.query(By.css('.add-device')).nativeElement;
    addDeviceLink.click();
    expect(fixture.debugElement.queryAll(By.css('.devices-list tr')).length).toEqual(2);
    const redundancySelect = fixture.debugElement.query(By.css('.redundancy .mat-select-trigger')).nativeElement;
    redundancySelect.click();
    fixture.detectChanges();
    await fixture.whenStable().then(() => {
      const activeRedundancyOptions = fixture.debugElement.queryAll(By.css('mat-option:not(.mat-option-disabled)'));
      expect(activeRedundancyOptions.length).toEqual(2);
      const disabledRedundancyOption = fixture.debugElement.queryAll(By.css('mat-option.mat-option-disabled'));
      expect(disabledRedundancyOption.length).toEqual(3);
    });
  });
  it('should disable redundancy option depending on devices amount, when device amount is 3 all options are active', async () => {
    const addDeviceLink = fixture.debugElement.query(By.css('.add-device')).nativeElement;
    addDeviceLink.click();
    fixture.detectChanges();
    addDeviceLink.click();
    expect(fixture.debugElement.queryAll(By.css('.devices-list tr')).length).toEqual(3);
    const redundancySelect = fixture.debugElement.query(By.css('.redundancy .mat-select-trigger')).nativeElement;
    redundancySelect.click();
    fixture.detectChanges();
    await fixture.whenStable().then(() => {
      const activeRedundancyOptions = fixture.debugElement.queryAll(By.css('mat-option:not(.mat-option-disabled)'));
      expect(activeRedundancyOptions.length).toEqual(redundancyOptions.length);
    });
  });

  it('should show default values in ASM configuration if no data from backend is available', async() => {
    const auSizeSelect = fixture.debugElement.query(By.css('[formControlName=au_size] .mat-select-trigger')).nativeElement;
    auSizeSelect.click();
    const redundancySelect = fixture.debugElement.query(By.css('[formControlName=redundancy] .mat-select-trigger')).nativeElement;
    redundancySelect.click();
    fixture.detectChanges();

    const auSizeSelectedText = auSizeSelect.querySelector('.mat-select-min-line').textContent;
    const redundancySelectedText = redundancySelect.querySelector('.mat-select-min-line').textContent;
    expect(auSizeSelectedText).toEqual('4M');
    expect(redundancySelectedText).toEqual('EXTERNAL');
  })

  it('should save draft with unvalid fields', async() => {
    spyOn(component, 'saveDraft').and.callThrough();
    spyOn(component, 'prepareForm');
    spyOn(component, 'openSnackBar');
    const draftBtn = fixture.debugElement.query(By.css('.draft-btn')).nativeElement;
    draftBtn.click();
    fixture.detectChanges();
    await fixture.whenStable().then(()=> {
      expect(component.saveDraft).toHaveBeenCalledTimes(1);
      expect(component.prepareForm).toHaveBeenCalledTimes(1);
		  expect(component.openSnackBar).toHaveBeenCalledWith('Configuration Draft is saved', 'OK');
    });
  })

  it('should disable form if the database is successfully deployed', async() => {
    component.mappings!.is_deployed = true;
    component.checkDisableForm(component.mappings!);
    fixture.detectChanges();
    
    const roleSeparationSwitcher = fixture.debugElement.query(By.css('.custom-switcher')).nativeElement;
    const ntpPreferred = fixture.debugElement.query(By.css('#ntp-preferred')).nativeElement;
    const purposeSelect = fixture.debugElement.query(By.css('#purpose')).nativeElement;
    const oracleUser = fixture.debugElement.query(By.css('#oracle-user')).nativeElement;
    const clusterName = fixture.debugElement.query(By.css('#cluster-name')).nativeElement;
    const vipIP = fixture.debugElement.query(By.css('#vip-ip')).nativeElement;

    await fixture.whenStable().then(()=> {
      expect(roleSeparationSwitcher.classList.contains('mat-disabled')).toEqual(true);
      expect(ntpPreferred.disabled).toEqual(true);
      expect(purposeSelect.disabled).toEqual(true);
      expect(oracleUser.disabled).toEqual(true);
      expect(clusterName.disabled).toEqual(true);
      expect(vipIP.disabled).toEqual(true);
    });
  })
});
