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

import math
import re

import numpy as np
import pandas as pd


class MigvisorFileError(Exception):
    pass


class MigvisorFileFormatError(MigvisorFileError):
    pass


class MigvisorFileDataError(MigvisorFileError):
    pass


def convert_to_mb(size_bytes):
    size = int(size_bytes)
    i = int(math.floor(math.log(size, 1024)))
    p = math.pow(1024, i)
    s = round(size / p)
    return f'{s}M'


class MigvisorParser:
    """Migvisor output file parser."""

    COLUMNS_TO_PARSE = [
        'server', 'oracle_version', 'arch', 'cores', 'ram',
        'allocated_memory', 'db_name', 'db_size'
    ]
    COLUMNS_MAP = {
        'architecture': 'arch',
        'allocated memory': 'allocated_memory',
        'database name': 'db_name',
        'database size (gb)': 'db_size',
        'version': 'oracle_version'
    }
    DATABASE_SERVERS_SHEET = 'Database Servers'
    RAC_FEATURE = 'Real Application Clusters'
    DB_FULL_VERSION = 'DB Full Version'
    PSU_INSTALLED = 'PSU Installed'
    ASM_DISKGROUPS = 'ASM Diskgroups'
    DB_VERSIONS_MAP = {
        '19': '19.3.0.0.0',
        '18': '18.0.0.0.0',
        '12.2': '12.2.0.1.0',
        '12.1': '12.1.0.2.0',
        '11.2': '11.2.0.4.0'
    }

    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        """Return list of parsed databases."""
        wb = self._read_workbook()
        db_data = self._parse_databases_sheet(wb)
        self._validate_data(db_data)
        self._extend_db_data(wb, db_data)
        return db_data

    def _read_workbook(self):
        """Read excel file."""
        try:
            return pd.ExcelFile(self.file_path)
        except Exception as exc:
            raise MigvisorFileFormatError('Incorrect file format') from exc

    def _parse_databases_sheet(self, wb):
        """Parse data from "Database Servers" tab."""
        df = self._read_database_sheet_to_df(wb)
        return self._convert_db_df_to_data(df)

    def _extend_db_data(self, wb, db_data):
        """Add db specific parameters.

        Db parameters are defined in sheets which names start with "#" symbol.
        #-sheets order corresponds to db order in the Databases sheet.
        Read each #sheet and extract necessary data.
        """
        wb_sheet_names = [n for n in wb.sheet_names if n.startswith('#')]

        for ind, sheet_name in enumerate(wb_sheet_names):
            df = wb.parse(sheet_name)

            rac_nodes = self._get_rac_nodes(df)
            db_full_version = self._full_db_version(df, db_data[ind])
            oracle_release = self._add_oracle_release(df)
            asm_dg_data = self._parse_asm_diskgroup_data(df)

            db_data[ind].update({
                'rac_nodes': rac_nodes,
                'oracle_version': db_full_version,
                'oracle_release': oracle_release,
            })

            db_data[ind].update(asm_dg_data)

    def _parse_asm_diskgroup_data(self, df):
        """Parse oracle asm diskgroup data."""
        asm_columns = {
            'ALLOC_SIZE': 'au_size',
            'DG_NAME': 'diskgroup',
            'REDUNDANCY': 'redundancy',
        }
        misc_columns = {
            'COMPAT': 'compatible_asm',
            'DB_COMPAT': 'compatible_rdbms',
        }
        redundancy_names = {
            'EXTEND': 'EXTENDED',
            'EXTERN': 'EXTERNAL'
        }

        data = {
            'asm': []
        }

        asm_dg_df = df[df['Feature'] == self.ASM_DISKGROUPS]

        if not asm_dg_df.empty:
            for row in list(asm_dg_df.Value):
                asm_item = {}
                for key_value in row.split():
                    key, value = key_value.split(':')
                    key = key.strip()
                    value = value.strip()

                    if key in asm_columns:
                        if key == 'ALLOC_SIZE':
                            value = convert_to_mb(value)
                        elif key == 'REDUNDANCY':
                            value = redundancy_names.get(value, value)

                        asm_item[asm_columns[key]] = value

                    if key in misc_columns:
                        # later this data will go to asm too
                        data[misc_columns[key]] = value

                if asm_item:
                    data['asm'].append(asm_item)

        return data

    def _get_rac_nodes(self, df):
        """Add number of nodes in the RAC cluster."""
        return len(df[df['Feature'] == self.RAC_FEATURE])

    def _full_db_version(self, df, db_data_row):
        """Add full oracle version if exists."""
        db_full_version = df[df['Feature'] == self.DB_FULL_VERSION]
        if not db_full_version.empty:
            db_full_version = list(db_full_version.Value)[0]
        else:
            db_full_version = db_data_row['oracle_version']

        # convert to "base" version if it is not in full format.
        if db_full_version.count('.') < 4:
            db_full_version = self._db_version_format_conversion(
                db_full_version
            )

        return db_full_version

    def _db_version_format_conversion(self, db_version):
        """Convert db version to full format."""
        for short_ver, long_ver in self.DB_VERSIONS_MAP.items():
            if db_version.startswith(short_ver):
                return long_ver

        return db_version

    def _add_oracle_release(self, df):
        """Add oracle release if exists.
        Examples:
        1. the original value RDBMS_12.2.0.1.0_LINUX.X64_170125 should become 12.2.0.1.170125
        2. the original value RDBMS_19.11.0.0.0DBRU_LINUX.X64_210412 should become 19.11.0.0.210412

        Explanation:
        Trim the first 6 characters
        Take version number X.X.X.X. + last 6 digits
        """
        oracle_release = df[df['Feature'] == self.PSU_INSTALLED]
        if not oracle_release.empty:
            oracle_release = list(oracle_release.Value)[0]
            oracle_release = '{}.{}'.format(
                '.'.join(oracle_release[6:].split('.')[0:4]),
                oracle_release[-6:]
            )
        else:
            oracle_release = 'base'

        return oracle_release

    def _convert_db_df_to_data(self, df):
        """Convert dabatase df to dict data: rename/remove columns"""
        lower_columns = [x.lower() for x in df.columns]
        new_columns = {x: self.COLUMNS_MAP.get(y, y) for x, y in zip(df.columns, lower_columns)}
        df.rename(columns=new_columns, inplace=True)
        df = df.replace({np.nan: None})
        df = df[self.COLUMNS_TO_PARSE]
        # make sure 'oracle_version' is string
        df['oracle_version'] = df['oracle_version'].apply(
            lambda x: None if x is None else str(x)
        )

        return df.to_dict(orient='records')

    @classmethod
    def _read_database_sheet_to_df(cls, wb):
        """Read and validate 'Database Servers' sheet."""
        if cls.DATABASE_SERVERS_SHEET not in wb.sheet_names:
            raise MigvisorFileDataError(
                f'No {cls.DATABASE_SERVERS_SHEET} sheet found'
            )

        df = wb.parse(cls.DATABASE_SERVERS_SHEET, header=None)

        header_row_index = cls._find_header_row_index(df)

        if header_row_index is None:  # might be 0 which is OK
            raise MigvisorFileDataError('Headers row not found')

        # set correct headers
        df.columns = df.iloc[header_row_index]
        df.columns.name = None
        # drop empty rows before headers
        df = df[header_row_index + 1:]

        # drop completely empty rows if present
        df.dropna(how='all', inplace=True)

        if df.empty:
            raise MigvisorFileDataError('No database found')

        return df

    @staticmethod
    def _find_header_row_index(df):
        """Find index of the row with headers.

        It might be in different row depending on migvizor version.
        Look for the row that contains 'server' and 'database name' values.
        """
        header_row_index = None

        for index, row in df.iterrows():
            values = [x.lower() for x in row.values if isinstance(x, str)]

            if all((x in values for x in ('server', 'database name'))):
                header_row_index = index
                break

        return header_row_index

    def _validate_data(self, db_data):
        """Validate required fields and db name"""
        self._validate_required_fields(db_data)
        self._validate_db_name(db_data)

    def _validate_required_fields(self, db_data):
        """Check if ['server', 'db_name', 'oracle_version'] are parsed."""
        required_fields = ('server', 'db_name', 'oracle_version')

        for ind, item in enumerate(db_data):
            missed = [f for f in required_fields if item.get(f) is None]
            if missed:
                original_col_names = self._get_original_column_names(missed)
                raise MigvisorFileDataError(
                    f'Missed {original_col_names} field(s) in the row #{ind}'
                )

    @staticmethod
    def _validate_db_name(db_data):
        """Validate db name"""
        for item in db_data:
            if not item['db_name'][0].isalpha():
                raise MigvisorFileDataError(
                    'Db name should start with a letter'
                )

            if len(item['db_name']) > 8:
                raise MigvisorFileDataError(
                    'Db name should be less than 8 characters'
                )

            if not re.search(r'^[a-zA-Z0-9_$#]*$', item['db_name']):
                raise MigvisorFileDataError(
                    'Db name shoulf match the pattern: a-zA-Z0-9_$#'
                )

    def _get_original_column_names(self, cols):
        """Return original column names from the file."""
        reversed_col_map = {v: k for k, v in self.COLUMNS_MAP.items()}
        return [reversed_col_map.get(f, f).capitalize() for f in cols]
