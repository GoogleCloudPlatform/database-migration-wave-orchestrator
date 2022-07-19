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

import os
from unittest.mock import patch

from bms_app.services.rman import RmanLogFileError, RmanLogFileParser


def test_rman_parser_no_errors(client, files_dir):
    with open(os.path.join(files_dir, 'pre_restore_rman.log')) as fp:
        with patch('bms_app.services.rman.get_file_content',
                   return_value=fp.read()) as gcs_mock:
            parser = RmanLogFileParser(1)
            parser.validate()

            gcs_mock.assert_called_with(
                'test-bucket',
                'control_node_logs/bms_logs_1/rman_pre_restore.log'
            )


def test_rman_parser_errors(client, files_dir):
    with open(os.path.join(files_dir, 'pre_restore_rman_with_errors.log')) as fp:
        with patch('bms_app.services.rman.get_file_content',
                   return_value=fp.read()) as gcs_mock:
            parser = RmanLogFileParser(1)

            exc = None

            try:
                parser.validate()
            except RmanLogFileError as e:
                exc = e

            assert exc
            assert exc.errors == [
                'RMAN> crosscheck backup',
                'RMAN> list backup',
                'RMAN> restore database preview',
                'RMAN> report need backup',
                'RMAN> report unrecoverable',
                'RMAN> restore database validate',
                'RMAN> restore database validate check logical'
            ]

            gcs_mock.assert_called_with(
                'test-bucket',
                'control_node_logs/bms_logs_1/rman_pre_restore.log'
            )


def test_rman_parser_specific_command(client, files_dir):
    with open(os.path.join(files_dir, 'pre_restore_rman.log')) as fp:
        with patch('bms_app.services.rman.get_file_content',
                   return_value=fp.read()) as gcs_mock:
            parser = RmanLogFileParser(1)
            text = parser.get_cmd_output('RMAN> report unrecoverable')

            gcs_mock.assert_called_with(
                'test-bucket',
                'control_node_logs/bms_logs_1/rman_pre_restore.log'
            )

            assert text == (
                'report unrecoverable;\n'
                'Report of files that need backup due to unrecoverable operations\n'
                'File Type of Backup Required Name\n'
                '---- ----------------------- -----------------------------------'
            )
