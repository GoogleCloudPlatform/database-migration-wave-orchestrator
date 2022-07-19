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

from bms_app.upload.configs import ORACLE_FILE_NAMES_MAP


def get_software_library(binary_names):
    """Return list of files with oracle release and software names.

    According to https://google.github.io/bms-toolkit/user-guide.html#installing-the-toolkit
    "Required Oracle Software - Download Summary" table
    """
    items = []
    binary_names = set(binary_names)
    found_files = set()

    for release, release_data in ORACLE_FILE_NAMES_MAP.items():
        for category, category_data in release_data.items():
            for software_data in category_data:
                match_files = software_data['files'] & binary_names
                if match_files:
                    found_files.update(match_files)
                    items.append({
                        'oracle_release': release,
                        'software': software_data['name'],
                        'files': list(match_files)
                    })

    # include not mapped files
    for file_name in binary_names.difference(found_files):
        items.append({
            'oracle_release': '',
            'software': '',
            'files': [file_name]
        })

    return items
