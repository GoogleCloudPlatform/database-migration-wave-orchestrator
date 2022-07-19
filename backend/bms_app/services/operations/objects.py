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

from dataclasses import dataclass

from bms_app.models import SourceDB


@dataclass
class DbMapping:
    """Wrapper to keep source dbs ans related mappings in one place.

    It should allow manipulate the same db/mappings data in different places.
    """
    db: SourceDB
    mappings: list  # list of Mapping objects
