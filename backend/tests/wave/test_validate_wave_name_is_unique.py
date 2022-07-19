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

import pytest
from marshmallow import ValidationError

from bms_app.wave.services import validate_wave_name_is_unique

from tests.factories import ProjectFactory, WaveFactory


def test_err(client):
    """Test err if the same name in the same project."""
    wave = WaveFactory()

    with pytest.raises(ValidationError):
        validate_wave_name_is_unique(
            wave.name,
            wave.project_id
        )


def test_no_err(client):
    """The same name can be in other project."""
    pr_1 = ProjectFactory()
    pr_2 = ProjectFactory()
    wave = WaveFactory(project=pr_1)

    validate_wave_name_is_unique(
        wave.name,
        pr_2.id
    )


def test_exclude(client):
    wave = WaveFactory()

    validate_wave_name_is_unique(
        wave.name,
        wave.project_id,
        wave.id
    )
