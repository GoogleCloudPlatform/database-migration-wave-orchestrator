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

interface BaseOptions {
  id?: number,
  text: string,
  value:string,
  selected?: boolean,
  size_gb?: string
}


const dataMountPurposeOptions: BaseOptions[] = [
  { text: 'software', value:'software'},
  { text: 'diag', value:'diag'},
  { text: 'swap', value: 'swap'}
]

const redundancyOptions = [
  {value: 'EXTERNAL' , text: 'EXTERNAL', disks_number: 1, is_new_version: false},
  {value: 'NORMAL' , text: 'NORMAL', disks_number: 2, is_new_version: false},
  {value: 'FLEX' , text: 'FLEX', disks_number: 3, is_new_version: true},
  {value: 'HIGH' , text: 'HIGH', disks_number: 3, is_new_version: false},
  {value: 'EXTENDED' , text: 'EXTENDED', disks_number: 3, is_new_version: true}
]

const auSizeOptions = [
  {value: '1M' , text: '1M'},
  {value: '2M' , text: '2M'},
  {value: '4M' , text: '4M'},
  {value: '8M' , text: '8M'},
  {value: '16M' , text: '16M'},
  {value: '32M' , text: '32M'},
  {value: '64M' , text: '64M'},
]    

interface LocalDataStorageInt {
  device:  {text:string , value: string}[],
  purpose: {text:string , value: string}[]
}

const localDataStorageParamters: LocalDataStorageInt = {
  device : [
    {text : '' , value : ''},
    {text : '' , value : ''},
    {text : '' , value : ''}
  ],
  purpose : [
    {text : '' , value : ''}
  ]
}

const asmDiskOptionSelect = [
  { text: 'Udev', value:'Udev'},
  { text: 'ASMLib', value: 'ASMLib'}
]

interface errorInfo {
  error: boolean,
  value: number
}

export {localDataStorageParamters, errorInfo, dataMountPurposeOptions, BaseOptions, redundancyOptions, asmDiskOptionSelect, auSizeOptions}
