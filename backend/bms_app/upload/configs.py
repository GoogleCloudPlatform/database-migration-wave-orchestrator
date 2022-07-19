# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ORACLE_FILE_NAMES_MAP = {
    '12.1.0.2.0 ': {
        'Base - eDelivery': [
            {
                'files': {'V46095-01_1of2.zip', 'V46095-01_2of2.zip'},
                'name': 'Oracle Database 12.1.0.2.0 for Linux x86-64'
            },
            {   'files': {'V77388-01_1of2.zip', 'V77388-01_2of2.zip'},
                'name': 'Oracle Database 12c Standard Edition 2 12.1.0.2.0 for Linux x86-64'},
            {
                'files': {'V46096-01_1of2.zip', 'V46096-01_2of2.zip'},
                'name': 'Oracle Grid Infrastructure 12.1.0.2.0 for Linux x86-64'
            }
        ]
    },
    '12.2.0.1.0': {
        'Patch - MOS': [
            {
                'files': {'p32579057_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.210420 + 12.2.0.1.210420 GIAPR2021RU'
            },
            {
                'files': {'p32126883_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.210119 + 12.2.0.1.210119 GIJAN2021RU'
            },
            {
                'files': {'p31720486_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.201020 + 12.2.0.1.201020 GIOCT2020RU'
            },
            {
                'files': {'p31326390_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.200714 + 12.2.0.1.200714 GIJUL2020RU'},
            {
                'files': {'p30783652_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.200414 12.2.0.1.200414 GIAPR2020RU'},
            {
                'files': {'p30463673_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.200114 12.2.0.1.200114 GIJAN2020RU'},
            {
                'files': {'p30133386_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.191015 12.2.0.1.191015 GIOCT2019RU'},
            {
                'files': {'p29699173_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.190716 + 12.2.0.1.190716 GIJUL2019RU'},
            {
                'files': {'p29252072_122010_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 12.2.0.1.190416 + 12.2.0.1.190416 GIAPR2019RU'},
            {
                'files': {'p25078431_122010_Linux-x86-64.zip'},
                'name': 'ACFS MODULE ORACLEACFS.KO FAILS TO LOAD ON OL7U3 SERVER WITH RHCK (Patch) patch 25078431 for Linux x86-64'},
            {
                'files': {'p6880880_122010_Linux-x86-64.zip'},
                'name': 'OPatch Utility'
            }
        ]
    },
    '18.0.0.0.0 ': {
        'Patch - MOS': [
            {
                'files': {'p32579024_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.14.0.0.210420 + GI RU 18.14.0.0.210420'
            },
            {
                'files': {'p32126862_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.13.0.0.210119 + GI RU 18.13.0.0.210119'
            },
            {
                'files': {'p31720457_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.12.0.0.201020 + GI RU 18.12.0.0.201020'
            },
            {
                'files': {'p31326376_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.11.0.0.200714 + GI RU 18.11.0.0.200714'},
            {
                'files': {'p30783607_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.10.0.0.200414 GI RU 18.10.0.0.200414'
            },
            {
                'files': {'p30463635_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.9.0.0.200114 GI RU 18.9.0.0.200114'
            },
            {
                'files': {'p30133246_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.8.0.0.191015 GI RU 18.8.0.0.191015'
            },
            {
                'files': {'p29699160_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.7.0.0.190716 + GI RU 18.7.0.0.190716'
            },
            {
                'files': {'p29251992_180000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 18.6.0.0.190416 + GI RU 18.6.0.0.190416'},
            {
                'files': {'p6880880_180000_Linux-x86-64.zip'},
                'name': 'OPatch Utility'
                }
        ]
    },
    '19.3.0.0.0': {
        'Patch - MOS': [
            {
                'files': {'p32578973_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.11.0.0.210420 + GI RU 19.11.0.0.210420'
            },
            {
                'files': {'p32126842_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.10.0.0.210119 + GI RU 19.10.0.0.210119'
            },
            {
                'files': {'p31720429_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.9.0.0.201020 + GI RU 19.9.0.0.201020'
            },
            {
                'files': {'p31326369_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.8.0.0.200714 + GI RU 19.8.0.0.200714'
            },
            {
                'files': {'p30783556_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.7.0.0.200414 + GI RU 19.7.0.0.200414'},
            {
                'files': {'p30463609_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.6.0.0.200114 GI RU 19.6.0.0.200114'},
            {
                'files': {'p30133178_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.5.0.0.191015 GI RU 19.5.0.0.191015'},
            {
                'files': {'p29699097_190000_Linux-x86-64.zip'},
                'name': 'COMBO OF OJVM RU COMPONENT 19.4.0.0.190716 + GI RU 19.4.0.0.190716'},
            {
                'files': {'p6880880_190000_Linux-x86-64.zip'},
                'name': 'OPatch Utility'
            }
        ]
    },
    '11.2.0.4': {
        'Patch - MOS': [
            {
                'name': '1.2.0.4.0 PATCH SET FOR ORACLE DATABASE SERVER - Patch 13390677 for Linux x86-64',
                'files': {
                    'p13390677_112040_Linux-x86-64_1of7.zip',
                    'p13390677_112040_Linux-x86-64_2of7.zip'
                }
            },
            {
                'name': '11.2.0.4.0 PATCH SET FOR ORACLE DATABASE SERVER - Patch 13390677 for Linux x86-64',
                'files': {'p13390677_112040_Linux-x86-64_3of7.zip'}
            },
            {
                'name': 'Combo of OJVM Component 11.2.0.4.201020 DB PSU + GI PSU 11.2.0.4.201020',
                'files': {'p31720783_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'Combo of OJVM Component 11.2.0.4.200714 DB PSU + GI PSU 11.2.0.4.200714',
                'files': {'p31326410_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'COMBO OF 11.2.0.4.200414 OJVM PSU GIPSU 11.2.0.4.200414',
                'files': {'p30783890_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'GRID INFRASTRUCTURE PATCH SET UPDATE 11.2.0.4.200114',
                'files': {'p30501155_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'GRID INFRASTRUCTURE PATCH SET UPDATE 11.2.0.4.191015',
                'files': {'p30070097_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'GRID INFRASTRUCTURE PATCH SET UPDATE 11.2.0.4.190716',
                'files': {'p29698727_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'GRID INFRASTRUCTURE PATCH SET UPDATE 11.2.0.4.190416',
                'files': {'p29255947_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'Combo OJVM PSU 11.2.0.4.190416 and Database PSU 11.2.0.4.190416 patch 29252186 for Linux x86-64',
                'files': {'p29252186_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'GI PSU 11.2.0.4.190416 patch 29255947 for Linux x86-64',
                'files': {'p29255947_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'RC SCRIPTS (/ETC/RC.D/RC.* , /ETC/INIT.D/* ) ON OL7 FOR CLUSTERWARE (Patch) patch 18370031 for Linux x86-64',
                'files': {'p18370031_112040_Linux-x86-64.zip'}
            },
            {
                'name': 'OPatch Utility',
                'files': {'p6880880_112000_Linux-x86-64.zip'}
            }
        ]
    }
}
